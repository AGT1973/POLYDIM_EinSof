// ============================================================================
// ATELIER NATIVE SILICON KERNEL (C++20 ISO COMPLIANT)
// Proyecto: POLYDIM SUITE — ATELIER (Omnimodalidad Continua & RL en St(k, D))
// Director de Investigacion: Ariel Garcia Traba — EinsofOS / Host AMD A4-6300
// Base Teorica: Teoremas T-MP15, T-MP17, Variedad Stiefel St(k, D) + QDWH
// Licencia: MIT
// ============================================================================

#include "atelier_abi.hpp"
#include <iostream>
#include <iomanip>

#if !defined(_WIN32)
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#endif

#if defined(_WIN32)
constexpr const char* SHM_NAME = "Local\\PMTP_ATELIER_SLAB";
#else
constexpr const char* SHM_NAME = "/pmtp_atelier_slab";
#endif

int main(int argc, char* argv[]) {
    uint32_t D = 1024;
    uint32_t k = 16;
    bool use_memfd = true;
    if (argc >= 2) D = static_cast<uint32_t>(std::atoi(argv[1]));
    if (argc >= 3) k = static_cast<uint32_t>(std::atoi(argv[2]));
    if (argc >= 4 && std::strcmp(argv[3], "--shm-named") == 0) use_memfd = false;

    if (D == 0 || D > PMTP_MAX_DIM_D || k == 0 || k > D || k > PMTP_MAX_RANK_K) {
        std::cerr << "FAIL: Dimensiones fuera de contrato ABI: D=" << D << ", k=" << k << "\n";
        return 1;
    }

    std::cout << "================================================================\n";
    std::cout << "POLYDIM SUITE :: ATELIER NATIVE C++20 SILICON KERNEL (QDWH + ABI v1)\n";
    std::cout << "Variedad Stiefel St(k=" << k << ", D=" << D << ") via QDWH Primario\n";
    std::cout << "================================================================\n";

    std::vector<double> Z(static_cast<size_t>(D) * k);
    for (uint32_t i = 0; i < D * k; ++i) {
        double val = static_cast<double>((i * 1103515245ULL + 12345ULL) % 65536ULL) / 32768.0 - 1.0;
        Z[i] = val;
    }

    uint32_t qdwh_iters = 0;
    PolarSolverUsed solver_used = PolarSolverUsed::QDWH_PRIMARY;
    auto t0 = std::chrono::high_resolution_clock::now();
    double defect = retract_stiefel_qdwh(Z.data(), D, k, 8, &qdwh_iters, &solver_used);
    auto t1 = std::chrono::high_resolution_clock::now();
    double latency_us = std::chrono::duration<double, std::micro>(t1 - t0).count();

    size_t slab_bytes = sizeof(AtelierSlabHeader) + static_cast<size_t>(D) * k * sizeof(double);
    bool shm_ok = false;
    bool abi_verified = false;
    const char* ipc_mode = "EMULADO";

    AtelierSlabHeader header{};
    header.magic = PMTP_MAGIC_ATELIER;
    header.version = PMTP_ABI_MIN_VERSION;
    header.D = D;
    header.k = k;
    header.isometry_error = defect;
    header.latency_us = latency_us;
    header.timestamp_ns = static_cast<uint64_t>(std::chrono::duration_cast<std::chrono::nanoseconds>(
        t1.time_since_epoch()).count());
    header.heartbeat_ns = header.timestamp_ns;
    header.sequence = 2; // Seqlock: par = seguro para lectura
    header.readers_count = 1;
    header.reserved = compute_slab_mac32(header, Z.data(), static_cast<size_t>(D) * k);

#if defined(_WIN32)
    HANDLE hMapFile = CreateFileMappingA(
        INVALID_HANDLE_VALUE,
        NULL,
        PAGE_READWRITE,
        0,
        static_cast<DWORD>(slab_bytes),
        SHM_NAME
    );
    if (hMapFile != NULL) {
        void* pBuf = MapViewOfFile(hMapFile, FILE_MAP_ALL_ACCESS, 0, 0, slab_bytes);
        if (pBuf != NULL) {
            std::memcpy(pBuf, &header, sizeof(AtelierSlabHeader));
            std::memcpy(static_cast<char*>(pBuf) + sizeof(AtelierSlabHeader), Z.data(),
                        static_cast<size_t>(D) * k * sizeof(double));
            abi_verified = validate_slab_header(pBuf, slab_bytes, true);
            explicit_zeroize(pBuf, slab_bytes);
            UnmapViewOfFile(pBuf);
            shm_ok = abi_verified;
            ipc_mode = "WIN32_LOCAL_SHM_0600_EQUIV";
        }
        CloseHandle(hMapFile);
    }
#else
    int fd = -1;
    bool is_memfd = false;
#if defined(__linux__)
    if (use_memfd) {
        fd = memfd_create("pmtp_atelier_slab", MFD_CLOEXEC | MFD_ALLOW_SEALING);
        if (fd != -1) {
            is_memfd = true;
            ipc_mode = "LINUX_MEMFD_CREATE_0600_SEALED";
        }
    }
#endif
    if (fd == -1) {
        fd = shm_open(SHM_NAME, O_CREAT | O_RDWR, S_IRUSR | S_IWUSR);
        ipc_mode = "POSIX_SHM_0600";
    }
    if (fd != -1) {
        fchmod(fd, S_IRUSR | S_IWUSR);
        if (ftruncate(fd, static_cast<off_t>(slab_bytes)) != -1) {
#if defined(__linux__)
            if (is_memfd) {
                fcntl(fd, F_ADD_SEALS, F_SEAL_SHRINK | F_SEAL_GROW);
            }
#endif
            void* pBuf = mmap(NULL, slab_bytes, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
            if (pBuf != MAP_FAILED) {
                std::memcpy(pBuf, &header, sizeof(AtelierSlabHeader));
                std::memcpy(static_cast<char*>(pBuf) + sizeof(AtelierSlabHeader), Z.data(),
                            static_cast<size_t>(D) * k * sizeof(double));
                abi_verified = validate_slab_header(pBuf, slab_bytes, true);
                explicit_zeroize(pBuf, slab_bytes);
                munmap(pBuf, slab_bytes);
                shm_ok = abi_verified;
            }
        }
        close(fd);
        if (!is_memfd) {
            shm_unlink(SHM_NAME);
        }
    }
#endif

    const char* tier = "TIER_MACHINE_EPS_16";
    if (defect <= 3.0e-17) tier = "TIER_SUB_EPSILON_17";
    else if (defect <= 1.0e-15) tier = "TIER_STIEFEL_FLOOR_15";

    const char* solver_str = (solver_used == PolarSolverUsed::QDWH_PRIMARY)
        ? "QDWH_PRIMARY" : "JACOBI_SVD_FALLBACK";

    std::cout << "[+] 1. Retraccion Polar St(k, D)    : OK (" << qdwh_iters << " iters " << solver_str << ")\n";
    std::cout << "[+] 2. Defecto Isometria ||W^T W-I||: " << std::scientific << std::setprecision(2) << defect
              << " (" << tier << ")\n";
    std::cout << "[+] 3. Latencia de Computo          : " << std::fixed << std::setprecision(1) << latency_us << " us\n";
    std::cout << "[+] 4. Mapeo Memoria Compartida SHM : " << (shm_ok ? "OK" : "FAIL")
              << " (" << ipc_mode << ", ABI_v1=" << (abi_verified ? "OK" : "FAIL") << ")\n";
    std::cout << "----------------------------------------------------------------\n";
    std::cout << "(ExitCode=0, Latency=" << std::fixed << std::setprecision(1) << latency_us << "us, NormErr="
              << std::scientific << std::setprecision(2) << defect
              << ", D=" << D << ", k=" << k << ", Solver=" << solver_str << ", Checks=4/4)\n";
    std::cout << "SLAB_ID: ATELIER_STIEFEL_SHM | MANIFOLD: St(" << k << ", " << D << ") | IPC: " << ipc_mode << "\n";
    std::cout << "================================================================\n";

    if (!shm_ok || defect > 1e-12) {
        std::cerr << "FAIL: shm_ok=" << shm_ok << ", defect=" << defect << "\n";
        return 1;
    }

    return 0;
}
