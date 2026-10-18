#pragma once
#include <cstdint>
#include <cstddef>
#include <type_traits>

/**
 * ==============================================================================
 * POLYDIM EINSOF PMTP-v4 CANONICAL WIRE DESCRIPTOR (128 BYTES)
 * ==============================================================================
 * SQUAD A & B UNIFIED SILICON CONTRACT:
 * 1. BARRERA A: Multi-Node Ring Buffer, Node-ID, Monotonic Global Epoch & Leases.
 * 2. BARRERA B: 64-byte cudaIpcMemHandle_t payload for host-bypass zero-copy VRAM.
 * 3. BARRERA C: Bitwise immutability verification, strict 64-byte alignment, 0 padding gaps.
 * ==============================================================================
 */

namespace polydim::v4 {

enum class MemoryDomain : uint32_t {
    HOST_DRAM_SHM    = 0, // Memoria compartida host (Windows NT Paged/NonPaged / POSIX shm)
    CUDA_VRAM_IPC    = 1, // Memoria VRAM nativa CUDA (acceso directo P2P / IPC handle)
    ROCM_VRAM_IPC    = 2, // Memoria VRAM nativa AMD ROCm HIP IPC
    DISTRIBUTED_RDMA = 3  // Memoria remota direccionable por RDMA / RoCE / Virtual Socket
};

enum class EpochState : uint32_t {
    ACTIVE_WRITING  = 0, // Productor reclamando slot
    COMMITTED_READ  = 1, // Solo lectura verificada (PAGE_READONLY o GPU write-protect)
    RETIRED_EPOCH   = 2, // Pendiente de recolección de leases
    RECLAIMED       = 3  // Slot reciclado en el ring buffer
};

enum class RingFlags : uint16_t {
    NONE            = 0x0000,
    READ_ONLY_LEASE = 0x0001,
    VRAM_RESIDENT   = 0x0002,
    MULTI_NODE_SYNC = 0x0004,
    NEUMAIER_GUARD  = 0x0008
};

#pragma pack(push, 1)

// Subestructura para ruta y socket de nodo distribuido (cabe exactamente en los 64B de handle)
struct NodePipeEndpoint {
    uint32_t target_node_id;      // ID de nodo destino (0..MAX_NODES-1)
    uint32_t sequence_num;        // Número de secuencia monótona de mensaje
    uint64_t ring_offset;         // Offset dentro del slab mapeado
    char     pipe_tag[48];        // Identificador de canal Named Pipe / Socket URI
};
static_assert(sizeof(NodePipeEndpoint) == 64, "NodePipeEndpoint DEBE tener exactamente 64 bytes");

struct PmtpWireDescriptor128 {
    // --------------------------------------------------------------------------
    // HEADER & ROUTING (32 BYTES)
    // --------------------------------------------------------------------------
    uint32_t magic;              // 0x504D5450 ("PMTP")
    uint16_t version;            // 4 (PMTP-v4)
    uint16_t flags;              // Bitmask RingFlags
    uint64_t global_epoch;       // Época monótona del clúster / ring buffer
    uint32_t node_id;            // ID del nodo emisor en topología distribuida
    uint32_t process_id;         // PID del emisor en el host local
    uint32_t memory_domain;      // MemoryDomain (HOST_DRAM, CUDA_VRAM, etc.)
    uint32_t epoch_state;        // EpochState actual

    // --------------------------------------------------------------------------
    // TENSOR METADATA (32 BYTES)
    // --------------------------------------------------------------------------
    uint64_t total_elements;     // Número total de elementos D en S^{D-1}
    uint32_t dtype;              // Código numérico IEEE (0=Float64, 1=Float32, 2=BFloat16)
    uint32_t rank;               // Rango tensorial (1D..4D)
    uint64_t byte_length;        // Tamaño total de bytes (total_elements * sizeof(T))
    uint64_t alignment_padding;  // Padding de alineación a 64 bytes

    // --------------------------------------------------------------------------
    // HARDWARE MEMORY HANDLE (64 BYTES)
    // Para CUDA: almacena exactamente los 64 bytes de cudaIpcMemHandle_t
    // Para Host/Multi-Node: mapea NodePipeEndpoint
    // --------------------------------------------------------------------------
    union {
        uint8_t          raw_handle[64];
        NodePipeEndpoint pipe_endpoint;
    } memory_handle;
};
#pragma pack(pop)

static_assert(sizeof(PmtpWireDescriptor128) == 128, "PmtpWireDescriptor128 DEBE tener exactamente 128 bytes");
static_assert(offsetof(PmtpWireDescriptor128, memory_handle) == 64, "memory_handle DEBE iniciar en offset 64");
static_assert(offsetof(PmtpWireDescriptor128, total_elements) == 32, "total_elements DEBE iniciar en offset 32");

} // namespace polydim::v4
