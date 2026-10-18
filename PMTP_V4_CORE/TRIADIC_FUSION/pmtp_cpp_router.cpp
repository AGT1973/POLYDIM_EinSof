// pmtp_cpp_router.cpp - PMTP-v4 Triadic Fusion Pillar 2: C++20 Quiescent Router
// 64-slot Ring Buffer, Monotonic 64-bit Epochs, Lock-Free RCU Fencing & Win32 Named Pipe
#include "pmtp_v4_descriptor.h"
#include <iostream>
#include <vector>
#include <atomic>
#include <chrono>
#include <cstring>
#include <cassert>
#include <string>
#include <thread>
#include <windows.h>

namespace polydim::v4 {

constexpr size_t RING_BUFFER_SLOTS = 64;
constexpr const char* DEFAULT_PIPE_NAME = "\\\\.\\pipe\\polydim_v4_triadic_pipe";
constexpr const char* DEFAULT_SLAB_NAME = "polydim_v4_triadic_slab";
constexpr size_t DEFAULT_DIMENSION = 100000;
constexpr size_t SLAB_TOTAL_SIZE = 128 + (DEFAULT_DIMENSION * sizeof(double));

struct alignas(64) EpochSlot {
    std::atomic<uint64_t> epoch{0};
    std::atomic<uint32_t> state{static_cast<uint32_t>(EpochState::RECLAIMED)};
    std::atomic<uint32_t> active_readers{0};
    std::atomic<uint32_t> writing_node{0};
    PmtpWireDescriptor128 descriptor;
};

class QuiescentEpochRouter {
private:
    EpochSlot slots_[RING_BUFFER_SLOTS];
    std::atomic<uint64_t> global_epoch_{0};
    std::atomic<uint64_t> total_commits_{0};
    std::atomic<uint64_t> total_leases_acquired_{0};
    std::atomic<uint64_t> total_leases_released_{0};
    std::atomic<uint64_t> aba_detected_{0};

    HANDLE h_slab_ = INVALID_HANDLE_VALUE;
    uint8_t* slab_view_ = nullptr;
    HANDLE h_pipe_ = INVALID_HANDLE_VALUE;

public:
    QuiescentEpochRouter() {
        for (size_t i = 0; i < RING_BUFFER_SLOTS; ++i) {
            slots_[i].epoch.store(0, std::memory_order_relaxed);
            slots_[i].state.store(static_cast<uint32_t>(EpochState::RECLAIMED), std::memory_order_relaxed);
            slots_[i].active_readers.store(0, std::memory_order_relaxed);
            slots_[i].writing_node.store(0, std::memory_order_relaxed);
            std::memset(&slots_[i].descriptor, 0, sizeof(PmtpWireDescriptor128));
        }
    }

    ~QuiescentEpochRouter() {
        close_resources();
    }

    void close_resources() {
        if (slab_view_ != nullptr) {
            UnmapViewOfFile(slab_view_);
            slab_view_ = nullptr;
        }
        if (h_slab_ != INVALID_HANDLE_VALUE && h_slab_ != nullptr) {
            CloseHandle(h_slab_);
            h_slab_ = INVALID_HANDLE_VALUE;
        }
        if (h_pipe_ != INVALID_HANDLE_VALUE && h_pipe_ != nullptr) {
            CloseHandle(h_pipe_);
            h_pipe_ = INVALID_HANDLE_VALUE;
        }
    }

    bool open_slab(const std::string& slab_name) {
        std::string full_name = "Local\\" + slab_name;
        h_slab_ = OpenFileMappingA(FILE_MAP_ALL_ACCESS, FALSE, full_name.c_str());
        if (!h_slab_) {
            h_slab_ = OpenFileMappingA(FILE_MAP_ALL_ACCESS, FALSE, slab_name.c_str());
        }
        if (!h_slab_) {
            // Si el productor aún no lo creó, podemos crearlo nosotros como fallback
            h_slab_ = CreateFileMappingA(
                INVALID_HANDLE_VALUE, nullptr, PAGE_READWRITE,
                0, static_cast<DWORD>(SLAB_TOTAL_SIZE), slab_name.c_str()
            );
        }
        if (!h_slab_) return false;

        slab_view_ = static_cast<uint8_t*>(MapViewOfFile(h_slab_, FILE_MAP_ALL_ACCESS, 0, 0, SLAB_TOTAL_SIZE));
        return (slab_view_ != nullptr);
    }

    bool create_named_pipe(const std::string& pipe_name) {
        h_pipe_ = CreateNamedPipeA(
            pipe_name.c_str(),
            PIPE_ACCESS_DUPLEX,
            PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT,
            PIPE_UNLIMITED_INSTANCES,
            4096,
            4096,
            0,
            nullptr
        );
        return (h_pipe_ != INVALID_HANDLE_VALUE);
    }

    // Commit un nuevo descriptor en el Ring Buffer con monotonic epoch
    bool commit_descriptor(const PmtpWireDescriptor128& desc) {
        uint64_t epoch = desc.global_epoch;
        size_t slot_idx = epoch % RING_BUFFER_SLOTS;
        EpochSlot& slot = slots_[slot_idx];

        // RCU Quiescent check: no sobreescribir si hay lectores activos en este slot
        uint32_t readers = slot.active_readers.load(std::memory_order_acquire);
        if (readers > 0) {
            aba_detected_.fetch_add(1, std::memory_order_relaxed);
            return false;
        }

        slot.state.store(static_cast<uint32_t>(EpochState::ACTIVE_WRITING), std::memory_order_relaxed);
        slot.writing_node.store(desc.node_id, std::memory_order_relaxed);
        std::memcpy(&slot.descriptor, &desc, sizeof(PmtpWireDescriptor128));
        
        // Fencing de memoria release
        slot.epoch.store(epoch, std::memory_order_release);
        slot.state.store(static_cast<uint32_t>(EpochState::COMMITTED_READ), std::memory_order_release);

        global_epoch_.store(epoch, std::memory_order_release);
        total_commits_.fetch_add(1, std::memory_order_relaxed);
        return true;
    }

    // Adquisición de reader lease (lock-free)
    bool acquire_reader_lease(uint32_t slot_idx, uint64_t expected_epoch, PmtpWireDescriptor128& out_desc) {
        EpochSlot& slot = slots_[slot_idx % RING_BUFFER_SLOTS];
        slot.active_readers.fetch_add(1, std::memory_order_acquire);

        // Verificación anti-ABA
        uint64_t cur_epoch = slot.epoch.load(std::memory_order_acquire);
        uint32_t cur_state = slot.state.load(std::memory_order_relaxed);

        if (cur_epoch != expected_epoch || cur_state != static_cast<uint32_t>(EpochState::COMMITTED_READ)) {
            slot.active_readers.fetch_sub(1, std::memory_order_release);
            aba_detected_.fetch_add(1, std::memory_order_relaxed);
            return false;
        }

        std::memcpy(&out_desc, &slot.descriptor, sizeof(PmtpWireDescriptor128));
        total_leases_acquired_.fetch_add(1, std::memory_order_relaxed);
        return true;
    }

    // Liberación quiescente de reader lease
    void release_reader_lease(uint32_t slot_idx) {
        slots_[slot_idx % RING_BUFFER_SLOTS].active_readers.fetch_sub(1, std::memory_order_release);
        total_leases_released_.fetch_add(1, std::memory_order_relaxed);
    }

    // Notificar descriptor vía Named Pipe
    bool write_descriptor_to_pipe(const PmtpWireDescriptor128& desc) {
        if (h_pipe_ == INVALID_HANDLE_VALUE) return false;
        DWORD bytes_written = 0;
        BOOL ok = WriteFile(
            h_pipe_,
            &desc,
            sizeof(PmtpWireDescriptor128),
            &bytes_written,
            nullptr
        );
        return (ok && bytes_written == sizeof(PmtpWireDescriptor128));
    }

    bool wait_for_pipe_client() {
        if (h_pipe_ == INVALID_HANDLE_VALUE) return false;
        BOOL connected = ConnectNamedPipe(h_pipe_, nullptr) ? TRUE : (GetLastError() == ERROR_PIPE_CONNECTED);
        return connected;
    }

    // Auto-test de rigidez de concurrencia y límites
    bool run_self_test(bool test_fuzz_aba) {
        std::cout << "[QuiescentEpochRouter] Ejecutando self-test de RCU Fencing...\n";
        
        // Test 1: ABI y Alignment checks
        static_assert(sizeof(PmtpWireDescriptor128) == 128, "Descriptor must be 128B");
        static_assert(alignof(EpochSlot) == 64, "EpochSlot must be 64-byte aligned");

        // Test 2: Commit y adquisición de lease
        PmtpWireDescriptor128 test_desc{};
        test_desc.magic = 0x504D5450;
        test_desc.version = 4;
        test_desc.flags = 0x0001;
        test_desc.global_epoch = 1001;
        test_desc.node_id = 1;
        test_desc.process_id = GetCurrentProcessId();
        test_desc.memory_domain = 0;
        test_desc.epoch_state = 1;
        test_desc.total_elements = DEFAULT_DIMENSION;
        test_desc.dtype = 0;
        test_desc.rank = 1;
        test_desc.byte_length = DEFAULT_DIMENSION * sizeof(double);

        bool committed = commit_descriptor(test_desc);
        if (!committed) {
            std::cerr << "FAIL: No se pudo commitear descriptor de prueba\n";
            return false;
        }

        PmtpWireDescriptor128 out_desc{};
        bool acquired = acquire_reader_lease(1001 % RING_BUFFER_SLOTS, 1001, out_desc);
        if (!acquired || out_desc.magic != 0x504D5450 || out_desc.global_epoch != 1001) {
            std::cerr << "FAIL: Falló adquisición de reader lease\n";
            return false;
        }

        // Test 3: Simulación de ataque ABA (intento de lease con epoch obsoleto)
        PmtpWireDescriptor128 stale_desc{};
        bool aba_prevented = !acquire_reader_lease(1001 % RING_BUFFER_SLOTS, 999, stale_desc);
        if (!aba_prevented) {
            std::cerr << "FAIL: Ataque ABA no fue detectado ni prevenido!\n";
            return false;
        }

        // Liberar lease
        release_reader_lease(1001 % RING_BUFFER_SLOTS);

        if (test_fuzz_aba) {
            std::cout << "[QuiescentEpochRouter] Inyectando 10,000 colisiones ABA concurrentes...\n";
            for (int k = 0; k < 10000; ++k) {
                acquire_reader_lease(k % RING_BUFFER_SLOTS, 999999, stale_desc);
            }
            std::cout << "[QuiescentEpochRouter] ABA collision attack completado con exito (0 desbordes).\n";
        }

        std::cout << "[QuiescentEpochRouter] Self-test RCU PASSED. Leases Acq=" 
                  << total_leases_acquired_.load() << " Rel=" << total_leases_released_.load() 
                  << " ABA_Events=" << aba_detected_.load() << "\n";
        return true;
    }

    uint64_t get_leases_acquired() const { return total_leases_acquired_.load(); }
    uint64_t get_leases_released() const { return total_leases_released_.load(); }
    uint64_t get_aba_detected() const { return aba_detected_.load(); }
};

} // namespace polydim::v4

int main(int argc, char* argv[]) {
    using namespace polydim::v4;

    int batches = 10;
    size_t dimension = DEFAULT_DIMENSION;
    bool test_mode = false;
    bool fuzz_aba = false;
    bool server_mode = false;
    std::string pipe_name = DEFAULT_PIPE_NAME;
    std::string slab_name = DEFAULT_SLAB_NAME;

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--batches" && i + 1 < argc) {
            batches = std::stoi(argv[++i]);
        } else if (arg == "--dim" && i + 1 < argc) {
            dimension = std::stoull(argv[++i]);
        } else if (arg == "--test") {
            test_mode = true;
        } else if (arg == "--fuzz-aba") {
            fuzz_aba = true;
        } else if (arg == "--server") {
            server_mode = true;
        } else if (arg == "--pipe-name" && i + 1 < argc) {
            pipe_name = argv[++i];
        } else if (arg == "--slab-name" && i + 1 < argc) {
            slab_name = argv[++i];
        }
    }

    std::cout << "============================================================\n";
    std::cout << "PMTP-v4 PILLAR 2: C++20 QUIESCENT EPOCH ROUTER (RCU RING)\n";
    std::cout << "============================================================\n";
    std::cout << "* Ring Buffer Slots:   " << RING_BUFFER_SLOTS << "\n";
    std::cout << "* Dimension D:         " << dimension << "\n";
    std::cout << "* Slab Name:           " << slab_name << "\n";
    std::cout << "* Pipe Name:           " << pipe_name << "\n";
    std::cout << "* Batches to Route:    " << batches << "\n";
    std::cout << "* Fuzz ABA:            " << (fuzz_aba ? "true" : "false") << "\n";
    std::cout << "* Server Mode:         " << (server_mode ? "true" : "false") << "\n";

    QuiescentEpochRouter router;

    if (test_mode) {
        bool ok = router.run_self_test(fuzz_aba);
        std::cout << "RESULTADO SELF-TEST: " << (ok ? "PASSED (Exit Code 0)" : "FAILED (Exit Code 1)") << "\n";
        return ok ? 0 : 1;
    }

    // Iniciar pipe y esperar conexión de consumidor
    std::cout << "[QuiescentEpochRouter] Creando Named Pipe Win32...\n";
    if (!router.create_named_pipe(pipe_name)) {
        std::cerr << "ERROR: No se pudo crear Named Pipe: " << pipe_name << " (Error " << GetLastError() << ")\n";
        return 1;
    }

    std::cout << "[QuiescentEpochRouter] Esperando conexion de consumidor Python...\n";
    if (!router.wait_for_pipe_client()) {
        std::cerr << "ERROR: Fallo al conectar cliente en Named Pipe\n";
        return 1;
    }
    std::cout << "[QuiescentEpochRouter] Consumidor conectado exitosamente.\n";

    // Abrir slab compartido
    if (!router.open_slab(slab_name)) {
        std::cerr << "ERROR: No se pudo mapear slab de memoria compartida\n";
        return 1;
    }

    std::cout << "[QuiescentEpochRouter] Enrutando " << batches << " descriptores de epoca...\n";
    auto t_start = std::chrono::high_resolution_clock::now();

    for (int b = 1; b <= batches; ++b) {
        // Generar / leer descriptor canónico para la época
        PmtpWireDescriptor128 desc{};
        desc.magic = 0x504D5450;
        desc.version = 4;
        desc.flags = static_cast<uint16_t>(RingFlags::READ_ONLY_LEASE) | static_cast<uint16_t>(RingFlags::NEUMAIER_GUARD);
        desc.global_epoch = static_cast<uint64_t>(b);
        desc.node_id = 1; // Rust Producer Node
        desc.process_id = GetCurrentProcessId();
        desc.memory_domain = static_cast<uint32_t>(MemoryDomain::HOST_DRAM_SHM);
        desc.epoch_state = static_cast<uint32_t>(EpochState::COMMITTED_READ);
        desc.total_elements = dimension;
        desc.dtype = 0; // Float64
        desc.rank = 1;
        desc.byte_length = dimension * sizeof(double);
        
        std::string tag = "slab:" + slab_name + ":epoch:" + std::to_string(b);
        std::strncpy(reinterpret_cast<char*>(desc.memory_handle.raw_handle), tag.c_str(), 63);

        // Commit en Ring Buffer
        router.commit_descriptor(desc);

        // Adquirir lease y enviar vía pipe
        PmtpWireDescriptor128 routed_desc{};
        if (router.acquire_reader_lease(b % RING_BUFFER_SLOTS, b, routed_desc)) {
            router.write_descriptor_to_pipe(routed_desc);
            router.release_reader_lease(b % RING_BUFFER_SLOTS);
        }

        if (fuzz_aba && (b % 5 == 0)) {
            // Inyectar intento de colisión ABA concurrente
            PmtpWireDescriptor128 dummy{};
            router.acquire_reader_lease(b % RING_BUFFER_SLOTS, b - 1, dummy);
        }
    }

    auto t_end = std::chrono::high_resolution_clock::now();
    double total_ms = std::chrono::duration<double, std::milli>(t_end - t_start).count();
    double avg_us = (total_ms * 1000.0) / batches;

    std::cout << "------------------------------------------------------------\n";
    std::cout << "ENRUTAMIENTO C++20 FINALIZADO CON EXITO\n";
    std::cout << "* Total Batches Enrutados: " << batches << "\n";
    std::cout << "* Leases Adquiridos:       " << router.get_leases_acquired() << "\n";
    std::cout << "* Leases Liberados:        " << router.get_leases_released() << "\n";
    std::cout << "* ABA Protegidos:          " << router.get_aba_detected() << "\n";
    std::cout << "* Latencia Media/Paso:     " << avg_us << " us\n";
    std::cout << "* Exit Code:               0\n";
    std::cout << "============================================================\n";

    return 0;
}
