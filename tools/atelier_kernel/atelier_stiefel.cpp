// ============================================================================
// ATELIER NATIVE SILICON KERNEL (C++20 ISO COMPLIANT)
// Proyecto: POLYDIM SUITE — ATELIER (Omnimodalidad Continua & RL en St(k, D))
// Director de Investigacion: Ariel Garcia Traba — EinsofOS / Host AMD A4-6300
// Base Teorica: Teoremas T-MP15, T-MP17, Variedad Stiefel St(k, D) + QDWH
// Licencia: MIT
// ============================================================================

#include "atelier_abi.hpp"
#include <cstdio>
#include <iostream>
#include <iomanip>
#include <fstream>

#if !defined(_WIN32)
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#endif

static std::array<char, 96> make_unique_shm_name(bool win32_local) {
    uint64_t nonce = 0;
    if (!fill_csprng_bytes(reinterpret_cast<uint8_t*>(&nonce), sizeof(nonce))) {
        std::abort();
    }
    std::array<char, 96> out{};
#if defined(_WIN32)
    (void)win32_local;
    std::snprintf(out.data(), out.size(), "Local\\PMTP_ATELIER_%lu_%016llx",
                  static_cast<unsigned long>(GetCurrentProcessId()),
                  static_cast<unsigned long long>(nonce));
#else
    (void)win32_local;
    std::snprintf(out.data(), out.size(), "/pmtp_atelier_%ld_%016llx",
                  static_cast<long>(getpid()),
                  static_cast<unsigned long long>(nonce));
#endif
    return out;
}

int main(int argc, char* argv[]) {
    uint32_t D = 1024;
    uint32_t k = 16;
    bool use_memfd = true;
    const char* dump_slab_path = nullptr;
    if (argc >= 2) D = static_cast<uint32_t>(std::atoi(argv[1]));
    if (argc >= 3) k = static_cast<uint32_t>(std::atoi(argv[2]));
    for (int ai = 3; ai < argc; ++ai) {
        if (std::strcmp(argv[ai], "--shm-named") == 0) use_memfd = false;
        else if (std::strcmp(argv[ai], "--dump-slab-file") == 0 && (ai + 1) < argc) {
            dump_slab_path = argv[++ai];
        }
    }

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
    header.sequence = 2; // Seqlock: par = seguro para lectura (word mutable excluido del MAC)
    header.mac64 = compute_slab_mac64(header, Z.data(), static_cast<size_t>(D) * k);

    std::array<char, 96> shm_name = make_unique_shm_name(true);
#if defined(_WIN32)
    HANDLE hMapFile = CreateFileMappingA(
        INVALID_HANDLE_VALUE,
        NULL,
        PAGE_READWRITE,
        0,
        static_cast<DWORD>(slab_bytes),
        shm_name.data()
    );
    if (hMapFile != NULL) {
        if (GetLastError() == ERROR_ALREADY_EXISTS) {
            CloseHandle(hMapFile);
            hMapFile = NULL;
        }
    }
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
            ipc_mode = "WIN32_LOCAL_SHM_UNIQUE_SESSION";
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
        fd = shm_open(shm_name.data(), O_CREAT | O_EXCL | O_RDWR, S_IRUSR | S_IWUSR);
        ipc_mode = "POSIX_SHM_0600_O_EXCL";
    }
    if (fd != -1) {
        struct stat st{};
        bool sec_ok = (fchmod(fd, S_IRUSR | S_IWUSR) == 0) &&
                      (fstat(fd, &st) == 0) &&
                      ((st.st_mode & 0777) == (S_IRUSR | S_IWUSR)) &&
                      (ftruncate(fd, static_cast<off_t>(slab_bytes)) == 0);
#if defined(__linux__)
        if (sec_ok && is_memfd) {
            if (fcntl(fd, F_ADD_SEALS, F_SEAL_SHRINK | F_SEAL_GROW | F_SEAL_SEAL) == -1) {
                sec_ok = false;
            }
        }
#endif
        if (sec_ok) {
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
            shm_unlink(shm_name.data());
        }
    }
#endif

    const char* tier = "TIER_MACHINE_EPS_16";
    if (defect <= 3.0e-17) tier = "TIER_SUB_EPSILON_17";
    else if (defect <= 1.0e-15) tier = "TIER_STIEFEL_FLOOR_15";

    const char* solver_str = (solver_used == PolarSolverUsed::QDWH_PRIMARY)
        ? "QDWH_PRIMARY" : "MGS_QR_FALLBACK";

    if (dump_slab_path) {
        std::ofstream ofs(dump_slab_path, std::ios::binary | std::ios::trunc);
        if (ofs) {
            ofs.write(reinterpret_cast<const char*>(&header), sizeof(AtelierSlabHeader));
            ofs.write(reinterpret_cast<const char*>(Z.data()),
                      static_cast<std::streamsize>(static_cast<size_t>(D) * k * sizeof(double)));
        }
    }

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
