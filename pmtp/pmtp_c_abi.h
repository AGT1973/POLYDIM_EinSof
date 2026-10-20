#ifndef PMTP_C_ABI_H
#define PMTP_C_ABI_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define PMTP_MAGIC_NUMBER       0x504D5450U  // "PMTP"
#define PMTP_VERSION_V1         0x0001U
#define PMTP_ALIGNMENT_BYTES    64U

#define PMTP_DESTROYING_BIT     (1ULL << 63)
#define PMTP_READERS_MASK       (~PMTP_DESTROYING_BIT)
#define PMTP_SLOT0_READERS_MASK 0x00000000FFFFFFFFULL
#define PMTP_SLOT1_READERS_MASK 0x7FFFFFFF00000000ULL

typedef enum {
    PMTP_DTYPE_FP32  = 0,
    PMTP_DTYPE_FP64  = 1,
    PMTP_DTYPE_FP16  = 2,
    PMTP_DTYPE_BF16  = 3,
    PMTP_DTYPE_INT32 = 4,
    PMTP_DTYPE_INT64 = 5
} pmtp_dtype_t;

typedef enum {
    PMTP_STATE_IDLE      = 0,
    PMTP_STATE_WRITING   = 1,
    PMTP_STATE_COMMITTED = 2,
    PMTP_STATE_READING   = 3
} pmtp_state_t;

#pragma pack(push, 1)

// ============================================================================
// 1. CABECERA COMPACTA PMTP (64 BYTES EXACTOS - CACHE LINE ALIGNED)
// ============================================================================
typedef struct {
    uint32_t magic;              // Offset  0 (4B): 0x504D5450 ("PMTP")
    uint16_t version;            // Offset  4 (2B): 0x0001
    uint16_t dtype_id;           // Offset  6 (2B): pmtp_dtype_t
    uint32_t active_slot;        // Offset  8 (4B): 0 o 1
    uint32_t slab_id;            // Offset 12 (4B): Identificador único de slab
    uint64_t num_elements;       // Offset 16 (8B): Escalares por slot
    uint64_t timestamp_ns;       // Offset 24 (8B): Época POSIX en nanosegundos
    double   scale;              // Offset 32 (8B): Factor de escala global IEEE-754
    uint32_t generation;         // Offset 40 (4B): Contador monotónico
    uint8_t  retired_slot0;      // Offset 44 (1B): Bandera de retiro slot 0
    uint8_t  retired_slot1;      // Offset 45 (1B): Bandera de retiro slot 1
    uint16_t reserved_flags;     // Offset 46 (2B): Flags
    uint64_t state_and_readers;  // Offset 48 (8B): Bit 63 = DESTROYING, Bits 32-62 = slot1, Bits 0-31 = slot0
    uint8_t  reserved_pad[8];    // Offset 56 (8B): Relleno a 64 bytes
} pmtp_header_compact_t;

// ============================================================================
// 2. CABECERA WIRE UNIFICADA DART-FFI / C-ABI / RUST (128 BYTES EXACTOS)
// Paridad estricta bit a bit entre C++, Rust y Dart FFI
// ============================================================================
typedef struct {
    uint32_t magic;               // Offset  0 (4B): 0x504D5450 ("PMTP")
    uint16_t version_major;       // Offset  4 (2B): 1
    uint16_t version_minor;       // Offset  6 (2B): 0
    uint8_t  slab_uuid[16];       // Offset  8 (16B): UUID o identificador de 128 bits
    uint64_t num_elements;        // Offset 24 (8B): Cantidad de elementos
    uint64_t payload_bytes;       // Offset 32 (8B): Tamaño del payload en bytes
    uint64_t timestamp_ns;        // Offset 40 (8B): Marca temporal en nanosegundos
    uint32_t dtype;               // Offset 48 (4B): Código de tipo de dato
    double   stiefel_defect;      // Offset 52 (8B): Defecto ortonormal ||W^T W - I||
    uint8_t  blake2s_hash[32];    // Offset 60 (32B): Firma criptográfica del payload
    uint8_t  reserved[36];        // Offset 92 (36B): Relleno a 128 bytes
} PolydimWireHeader;

#pragma pack(pop)

#ifdef __cplusplus
static_assert(sizeof(pmtp_header_compact_t) == 64, "pmtp_header_compact_t must be exactly 64 bytes");
static_assert(sizeof(PolydimWireHeader) == 128, "PolydimWireHeader must be exactly 128 bytes");
static_assert(offsetof(PolydimWireHeader, magic) == 0, "magic offset mismatch");
static_assert(offsetof(PolydimWireHeader, version_major) == 4, "version_major offset mismatch");
static_assert(offsetof(PolydimWireHeader, version_minor) == 6, "version_minor offset mismatch");
static_assert(offsetof(PolydimWireHeader, slab_uuid) == 8, "slab_uuid offset mismatch");
static_assert(offsetof(PolydimWireHeader, num_elements) == 24, "num_elements offset mismatch");
static_assert(offsetof(PolydimWireHeader, payload_bytes) == 32, "payload_bytes offset mismatch");
static_assert(offsetof(PolydimWireHeader, timestamp_ns) == 40, "timestamp_ns offset mismatch");
static_assert(offsetof(PolydimWireHeader, dtype) == 48, "dtype offset mismatch");
static_assert(offsetof(PolydimWireHeader, stiefel_defect) == 52, "stiefel_defect offset mismatch");
static_assert(offsetof(PolydimWireHeader, blake2s_hash) == 60, "blake2s_hash offset mismatch");
static_assert(offsetof(PolydimWireHeader, reserved) == 92, "reserved offset mismatch");
#endif

#ifdef _WIN32
  #ifdef BUILDING_PMTP_DLL
    #define PMTP_EXPORT __declspec(dllexport)
  #else
    #define PMTP_EXPORT __declspec(dllimport)
  #endif
#else
  #define PMTP_EXPORT __attribute__((visibility("default")))
#endif

// ============================================================================
// CONTEXTO NATIVO Y FIRMAS EXPORTADAS C-ABI
// ============================================================================
typedef struct pmtp_native_context_s pmtp_native_context_t;

PMTP_EXPORT pmtp_native_context_t* pmtp_shm_create(const char* name, uint32_t slab_id, uint64_t num_elements, uint16_t dtype_id);
PMTP_EXPORT pmtp_native_context_t* pmtp_shm_open(const char* name, uint32_t slab_id, uint64_t num_elements, uint16_t dtype_id);

PMTP_EXPORT int pmtp_shm_publish_atomic(pmtp_native_context_t* ctx, const void* data, uint64_t num_elements, double scale);
PMTP_EXPORT int pmtp_shm_acquire_lease(pmtp_native_context_t* ctx, uint32_t slot, uint64_t* out_generation);
PMTP_EXPORT int pmtp_shm_release_lease(pmtp_native_context_t* ctx, uint32_t slot);

PMTP_EXPORT int pmtp_shm_read_leased(pmtp_native_context_t* ctx, void* out_buffer, uint64_t buffer_capacity_bytes, uint32_t* out_slot, uint64_t* out_generation);
PMTP_EXPORT void pmtp_shm_close(pmtp_native_context_t* ctx);

#ifdef __cplusplus
}
#endif

#endif // PMTP_C_ABI_H
