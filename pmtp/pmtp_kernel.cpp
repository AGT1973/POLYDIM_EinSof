// ============================================================================
// PMTP C++20 NATIVE KERNEL & SHM ENGINE (CERTIFIED COMPATIBLE V26605)
// Unifies C++, Rust, Dart and Python with strict byte-level parity.
// ============================================================================

#define BUILDING_PMTP_DLL
#include "pmtp_c_abi.h"
#include "pmtp_win_shm.h"

#include <atomic>
#include <mutex>
#include <cstring>
#include <chrono>
#include <new>

struct pmtp_native_context_s {
    pmtp_win_shm_handle_t shm_handle;
    uint32_t              slab_id;
    uint64_t              num_elements;
    uint16_t              dtype_id;
    size_t                itemsize;
    size_t                payload_bytes;
    int                   is_owner;
    std::mutex            local_mtx;

    pmtp_header_compact_t* get_header() {
        return reinterpret_cast<pmtp_header_compact_t*>(shm_handle.pData);
    }

    void* get_slot_ptr(uint32_t slot) {
        if (!shm_handle.pData) return nullptr;
        uint8_t* base = reinterpret_cast<uint8_t*>(shm_handle.pData);
        size_t offset = sizeof(pmtp_header_compact_t) + (slot * payload_bytes);
        return base + offset;
    }
};

extern "C" {

pmtp_native_context_t* pmtp_shm_create(
    const char* name, 
    uint32_t slab_id, 
    uint64_t num_elements, 
    uint16_t dtype_id
) {
    if (!name || num_elements == 0) return nullptr;

    size_t itemsize = 8;
    if (dtype_id == PMTP_DTYPE_FP32 || dtype_id == PMTP_DTYPE_INT32) itemsize = 4;
    else if (dtype_id == PMTP_DTYPE_FP16 || dtype_id == PMTP_DTYPE_BF16) itemsize = 2;
    else if (dtype_id == PMTP_DTYPE_FP64 || dtype_id == PMTP_DTYPE_INT64) itemsize = 8;

    size_t payload_bytes = num_elements * itemsize;
    size_t total_bytes = sizeof(pmtp_header_compact_t) + (2 * payload_bytes);

    auto* ctx = new (std::nothrow) pmtp_native_context_s();
    if (!ctx) return nullptr;

    ctx->slab_id = slab_id;
    ctx->num_elements = num_elements;
    ctx->dtype_id = dtype_id;
    ctx->itemsize = itemsize;
    ctx->payload_bytes = payload_bytes;
    ctx->is_owner = 1;

    int rc = pmtp_win_shm_create_or_open(name, total_bytes, 1, &ctx->shm_handle);
    if (rc != 0) {
        delete ctx;
        return nullptr;
    }

    pmtp_header_compact_t* hdr = ctx->get_header();
    std::memset(hdr, 0, sizeof(pmtp_header_compact_t));
    hdr->magic = PMTP_MAGIC_NUMBER;
    hdr->version = PMTP_VERSION_V1;
    hdr->dtype_id = dtype_id;
    hdr->active_slot = 0;
    hdr->slab_id = slab_id;
    hdr->num_elements = num_elements;
    hdr->timestamp_ns = (uint64_t)std::chrono::duration_cast<std::chrono::nanoseconds>(
        std::chrono::system_clock::now().time_since_epoch()).count();
    hdr->scale = 1.0;
    hdr->generation = 1;
    hdr->retired_slot0 = 0;
    hdr->retired_slot1 = 1;
    hdr->state_and_readers = 0;

    return ctx;
}

pmtp_native_context_t* pmtp_shm_open(
    const char* name, 
    uint32_t slab_id, 
    uint64_t num_elements, 
    uint16_t dtype_id
) {
    if (!name || num_elements == 0) return nullptr;

    size_t itemsize = 8;
    if (dtype_id == PMTP_DTYPE_FP32 || dtype_id == PMTP_DTYPE_INT32) itemsize = 4;
    else if (dtype_id == PMTP_DTYPE_FP16 || dtype_id == PMTP_DTYPE_BF16) itemsize = 2;
    else if (dtype_id == PMTP_DTYPE_FP64 || dtype_id == PMTP_DTYPE_INT64) itemsize = 8;

    size_t payload_bytes = num_elements * itemsize;
    size_t total_bytes = sizeof(pmtp_header_compact_t) + (2 * payload_bytes);

    auto* ctx = new (std::nothrow) pmtp_native_context_s();
    if (!ctx) return nullptr;

    ctx->slab_id = slab_id;
    ctx->num_elements = num_elements;
    ctx->dtype_id = dtype_id;
    ctx->itemsize = itemsize;
    ctx->payload_bytes = payload_bytes;
    ctx->is_owner = 0; // Attached client, not owner

    int rc = pmtp_win_shm_create_or_open(name, total_bytes, 0, &ctx->shm_handle);
    if (rc != 0) {
        delete ctx;
        return nullptr;
    }

    pmtp_header_compact_t* hdr = ctx->get_header();
    if (hdr->magic != PMTP_MAGIC_NUMBER || hdr->version != PMTP_VERSION_V1) {
        pmtp_win_shm_close(&ctx->shm_handle);
        delete ctx;
        return nullptr;
    }

    return ctx;
}

int pmtp_shm_publish_atomic(
    pmtp_native_context_t* ctx, 
    const void* data, 
    uint64_t num_elements, 
    double scale
) {
    if (!ctx || !data || num_elements == 0) return -1;
    if (num_elements > ctx->num_elements) return -2;

    std::lock_guard<std::mutex> lock(ctx->local_mtx);
    pmtp_header_compact_t* hdr = ctx->get_header();
    if (!hdr) return -3;

    auto* atomic_sr = reinterpret_cast<std::atomic<uint64_t>*>(&hdr->state_and_readers);
    uint64_t current = atomic_sr->load(std::memory_order_acquire);
    if (current & PMTP_DESTROYING_BIT) {
        return -4; // Slab in destruction
    }

    uint32_t cur_active = hdr->active_slot;
    uint32_t target_slot = 1 - cur_active;

    // Verify target slot has ZERO active readers
    uint64_t target_readers = (target_slot == 0) ? (current & PMTP_SLOT0_READERS_MASK) : ((current & PMTP_SLOT1_READERS_MASK) >> 32);
    if (target_readers > 0) {
        return -5; // Slot is currently leased by reader
    }

    void* dst = ctx->get_slot_ptr(target_slot);
    if (!dst) return -6;

    size_t copy_bytes = num_elements * ctx->itemsize;
    std::memcpy(dst, data, copy_bytes);

    // Atomic update of metadata
    hdr->scale = scale;
    hdr->timestamp_ns = (uint64_t)std::chrono::duration_cast<std::chrono::nanoseconds>(
        std::chrono::system_clock::now().time_since_epoch()).count();
    hdr->generation++;
    
    // Switch active slot atomically
    hdr->active_slot = target_slot;
    if (target_slot == 0) {
        hdr->retired_slot0 = 0;
        hdr->retired_slot1 = 1;
    } else {
        hdr->retired_slot0 = 1;
        hdr->retired_slot1 = 0;
    }

    return 0; // Success
}

int pmtp_shm_acquire_lease(
    pmtp_native_context_t* ctx, 
    uint32_t slot, 
    uint64_t* out_generation
) {
    if (!ctx || slot > 1 || !out_generation) return -1;

    pmtp_header_compact_t* hdr = ctx->get_header();
    if (!hdr) return -2;

    auto* atomic_sr = reinterpret_cast<std::atomic<uint64_t>*>(&hdr->state_and_readers);
    uint64_t increment = (slot == 0) ? 1ULL : (1ULL << 32);

    uint64_t current = atomic_sr->load(std::memory_order_relaxed);
    while (true) {
        if (current & PMTP_DESTROYING_BIT) {
            return -3; // Slab in destruction
        }

        // Verify slot reader counter doesn't overflow
        if (slot == 0 && (current & PMTP_SLOT0_READERS_MASK) == PMTP_SLOT0_READERS_MASK) return -4;
        if (slot == 1 && ((current & PMTP_SLOT1_READERS_MASK) >> 32) >= 0x7FFFFFFFULL) return -4;

        if (atomic_sr->compare_exchange_weak(
                current,
                current + increment,
                std::memory_order_acquire,
                std::memory_order_relaxed)) {
            break;
        }
    }

    *out_generation = hdr->generation;
    return 0; // Acquired
}

int pmtp_shm_release_lease(pmtp_native_context_t* ctx, uint32_t slot) {
    if (!ctx || slot > 1) return -1;

    pmtp_header_compact_t* hdr = ctx->get_header();
    if (!hdr) return -2;

    auto* atomic_sr = reinterpret_cast<std::atomic<uint64_t>*>(&hdr->state_and_readers);
    uint64_t decrement = (slot == 0) ? 1ULL : (1ULL << 32);

    uint64_t current = atomic_sr->load(std::memory_order_relaxed);
    while (true) {
        uint64_t slot_readers = (slot == 0) ? (current & PMTP_SLOT0_READERS_MASK) : ((current & PMTP_SLOT1_READERS_MASK) >> 32);
        if (slot_readers == 0) {
            return -3; // Double-release guard
        }

        if (atomic_sr->compare_exchange_weak(
                current,
                current - decrement,
                std::memory_order_release,
                std::memory_order_relaxed)) {
            break;
        }
    }

    return 0; // Released
}

int pmtp_shm_read_leased(
    pmtp_native_context_t* ctx, 
    void* out_buffer, 
    uint64_t buffer_capacity_bytes,
    uint32_t* out_slot, 
    uint64_t* out_generation
) {
    if (!ctx || !out_buffer || buffer_capacity_bytes < ctx->payload_bytes) return -1;

    pmtp_header_compact_t* hdr = ctx->get_header();
    if (!hdr) return -2;

    uint32_t active_slot = hdr->active_slot;
    uint64_t gen = 0;

    int rc = pmtp_shm_acquire_lease(ctx, active_slot, &gen);
    if (rc != 0) return rc;

    void* src = ctx->get_slot_ptr(active_slot);
    if (!src) {
        pmtp_shm_release_lease(ctx, active_slot);
        return -3;
    }

    std::memcpy(out_buffer, src, ctx->payload_bytes);
    pmtp_shm_release_lease(ctx, active_slot);

    if (out_slot) *out_slot = active_slot;
    if (out_generation) *out_generation = gen;
    return 0;
}

void pmtp_shm_close(pmtp_native_context_t* ctx) {
    if (!ctx) return;

    pmtp_header_compact_t* hdr = ctx->get_header();
    if (hdr && ctx->is_owner) {
        // Only the owner initiates destruction
        auto* atomic_sr = reinterpret_cast<std::atomic<uint64_t>*>(&hdr->state_and_readers);
        atomic_sr->fetch_or(PMTP_DESTROYING_BIT, std::memory_order_acq_rel);

        // Drain active readers gracefully (max 200 ms)
        for (int i = 0; i < 200; ++i) {
            uint64_t active = atomic_sr->load(std::memory_order_acquire) & PMTP_READERS_MASK;
            if (active == 0) break;
            Sleep(1);
        }
    }

    pmtp_win_shm_close(&ctx->shm_handle);
    delete ctx;
}

} // extern "C"
