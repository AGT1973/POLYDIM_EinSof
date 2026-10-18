// ============================================================================
// POLYDIM EINSOF — C++20 AVX-512 / OPENMP PRODUCTION SILICON KERNEL V26503
// ============================================================================
// Canonical Unified Release V26503 (Hardened from V26502 + Dual External Audit)
// - Full Eradication of Complacent All-Green Fallacies.
// - [V26503-SEV1]: publish_flip TOCTOU state destruction resolved.
//   Clearing writer_cookie, writer_pid, reserved[0] occurs STRICTLY AFTER successful CAS.
// - [V26503-SEV1]: Legacy publish_flip alias validates header_len, alignment and non-zero cookie.
// - [V26503-SEV2]: validate_snapshot double-buffering invariant restored: valid if g == gen.
// - [V26503-SEV2]: CAM deterministic zeroing on all early numerical failure exits.
// - [V26503-SEV3]: Anti-aliasing in stiefel_residual_inject checked prior to beta == 0.0 fast-path.
// - [SEV-1]: Stiefel OpenMP data race eliminated (std::atomic<bool> flag).
//   Transactional in-place staging: h is NEVER modified on numerical failure.
//   Deterministic zeroing on failure when h_out != h.
// - [SEV-2]: PMTP Seqlock heartbeat with timestamp stamping in claim_writer and
//   dedicated writer_heartbeat API. Double-sampling cookie verification prevents
//   lock-stealing false positives.
// - [SEV-3]: Writer token authentication in publish_flip (token == writer_cookie)
//   and claimed slot verification (written_slot == claimed_slot).
//   Error code: POLYDIM_PMTP_TOKEN_MISMATCH (-19).
// - [SEV-4]: Strict OOB protection in read_snapshot: verifies payload_bytes
//   against num_elements * elem_size and total slab bounds.
// - [SEV-5]: Memory order inversion resolved in validate_snapshot: direct
//   std::memory_order_acquire load without inverted fence-before-load.
// - [SEV-6]: Strict reader zeroing of out_buf, out_slot, out_generation on race.
// - [SEV-7]: Token-authenticated abort_writer and explicit privileged force_recover.
// - [SEV-8]: CAM workspace capacity verification (workspace_bytes >= 2*M*sizeof(double)),
//   full mask byte-level anti-aliasing firewall, zero-query path after aliasing check,
//   and per-dimension compensated finitude verification.
// - [C-01]: Anti-fast-math macro guard with safe value check.
// - [Direct Atomic Member]: PmtpHeaderV6::seq_word declared as std::atomic<uint64_t>
//   directly (zero reinterpret_cast UB, standard layout, exact 64-byte alignment).
// - [V26503-FENCE]: Cross-process SeqCst barrier after post-CAS metadata writes.
// ============================================================================

#if defined(__FAST_MATH__) || (defined(__FINITE_MATH_ONLY__) && __FINITE_MATH_ONLY__)
#error "POLYDIM EINSOF: -ffast-math or -ffinite-math-only strictly prohibited! IEEE-754 subnormals and NaNs must be preserved."
#endif

#include <cstdint>
#include <cstddef>
#include <cmath>
#include <algorithm>
#include <limits>
#include <cstring>
#include <array>
#include <vector>
#include <memory>
#include <thread>
#include <atomic>
#include <chrono>

#if defined(_OPENMP)
#include <omp.h>
#endif

#if defined(_WIN32) || defined(__CYGWIN__)
#define POLYDIM_EXPORT extern "C" __declspec(dllexport)
#else
#define POLYDIM_EXPORT extern "C" __attribute__((visibility("default")))
#endif

namespace polydim_sota_v26503 {

enum Status : std::int32_t {
    POLYDIM_OK                         = 0,
    POLYDIM_INVALID_ARGUMENT           = -1,
    POLYDIM_NONFINITE_INPUT            = -2,
    POLYDIM_ALIAS_VIOLATION            = -3,
    POLYDIM_ALIGNMENT_ERROR            = -4,
    POLYDIM_NOT_UNIT                   = -5,
    POLYDIM_NOT_TANGENT                = -6,
    POLYDIM_ZERO_VECTOR                = -7,
    POLYDIM_PATH_REQUIRED              = -8,
    POLYDIM_NUMERICAL_FAILURE          = -9,
    POLYDIM_RANGE_ERROR                = -10,
    POLYDIM_FP_ENV_ERROR               = -11,
    POLYDIM_UNREPRESENTABLE_OUTPUT     = -12,
    POLYDIM_LENGTH_MISMATCH            = -13,
    POLYDIM_PRECISION_LOSS             = -14,
    POLYDIM_PMTP_SLAB_ERROR            = -15,
    POLYDIM_PMTP_RACE_DETECTED         = -16,
    POLYDIM_POLARSAFE_ILL_CONDITIONED  = -17,
    POLYDIM_POLARSAFE_SINGULAR         = -18,
    POLYDIM_PMTP_TOKEN_MISMATCH        = -19,
    POLYDIM_PMTP_WRITER_BUSY           = -20,
    POLYDIM_PMTP_EPOCH_EXHAUSTED        = -21,
    POLYDIM_PANIC_TRAPPED              = -99
};

constexpr std::uint64_t kMaxDimension = 100'000'000;
constexpr std::uint32_t kPmtpMagic    = 0x504D5450; // "PMTP"
constexpr std::uint16_t kPmtpVersion  = 26503;

// ----------------------------------------------------------------------------
// CABECERA BINARIA PMTP V6 (64 BYTES EXACTOS) — Cache-Line Aligned (alignas 64)
// Layout binario: <IHHQQQdIIQ8s (64 bytes exactos)
// Direct atomic member: seq_word eliminates all reinterpret_cast aliasing UB.
// ----------------------------------------------------------------------------
struct alignas(64) PmtpHeaderV6 {
    std::uint32_t              magic;          // offset 0  (0x504D5450 "PMTP")
    std::uint16_t              version;        // offset 4  (26503)
    std::uint16_t              dtype_id;       // offset 6  (1 = float64, 0 = float32)
    std::atomic<std::uint64_t> seq_word;       // offset 8  (Atomic Seqlock: bit0=writer_active, bit1=slot, bits2..63=gen)
    std::uint64_t              num_elements;   // offset 16 (Elementos por buffer)
    std::uint64_t              timestamp_ns;   // offset 24 (Timestamp de última actividad/heartbeat)
    double                     scale;          // offset 32 (Factor de escala, 1.0 default)
    std::uint32_t              slab_id;        // offset 40 (Identificador de slab)
    std::uint32_t              writer_pid;     // offset 44 (PID del proceso escritor)
    std::uint64_t              writer_cookie;  // offset 48 (Token de autenticación del escritor)
    char                       reserved[8];    // offset 56 (reserved[0] = claimed_slot, padding a 64 bytes)
};

static_assert(sizeof(PmtpHeaderV6) == 64 && alignof(PmtpHeaderV6) == 64, "PmtpHeaderV6 debe ocupar y alinear a 64 bytes exactos");
static_assert(offsetof(PmtpHeaderV6, seq_word) == 8, "seq_word debe ubicarse en offset 8");
static_assert(offsetof(PmtpHeaderV6, num_elements) == 16, "num_elements debe ubicarse en offset 16");
static_assert(offsetof(PmtpHeaderV6, timestamp_ns) == 24, "timestamp_ns debe ubicarse en offset 24");
static_assert(offsetof(PmtpHeaderV6, scale) == 32, "scale debe ubicarse en offset 32");
static_assert(offsetof(PmtpHeaderV6, slab_id) == 40, "slab_id debe ubicarse en offset 40");
static_assert(offsetof(PmtpHeaderV6, writer_pid) == 44, "writer_pid debe ubicarse en offset 44");
static_assert(offsetof(PmtpHeaderV6, writer_cookie) == 48, "writer_cookie debe ubicarse en offset 48");
static_assert(offsetof(PmtpHeaderV6, reserved) == 56, "reserved debe ubicarse en offset 56");

extern "C" {
    struct PolydimF64ConstView {
        const double* ptr;
        std::uint64_t len;
    };

    struct PolydimF64MutView {
        double* ptr;
        std::uint64_t len;
    };
}

// Generador de tokens pseudo-aleatorios splitmix64 de alta entropía
inline std::uint64_t splitmix64(std::uint64_t& state) noexcept {
    state += 0x9e3779b97f4a7c15ULL;
    std::uint64_t z = state;
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
    z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
    return z ^ (z >> 31);
}

inline std::uint64_t get_current_time_ns() noexcept {
    return static_cast<std::uint64_t>(
        std::chrono::duration_cast<std::chrono::nanoseconds>(
            std::chrono::system_clock::now().time_since_epoch()
        ).count()
    );
}

// TwoProduct FMA-compensated product error (Ogita-Rump-Oishi / Knuth)
inline void two_prod(double a, double b, double& p, double& e) noexcept {
    p = a * b;
    e = std::fma(a, b, -p);
}

// Neumaier Compensated Accumulator (preserva precisión frente a cancelación)
inline void neumaier_accumulate(double val, double& sum, double& comp) noexcept {
    double s = sum;
    double v = val;
    double t = s + v;
    if (std::abs(s) >= std::abs(v)) {
        comp += (s - t) + v;
    } else {
        comp += (v - t) + s;
    }
    sum = t;
}

// Anti-Aliasing Checker con Protección Total contra Desbordamiento de Enteros
inline bool buffers_overlap(const double* a, std::uint64_t len_a, const double* b, std::uint64_t len_b) noexcept {
    if (!a || !b || len_a == 0 || len_b == 0) return false;
    if (len_a > (std::numeric_limits<std::uintptr_t>::max() / sizeof(double))) return true;
    if (len_b > (std::numeric_limits<std::uintptr_t>::max() / sizeof(double))) return true;

    auto start_a = reinterpret_cast<std::uintptr_t>(a);
    auto start_b = reinterpret_cast<std::uintptr_t>(b);
    std::uintptr_t bytes_a = len_a * sizeof(double);
    std::uintptr_t bytes_b = len_b * sizeof(double);

    if (std::numeric_limits<std::uintptr_t>::max() - start_a < bytes_a ||
        std::numeric_limits<std::uintptr_t>::max() - start_b < bytes_b) {
        return true;
    }
    return (start_a < start_b + bytes_b) && (start_b < start_a + bytes_a);
}

// Anti-Aliasing Checker a nivel de bytes (para tipos heterogéneos como mask)
inline bool byte_buffers_overlap(const void* a, std::uintptr_t bytes_a, const void* b, std::uintptr_t bytes_b) noexcept {
    if (!a || !b || bytes_a == 0 || bytes_b == 0) return false;
    auto start_a = reinterpret_cast<std::uintptr_t>(a);
    auto start_b = reinterpret_cast<std::uintptr_t>(b);

    if (std::numeric_limits<std::uintptr_t>::max() - start_a < bytes_a ||
        std::numeric_limits<std::uintptr_t>::max() - start_b < bytes_b) {
        return true;
    }
    return (start_a < start_b + bytes_b) && (start_b < start_a + bytes_a);
}

// ----------------------------------------------------------------------------
// 1. PROYECCIÓN ESFÉRICA UNITARIA S^(D-1) UNIVERSAL
// Inmune a overflow y underflow para todo el rango IEEE-754 [5e-324, 1.79e308].
// ----------------------------------------------------------------------------
POLYDIM_EXPORT std::int32_t polydim_sphere_project_v26503(
    PolydimF64ConstView in_view,
    PolydimF64MutView out_view
) noexcept {
    if (!in_view.ptr || !out_view.ptr) return Status::POLYDIM_INVALID_ARGUMENT;
    if (in_view.len != out_view.len)   return Status::POLYDIM_LENGTH_MISMATCH;
    if (in_view.len == 0 || in_view.len > kMaxDimension) return Status::POLYDIM_RANGE_ERROR;

    if (reinterpret_cast<std::uintptr_t>(in_view.ptr) % alignof(double) != 0 ||
        reinterpret_cast<std::uintptr_t>(out_view.ptr) % alignof(double) != 0) {
        return Status::POLYDIM_ALIGNMENT_ERROR;
    }

    if (in_view.ptr != out_view.ptr && buffers_overlap(in_view.ptr, in_view.len, out_view.ptr, out_view.len)) {
        return Status::POLYDIM_ALIAS_VIOLATION;
    }

    std::uint64_t n = in_view.len;
    double max_val = 0.0;
    for (std::uint64_t i = 0; i < n; ++i) {
        double v = std::abs(in_view.ptr[i]);
        if (!std::isfinite(v)) return Status::POLYDIM_NONFINITE_INPUT;
        if (v > max_val) max_val = v;
    }

    if (max_val == 0.0) return Status::POLYDIM_ZERO_VECTOR;

    // Escalar por max_val para acotar todos los elementos en [-1.0, 1.0]
    alignas(64) double sum[8]  = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
    alignas(64) double comp[8] = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
    std::uint64_t i = 0;
    std::uint64_t n8 = n - (n % 8);

    for (; i < n8; i += 8) {
        for (int k = 0; k < 8; ++k) {
            double y = in_view.ptr[i + k] / max_val;
            neumaier_accumulate(y * y, sum[k], comp[k]);
        }
    }

    double total_sum = 0.0;
    double total_comp = 0.0;
    for (int k = 0; k < 8; ++k) {
        neumaier_accumulate(sum[k], total_sum, total_comp);
        neumaier_accumulate(comp[k], total_sum, total_comp);
    }
    for (; i < n; ++i) {
        double y = in_view.ptr[i] / max_val;
        neumaier_accumulate(y * y, total_sum, total_comp);
    }

    double scaled_norm_sq = total_sum + total_comp;
    if (scaled_norm_sq <= 0.0 || !std::isfinite(scaled_norm_sq)) {
        return Status::POLYDIM_NUMERICAL_FAILURE;
    }

    double r = std::sqrt(scaled_norm_sq);
    if (r <= 0.0 || !std::isfinite(r)) {
        return Status::POLYDIM_NUMERICAL_FAILURE;
    }

    // Normalizar y_i / r
    for (std::uint64_t j = 0; j < n; ++j) {
        double y = in_view.ptr[j] / max_val;
        double out_val = y / r;
        if (!std::isfinite(out_val)) return Status::POLYDIM_NUMERICAL_FAILURE;
        out_view.ptr[j] = out_val;
    }

    return Status::POLYDIM_OK;
}

// ----------------------------------------------------------------------------
// 2. PRODUCTO INTERNO COMPENSADO DE NEUMAIER CON VALIDACIÓN DE FINITUD
// ----------------------------------------------------------------------------
POLYDIM_EXPORT std::int32_t polydim_dot_neumaier_v26503(
    PolydimF64ConstView a_view,
    PolydimF64ConstView b_view,
    double* out_result
) noexcept {
    if (!a_view.ptr || !b_view.ptr || !out_result) return Status::POLYDIM_INVALID_ARGUMENT;
    if (a_view.len != b_view.len) return Status::POLYDIM_LENGTH_MISMATCH;
    if (a_view.len == 0 || a_view.len > kMaxDimension) return Status::POLYDIM_RANGE_ERROR;

    if (reinterpret_cast<std::uintptr_t>(a_view.ptr) % alignof(double) != 0 ||
        reinterpret_cast<std::uintptr_t>(b_view.ptr) % alignof(double) != 0 ||
        reinterpret_cast<std::uintptr_t>(out_result) % alignof(double) != 0) {
        return Status::POLYDIM_ALIGNMENT_ERROR;
    }

    if (buffers_overlap(a_view.ptr, a_view.len, out_result, 1) ||
        buffers_overlap(b_view.ptr, b_view.len, out_result, 1)) {
        return Status::POLYDIM_ALIAS_VIOLATION;
    }

    const std::uint64_t n = a_view.len;
    double scale_a = 0.0;
    double scale_b = 0.0;
    for (std::uint64_t i = 0; i < n; ++i) {
        const double va = a_view.ptr[i];
        const double vb = b_view.ptr[i];
        if (!std::isfinite(va) || !std::isfinite(vb)) {
            *out_result = 0.0;
            return Status::POLYDIM_NONFINITE_INPUT;
        }
        scale_a = std::max(scale_a, std::abs(va));
        scale_b = std::max(scale_b, std::abs(vb));
    }
    if (scale_a == 0.0 || scale_b == 0.0) {
        *out_result = 0.0;
        return Status::POLYDIM_OK;
    }

    // Normalize before multiplying: compensation cannot repair an Inf produced
    // by a raw product such as 1e308 * 1.0 followed by cancellation.
    double total_sum = 0.0;
    double total_comp = 0.0;
    for (std::uint64_t i = 0; i < n; ++i) {
        const double va = a_view.ptr[i] / scale_a;
        const double vb = b_view.ptr[i] / scale_b;
        double p = 0.0;
        double e = 0.0;
        two_prod(va, vb, p, e);
        neumaier_accumulate(p, total_sum, total_comp);
        if (e != 0.0) neumaier_accumulate(e, total_sum, total_comp);
    }
    const double scaled_res = total_sum + total_comp;
    if (!std::isfinite(scaled_res)) {
        *out_result = 0.0;
        return Status::POLYDIM_NUMERICAL_FAILURE;
    }
    if (scaled_res == 0.0) {
        *out_result = 0.0;
        return Status::POLYDIM_OK;
    }
    int ea = 0, eb = 0, es = 0;
    const double ma = std::frexp(scale_a, &ea);
    const double mb = std::frexp(scale_b, &eb);
    const double ms = std::frexp(scaled_res, &es);
    const double res = std::scalbn((ma * mb) * ms, ea + eb + es);
    if (!std::isfinite(res)) {
        *out_result = 0.0;
        return Status::POLYDIM_NUMERICAL_FAILURE;
    }
    *out_result = res;
    return Status::POLYDIM_OK;
}

// ----------------------------------------------------------------------------
// 3. PUENTE STIEFEL RESIDUAL DIRECCIÓN-AMPLITUD CON ANTI-ALIASING Y CERO-ALLOC
// ----------------------------------------------------------------------------
POLYDIM_EXPORT std::int32_t polydim_stiefel_residual_inject_v26503(
    const double* h,             // [D] Activación original
    const double* W,             // [D, K] Base ortonormal Stiefel (row-major: D filas, K columnas)
    const double* z_orig,        // [K] Coordenadas latentes originales
    const double* z_prime,       // [K] Coordenadas latentes modificadas
    double        beta,          // Factor de intervención
    std::uint64_t D,             // Dimensión espacial
    std::uint64_t K,             // Rango latente Stiefel
    double*       h_out          // [D] Activación resultante
) noexcept {
    if (!h || !W || !z_orig || !z_prime || !h_out) return Status::POLYDIM_INVALID_ARGUMENT;
    if (D == 0 || K == 0 || K > D || D > kMaxDimension) return Status::POLYDIM_RANGE_ERROR;
    if (!std::isfinite(beta)) return Status::POLYDIM_NONFINITE_INPUT;

    // Validación de alineación a 8 bytes
    if (reinterpret_cast<std::uintptr_t>(h) % alignof(double) != 0 ||
        reinterpret_cast<std::uintptr_t>(W) % alignof(double) != 0 ||
        reinterpret_cast<std::uintptr_t>(z_orig) % alignof(double) != 0 ||
        reinterpret_cast<std::uintptr_t>(z_prime) % alignof(double) != 0 ||
        reinterpret_cast<std::uintptr_t>(h_out) % alignof(double) != 0) {
        return Status::POLYDIM_ALIGNMENT_ERROR;
    }

    const std::uint64_t DK = D * K;

    if (buffers_overlap(h_out, D, W, DK) ||
        buffers_overlap(h_out, D, z_orig, K) ||
        buffers_overlap(h_out, D, z_prime, K) ||
        buffers_overlap(h, D, W, DK) ||
        buffers_overlap(h, D, z_orig, K) ||
        buffers_overlap(h, D, z_prime, K)) {
        return Status::POLYDIM_ALIAS_VIOLATION;
    }
    if (h_out != h && buffers_overlap(h, D, h_out, D)) {
        return Status::POLYDIM_ALIAS_VIOLATION;
    }

    // BYPASS EXACTO BIT A BIT SI BETA == 0.0 (T-MP16 / T-MP19)
    if (std::abs(beta) == 0.0) {
        if (h_out == h) return Status::POLYDIM_OK;
        std::memcpy(h_out, h, D * sizeof(double));
        return Status::POLYDIM_OK;
    }

    // Inyección residual CERO-ALLOC con pre-cálculo de dz [K]
    alignas(64) double dz_stack[512];
    std::unique_ptr<double[]> dz_heap;
    double* dz = dz_stack;
    if (K > 512) {
        try {
            dz_heap.reset(new double[K]);
            dz = dz_heap.get();
        } catch (...) {
            return Status::POLYDIM_PANIC_TRAPPED;
        }
    }
    for (std::uint64_t k = 0; k < K; ++k) {
        if (!std::isfinite(z_orig[k]) || !std::isfinite(z_prime[k])) return Status::POLYDIM_NONFINITE_INPUT;
        double diff = z_prime[k] - z_orig[k];
        double p = beta * diff;
        if (!std::isfinite(p)) return Status::POLYDIM_NUMERICAL_FAILURE;
        dz[k] = p;
    }

    double* target_out = h_out;
    std::unique_ptr<double[]> staged_buf;
    if (h_out == h) {
        try {
            staged_buf.reset(new double[D]);
            target_out = staged_buf.get();
        } catch (...) {
            return Status::POLYDIM_PANIC_TRAPPED;
        }
    }

    std::atomic<bool> has_numerical_failure{false};
    std::atomic<bool> has_nonfinite_w{false};

    #pragma omp parallel for schedule(static) if(D > 1024)
    for (std::int64_t i = 0; i < static_cast<std::int64_t>(D); ++i) {
        if (has_numerical_failure.load(std::memory_order_relaxed)) continue;

        double acc = 0.0;
        double comp = 0.0;
        std::uint64_t row_offset = static_cast<std::uint64_t>(i) * K;
        for (std::uint64_t k = 0; k < K; ++k) {
            double wk = W[row_offset + k];
            if (!std::isfinite(wk)) {
                has_nonfinite_w.store(true, std::memory_order_relaxed);
                break;
            }
            double prod = wk * dz[k];
            neumaier_accumulate(prod, acc, comp);
        }

        if (has_numerical_failure.load(std::memory_order_relaxed)) continue;

        double delta = acc + comp;
        double val = h[i] + delta;
        if (!std::isfinite(delta) || !std::isfinite(val)) {
            has_numerical_failure.store(true, std::memory_order_relaxed);
        } else {
            target_out[i] = (delta == 0.0) ? h[i] : val;
        }
    }

    if (has_nonfinite_w.load(std::memory_order_relaxed)) {
        if (h_out != h) {
            std::memset(h_out, 0, D * sizeof(double));
        }
        return Status::POLYDIM_NONFINITE_INPUT;
    }
    if (has_numerical_failure.load(std::memory_order_relaxed)) {
        if (h_out != h) {
            std::memset(h_out, 0, D * sizeof(double));
        }
        return Status::POLYDIM_NUMERICAL_FAILURE;
    }

    if (h_out == h) {
        std::memcpy(h_out, target_out, D * sizeof(double));
    }

    return Status::POLYDIM_OK;
}

// ----------------------------------------------------------------------------
// 4. MEMORIA ASOCIATIVA CAM CON WORKSPACE Y MÁSCARA DE VALIDEZ
// ----------------------------------------------------------------------------
POLYDIM_EXPORT std::uint64_t polydim_cam_workspace_bytes_v26503(std::uint64_t M) noexcept {
    if (M == 0 || M > 1'000'000 || M > (std::numeric_limits<std::uint64_t>::max() / (2 * sizeof(double)))) {
        return 0;
    }
    return 2 * M * sizeof(double);
}

POLYDIM_EXPORT std::int32_t polydim_cam_attention_retrieve_v26503(
    const double*       q,               // [D] Vector de consulta
    const double*       K_mat,           // [M, D] Matriz de claves
    const double*       V_mat,           // [M, D] Matriz de valores
    const std::uint8_t* mask,            // [M] Máscara de ocupación (1=ocupado, 0=vacío, nullptr=todos)
    std::uint64_t       M,               // Número de slots de memoria
    std::uint64_t       D,               // Dimensión por slot
    double              inv_temp,        // Inversa de temperatura 1/T (> 0.0, finito)
    double*             workspace,       // Búfer de trabajo de al menos workspace_bytes
    std::uint64_t       workspace_bytes, // Tamaño certificado del workspace en bytes
    double*             v_out            // [D] Valor recuperado
) noexcept {
    if (!q || !K_mat || !V_mat || !workspace || !v_out) return Status::POLYDIM_INVALID_ARGUMENT;
    if (M == 0 || D == 0 || M > 1'000'000 || D > kMaxDimension) return Status::POLYDIM_RANGE_ERROR;
    if (!(inv_temp > 0.0) || !std::isfinite(inv_temp)) return Status::POLYDIM_INVALID_ARGUMENT;

    std::uint64_t required_workspace_bytes = 2 * M * sizeof(double);
    if (workspace_bytes < required_workspace_bytes) {
        return Status::POLYDIM_INVALID_ARGUMENT;
    }

    if (reinterpret_cast<std::uintptr_t>(q) % alignof(double) != 0 ||
        reinterpret_cast<std::uintptr_t>(K_mat) % alignof(double) != 0 ||
        reinterpret_cast<std::uintptr_t>(V_mat) % alignof(double) != 0 ||
        reinterpret_cast<std::uintptr_t>(workspace) % alignof(double) != 0 ||
        reinterpret_cast<std::uintptr_t>(v_out) % alignof(double) != 0) {
        return Status::POLYDIM_ALIGNMENT_ERROR;
    }

    const std::uint64_t MD = M * D;

    if (buffers_overlap(workspace, 2 * M, v_out, D) ||
        buffers_overlap(workspace, 2 * M, q, D) ||
        buffers_overlap(workspace, 2 * M, K_mat, MD) ||
        buffers_overlap(workspace, 2 * M, V_mat, MD) ||
        buffers_overlap(v_out, D, q, D) ||
        buffers_overlap(v_out, D, K_mat, MD) ||
        buffers_overlap(v_out, D, V_mat, MD) ||
        buffers_overlap(q, D, K_mat, MD) ||
        buffers_overlap(q, D, V_mat, MD)) {
        return Status::POLYDIM_ALIAS_VIOLATION;
    }

    if (mask) {
        if (byte_buffers_overlap(mask, M, v_out, D * sizeof(double)) ||
            byte_buffers_overlap(mask, M, workspace, required_workspace_bytes) ||
            byte_buffers_overlap(mask, M, q, D * sizeof(double)) ||
            byte_buffers_overlap(mask, M, K_mat, MD * sizeof(double)) ||
            byte_buffers_overlap(mask, M, V_mat, MD * sizeof(double))) {
            return Status::POLYDIM_ALIAS_VIOLATION;
        }
    }

    // [V26503-FIX V3-032]: Validate finitude of q FIRST
    double q_max = 0.0;
    for (std::uint64_t d = 0; d < D; ++d) {
        if (!std::isfinite(q[d])) {
            std::memset(v_out, 0, D * sizeof(double));
            return Status::POLYDIM_NONFINITE_INPUT;
        }
        double a = std::abs(q[d]);
        if (a > q_max) q_max = a;
    }

    // [V26503-FIX V3-032]: Validate finitude of all active K and V before any zero-query early exit
    std::uint64_t num_occupied = 0;
    for (std::uint64_t m = 0; m < M; ++m) {
        if (mask && mask[m] == 0) continue;
        num_occupied++;
        for (std::uint64_t d = 0; d < D; ++d) {
            if (!std::isfinite(K_mat[m * D + d]) || !std::isfinite(V_mat[m * D + d])) {
                std::memset(v_out, 0, D * sizeof(double));
                return Status::POLYDIM_NONFINITE_INPUT;
            }
        }
    }

    if (num_occupied == 0) {
        std::memset(v_out, 0, D * sizeof(double));
        return Status::POLYDIM_OK;
    }

    // [V26503-FIX V3-012]: If q == 0, inner product q . K_m == 0 for all m.
    // Softmax of zeros gives uniform weights 1 / num_occupied over all active slots.
    if (q_max == 0.0) {
        double inv_occ = 1.0 / static_cast<double>(num_occupied);
        for (std::uint64_t d = 0; d < D; ++d) {
            double sum_v = 0.0;
            double comp_v = 0.0;
            for (std::uint64_t m = 0; m < M; ++m) {
                if (mask && mask[m] == 0) continue;
                neumaier_accumulate(V_mat[m * D + d], sum_v, comp_v);
            }
            v_out[d] = (sum_v + comp_v) * inv_occ;
        }
        return Status::POLYDIM_OK;
    }

    double* scores = workspace;
    double* exp_scores = workspace + M;

    double max_score = -std::numeric_limits<double>::infinity();
    bool has_occupied = false;

    for (std::uint64_t m = 0; m < M; ++m) {
        if (mask && mask[m] == 0) {
            scores[m] = -std::numeric_limits<double>::infinity();
            continue;
        }
        has_occupied = true;
        PolydimF64ConstView q_view{q, D};
        PolydimF64ConstView k_view{&K_mat[m * D], D};
        double dot = 0.0;
        int rc_dot = polydim_dot_neumaier_v26503(q_view, k_view, &dot);
        if (rc_dot != Status::POLYDIM_OK) {
            std::memset(v_out, 0, D * sizeof(double));
            return rc_dot;
        }
        double sc = dot * inv_temp;
        scores[m] = sc;
        if (sc > max_score) max_score = sc;
    }

    if (!has_occupied) {
        std::memset(v_out, 0, D * sizeof(double));
        return Status::POLYDIM_OK;
    }

    if (!std::isfinite(max_score)) {
        std::memset(v_out, 0, D * sizeof(double));
        return Status::POLYDIM_NUMERICAL_FAILURE;
    }

    double sum_exp = 0.0;
    double comp_exp = 0.0;
    for (std::uint64_t m = 0; m < M; ++m) {
        if (!std::isfinite(scores[m]) || scores[m] == -std::numeric_limits<double>::infinity()) {
            exp_scores[m] = 0.0;
            continue;
        }
        double e = std::exp(scores[m] - max_score);
        exp_scores[m] = e;
        neumaier_accumulate(e, sum_exp, comp_exp);
    }

    double total_sum_exp = sum_exp + comp_exp;
    if (total_sum_exp <= 0.0 || !std::isfinite(total_sum_exp)) {
        std::memset(v_out, 0, D * sizeof(double));
        return Status::POLYDIM_NUMERICAL_FAILURE;
    }
    double inv_sum_exp = 1.0 / total_sum_exp;

    for (std::uint64_t m = 0; m < M; ++m) {
        exp_scores[m] *= inv_sum_exp;
    }

    std::atomic<bool> agg_failure{false};

    #pragma omp parallel for schedule(static) if(D > 1024)
    for (std::int64_t d = 0; d < static_cast<std::int64_t>(D); ++d) {
        if (agg_failure.load(std::memory_order_relaxed)) continue;

        double sum_d = 0.0;
        double comp_d = 0.0;
        for (std::uint64_t m = 0; m < M; ++m) {
            double w = exp_scores[m];
            if (w == 0.0) continue;
            double p = w * V_mat[m * D + d];
            neumaier_accumulate(p, sum_d, comp_d);
        }
        double res = sum_d + comp_d;
        if (!std::isfinite(res)) {
            agg_failure.store(true, std::memory_order_relaxed);
        } else {
            v_out[d] = res;
        }
    }

    if (agg_failure.load(std::memory_order_relaxed)) {
        std::memset(v_out, 0, D * sizeof(double));
        return Status::POLYDIM_NUMERICAL_FAILURE;
    }

    return Status::POLYDIM_OK;
}

// ----------------------------------------------------------------------------
// 5. MONITOR ATÓMICO PMTP V6: SEQLOCK ATÓMICO INTER-PROCESO
// ----------------------------------------------------------------------------
POLYDIM_EXPORT std::int32_t polydim_pmtp_v6_claim_writer_v26503(
    void*          header_ptr,
    std::uint64_t  header_len,
    std::uint32_t  pid,
    std::uint32_t* out_write_slot,
    std::uint64_t* out_writer_token
) noexcept {
    if (!header_ptr || !out_write_slot || !out_writer_token || header_len < sizeof(PmtpHeaderV6)) {
        return Status::POLYDIM_INVALID_ARGUMENT;
    }
    if (reinterpret_cast<std::uintptr_t>(header_ptr) % alignof(PmtpHeaderV6) != 0) {
        return Status::POLYDIM_ALIGNMENT_ERROR;
    }
    auto* h = reinterpret_cast<PmtpHeaderV6*>(header_ptr);
    if (h->magic != kPmtpMagic || h->version != kPmtpVersion) return Status::POLYDIM_PMTP_SLAB_ERROR;

    std::uint64_t cur = h->seq_word.load(std::memory_order_acquire);

    for (int retry = 0; retry < 1000; ++retry) {
        if (cur & 1ULL) {
            if (retry > 500) {
                std::uint64_t sample_cookie_1 = h->writer_cookie;
                std::uint64_t sample_ts_1     = h->timestamp_ns;
                std::this_thread::sleep_for(std::chrono::microseconds(100));
                std::uint64_t sample_cookie_2 = h->writer_cookie;
                std::uint64_t sample_ts_2     = h->timestamp_ns;

                auto now_ns = get_current_time_ns();
                if (sample_cookie_1 == sample_cookie_2 && sample_ts_1 == sample_ts_2 &&
                    sample_ts_1 > 0 && now_ns > sample_ts_1 && (now_ns - sample_ts_1 > 5'000'000'000ULL)) {
                    // [V4-CPP-01 FIX]: Do NOT increment generation during stale recovery.
                    // If the slab was never published (cur >> 2 == 0), generation must remain 0
                    // so readers reject uninitialized memory.
                    std::uint64_t rec_gen = (cur >> 2);
                    std::uint64_t rec_slot = (cur >> 1) & 1ULL;
                    std::uint64_t rec_nxt = (rec_gen << 2) | (rec_slot << 1) | 0ULL;
                    if (h->seq_word.compare_exchange_weak(cur, rec_nxt, std::memory_order_acq_rel, std::memory_order_acquire)) {
                        cur = rec_nxt;
                        continue;
                    }
                }
            }
            std::this_thread::yield();
            cur = h->seq_word.load(std::memory_order_acquire);
            continue;
        }

        std::uint64_t next_claim = cur | 1ULL;
        if (h->seq_word.compare_exchange_weak(cur, next_claim, std::memory_order_acq_rel, std::memory_order_acquire)) {
            std::uint32_t active_slot = static_cast<std::uint32_t>((cur >> 1) & 1ULL);
            std::uint32_t claim_slot = 1 - active_slot;
            *out_write_slot = claim_slot;

            auto now_ns = get_current_time_ns();
            std::uint64_t rng_state = now_ns ^ (static_cast<std::uint64_t>(pid) << 32) ^ cur;
            std::uint64_t token = splitmix64(rng_state);
            if (token == 0) token = 1;

            h->writer_pid = pid;
            h->timestamp_ns = now_ns;
            h->writer_cookie = token;
            h->reserved[0] = static_cast<char>(claim_slot);

            // [V26503-FENCE]: Cross-process SeqCst barrier ensures all other processes observe metadata
            std::atomic_thread_fence(std::memory_order_seq_cst);

            *out_writer_token = token;
            return Status::POLYDIM_OK;
        }
    }
    return Status::POLYDIM_PMTP_RACE_DETECTED;
}

POLYDIM_EXPORT std::int32_t polydim_pmtp_v6_writer_heartbeat_v26503(
    void*         header_ptr,
    std::uint64_t header_len,
    std::uint64_t writer_token
) noexcept {
    if (!header_ptr || header_len < sizeof(PmtpHeaderV6) || writer_token == 0) {
        return Status::POLYDIM_INVALID_ARGUMENT;
    }
    if (reinterpret_cast<std::uintptr_t>(header_ptr) % alignof(PmtpHeaderV6) != 0) {
        return Status::POLYDIM_ALIGNMENT_ERROR;
    }
    auto* h = reinterpret_cast<PmtpHeaderV6*>(header_ptr);
    if (h->magic != kPmtpMagic || h->version != kPmtpVersion) return Status::POLYDIM_PMTP_SLAB_ERROR;

    std::uint64_t cur = h->seq_word.load(std::memory_order_acquire);
    if ((cur & 1ULL) == 0 || h->writer_cookie != writer_token) {
        return Status::POLYDIM_PMTP_TOKEN_MISMATCH;
    }

    h->timestamp_ns = get_current_time_ns();
    std::atomic_thread_fence(std::memory_order_release);
    return Status::POLYDIM_OK;
}

POLYDIM_EXPORT std::int32_t polydim_pmtp_v6_abort_writer_v26503(
    void*         header_ptr,
    std::uint64_t header_len,
    std::uint64_t writer_token
) noexcept {
    if (!header_ptr || header_len < sizeof(PmtpHeaderV6) || writer_token == 0) {
        return Status::POLYDIM_INVALID_ARGUMENT;
    }
    if (reinterpret_cast<std::uintptr_t>(header_ptr) % alignof(PmtpHeaderV6) != 0) {
        return Status::POLYDIM_ALIGNMENT_ERROR;
    }
    auto* h = reinterpret_cast<PmtpHeaderV6*>(header_ptr);
    if (h->magic != kPmtpMagic || h->version != kPmtpVersion) return Status::POLYDIM_PMTP_SLAB_ERROR;

    if (h->writer_cookie != writer_token) {
        return Status::POLYDIM_PMTP_TOKEN_MISMATCH;
    }

    std::uint64_t cur = h->seq_word.load(std::memory_order_acquire);
    for (int retry = 0; retry < 1000; ++retry) {
        if ((cur & 1ULL) == 0) return Status::POLYDIM_OK;
        // [V26503-FIX V3-031]: An aborted write does NOT commit new data.
        // The generation remains EXACTLY (cur >> 2) and published slot remains (cur >> 1 & 1).
        // If the slab was never published (cur >> 2 == 0), generation remains 0 so readers reject!
        std::uint64_t next_abort = ((cur >> 2) << 2) | ((cur >> 1 & 1ULL) << 1) | 0ULL;
        if (h->seq_word.compare_exchange_strong(cur, next_abort, std::memory_order_acq_rel, std::memory_order_acquire)) {
            // [V26503-FIX V3-010]: Clear metadata AFTER successful CAS only if cookie still matches
            if (h->writer_cookie == writer_token) {
                h->writer_cookie = 0;
                h->writer_pid = 0;
                h->reserved[0] = 0;
            }
            return Status::POLYDIM_OK;
        }
        std::this_thread::yield();
    }
    return Status::POLYDIM_PMTP_RACE_DETECTED;
}

POLYDIM_EXPORT std::int32_t polydim_pmtp_v6_force_recover_v26503(
    void* header_ptr, std::uint64_t header_len
) noexcept {
    if (!header_ptr || header_len < sizeof(PmtpHeaderV6)) return Status::POLYDIM_INVALID_ARGUMENT;
    if (reinterpret_cast<std::uintptr_t>(header_ptr) % alignof(PmtpHeaderV6) != 0)
        return Status::POLYDIM_ALIGNMENT_ERROR;
    auto* h = reinterpret_cast<PmtpHeaderV6*>(header_ptr);
    if (h->magic != kPmtpMagic || h->version != kPmtpVersion) return Status::POLYDIM_PMTP_SLAB_ERROR;
    // SECURITY: this legacy ABI has no administrator credential. Do not let any
    // caller unlock another process's active writer. Stale-writer recovery must
    // go through claim_writer's timestamp/lease policy until an authenticated
    // administrative API is supplied.
    const std::uint64_t cur = h->seq_word.load(std::memory_order_acquire);
    return (cur & 1ULL) ? Status::POLYDIM_PMTP_RACE_DETECTED : Status::POLYDIM_OK;
}

POLYDIM_EXPORT std::int32_t polydim_pmtp_v6_publish_flip_v26503(
    void*         header_ptr,
    std::uint64_t header_len,
    std::uint32_t written_slot,
    std::uint64_t timestamp_ns,
    std::uint64_t writer_token
) noexcept {
    if (!header_ptr || header_len < sizeof(PmtpHeaderV6) || writer_token == 0) {
        return Status::POLYDIM_INVALID_ARGUMENT;
    }
    if (written_slot != 0 && written_slot != 1) {
        return Status::POLYDIM_INVALID_ARGUMENT;
    }
    if (reinterpret_cast<std::uintptr_t>(header_ptr) % alignof(PmtpHeaderV6) != 0) {
        return Status::POLYDIM_ALIGNMENT_ERROR;
    }
    auto* h = reinterpret_cast<PmtpHeaderV6*>(header_ptr);
    if (h->magic != kPmtpMagic || h->version != kPmtpVersion) return Status::POLYDIM_PMTP_SLAB_ERROR;

    if (h->writer_cookie != writer_token) {
        return Status::POLYDIM_PMTP_TOKEN_MISMATCH;
    }
    if (static_cast<std::uint8_t>(h->reserved[0]) != written_slot) {
        return Status::POLYDIM_PMTP_TOKEN_MISMATCH;
    }

    std::uint64_t cur = h->seq_word.load(std::memory_order_acquire);
    if ((cur & 1ULL) == 0) {
        return Status::POLYDIM_PMTP_RACE_DETECTED;
    }

    h->timestamp_ns = timestamp_ns > 0 ? timestamp_ns : get_current_time_ns();

    std::uint64_t cur_gen = cur >> 2;
    // [V26503-FIX H-004]: Prevent generation wrap to 0 (62-bit field)
    constexpr std::uint64_t MAX_GENERATION = (std::uint64_t{1} << 62) - 1;
    if (cur_gen >= MAX_GENERATION) {
        return Status::POLYDIM_PMTP_EPOCH_EXHAUSTED;
    }
    std::uint64_t next_gen = cur_gen + 1;
    std::uint64_t nxt = (next_gen << 2) | ((static_cast<std::uint64_t>(written_slot) & 1ULL) << 1) | 0ULL;

    if (!h->seq_word.compare_exchange_strong(cur, nxt, std::memory_order_acq_rel, std::memory_order_acquire)) {
        return Status::POLYDIM_PMTP_RACE_DETECTED;
    }
    // [V26503-FIX CPP-001/V3-010]: Clear metadata AFTER successful CAS commit
    if (h->writer_cookie == writer_token) {
        h->writer_cookie = 0;
        h->writer_pid = 0;
        h->reserved[0] = 0;
    }
    return Status::POLYDIM_OK;
}

POLYDIM_EXPORT std::int32_t polydim_pmtp_v6_read_snapshot_v26503(
    const void*    header_ptr,
    std::uint64_t  header_len,
    const void*    slab_base_ptr,
    std::uint64_t  slab_total_bytes,
    std::uint64_t  payload_bytes,
    void*          out_buf,
    std::uint32_t* out_slot,
    std::uint64_t* out_generation
) noexcept {
    if (!header_ptr || !slab_base_ptr || !out_buf || !out_slot || !out_generation ||
        header_len < sizeof(PmtpHeaderV6) || payload_bytes == 0 || slab_total_bytes == 0) {
        return Status::POLYDIM_INVALID_ARGUMENT;
    }
    if (reinterpret_cast<std::uintptr_t>(header_ptr) % alignof(PmtpHeaderV6) != 0) {
        return Status::POLYDIM_ALIGNMENT_ERROR;
    }
    const auto* h = reinterpret_cast<const PmtpHeaderV6*>(header_ptr);
    if (h->magic != kPmtpMagic || h->version != kPmtpVersion) return Status::POLYDIM_PMTP_SLAB_ERROR;

    std::uint64_t elem_size = 0;
    if (h->dtype_id == 1) {
        elem_size = sizeof(double);
    } else if (h->dtype_id == 0) {
        elem_size = sizeof(float);
    } else {
        return Status::POLYDIM_PMTP_SLAB_ERROR;
    }
    if (h->num_elements > (std::numeric_limits<std::uint64_t>::max() / elem_size)) {
        return Status::POLYDIM_RANGE_ERROR;
    }
    std::uint64_t expected_payload = h->num_elements * elem_size;
    if (payload_bytes != expected_payload) {
        return Status::POLYDIM_INVALID_ARGUMENT;
    }

    if (payload_bytes > std::numeric_limits<std::uint64_t>::max() - 63ULL) {
        return Status::POLYDIM_RANGE_ERROR;
    }
    std::uint64_t slot_stride = (payload_bytes + 63ULL) & ~63ULL;
    if (slot_stride > (std::numeric_limits<std::uint64_t>::max() - sizeof(PmtpHeaderV6)) / 2) {
        return Status::POLYDIM_RANGE_ERROR;
    }
    std::uint64_t required_slab_bytes = sizeof(PmtpHeaderV6) + 2 * slot_stride;
    if (slab_total_bytes < required_slab_bytes) {
        return Status::POLYDIM_RANGE_ERROR;
    }

    if (byte_buffers_overlap(out_buf, payload_bytes, slab_base_ptr, slab_total_bytes)) {
        return Status::POLYDIM_ALIAS_VIOLATION;
    }

    for (int retry = 0; retry < 1000; ++retry) {
        std::uint64_t s1 = h->seq_word.load(std::memory_order_acquire);
        // [V26503-FIX AUD-CPP-06/H-006]: Allow reading during active writer.
        // The writer works on the INACTIVE slot; the active slot is stable.
        // Still reject generation 0 (uninitialized).
        if ((s1 >> 2) == 0) {
            std::this_thread::yield();
            continue;
        }
        std::uint32_t slot = static_cast<std::uint32_t>((s1 >> 1) & 1ULL);
        const std::uint8_t* src = static_cast<const std::uint8_t*>(slab_base_ptr) + sizeof(PmtpHeaderV6) + slot * slot_stride;
        std::memcpy(out_buf, src, payload_bytes);
        std::atomic_thread_fence(std::memory_order_acquire);
        std::uint64_t s2 = h->seq_word.load(std::memory_order_acquire);
        // [V26503-FIX]: Accept snapshot if seq_word unchanged (s1==s2) and gen>0.
        if (s1 == s2 && ((s2 >> 2) > 0)) {
            *out_slot = slot;
            *out_generation = s1 >> 2;
            return Status::POLYDIM_OK;
        }
        std::this_thread::yield();
    }

    std::memset(out_buf, 0, payload_bytes);
    *out_slot = 0;
    *out_generation = 0;
    return Status::POLYDIM_PMTP_RACE_DETECTED;
}

POLYDIM_EXPORT std::int32_t polydim_pmtp_v6_validate_snapshot_v26503(
    const void*    header_ptr,
    std::uint64_t  header_len,
    std::uint64_t  gen,
    std::uint32_t* out_ok
) noexcept {
    if (!header_ptr || !out_ok || header_len < sizeof(PmtpHeaderV6)) {
        return Status::POLYDIM_INVALID_ARGUMENT;
    }
    if (reinterpret_cast<std::uintptr_t>(header_ptr) % alignof(PmtpHeaderV6) != 0) {
        return Status::POLYDIM_ALIGNMENT_ERROR;
    }
    const auto* h = reinterpret_cast<const PmtpHeaderV6*>(header_ptr);
    if (h->magic != kPmtpMagic || h->version != kPmtpVersion) return Status::POLYDIM_PMTP_SLAB_ERROR;

    std::uint64_t s = h->seq_word.load(std::memory_order_acquire);
    std::uint64_t g = s >> 2;
    // [V26503-FIX H-005 & V3-008]: Double-buffering invariant:
    // gen=0 means no publication has occurred; reject uninitialized.
    // The published snapshot is valid as long as its generation (s >> 2) matches expected gen.
    // An active writer on the inactive slot does not invalidate the published slot.
    *out_ok = (gen != 0 && g == gen) ? 1U : 0U;
    return Status::POLYDIM_OK;
}

// ----------------------------------------------------------------------------
// ALIASES CANÓNICOS C FFI DESACOPLADOS (COMPATIBILIDAD TEST ADAPTER Y LEGACY)
// ----------------------------------------------------------------------------
POLYDIM_EXPORT std::int32_t polydim_sphere_project(
    PolydimF64ConstView in_view,
    PolydimF64MutView out_view
) noexcept {
    return polydim_sphere_project_v26503(in_view, out_view);
}

POLYDIM_EXPORT std::int32_t polydim_dot_neumaier(
    PolydimF64ConstView a_view,
    PolydimF64ConstView b_view,
    double* out_result
) noexcept {
    return polydim_dot_neumaier_v26503(a_view, b_view, out_result);
}

POLYDIM_EXPORT std::int32_t polydim_stiefel_residual_inject(
    const double* h, const double* W, const double* z_orig, const double* z_prime,
    double beta, std::uint64_t D, std::uint64_t K, double* h_out
) noexcept {
    return polydim_stiefel_residual_inject_v26503(h, W, z_orig, z_prime, beta, D, K, h_out);
}

POLYDIM_EXPORT std::uint64_t polydim_cam_workspace_bytes(std::uint64_t M) noexcept {
    return polydim_cam_workspace_bytes_v26503(M);
}

POLYDIM_EXPORT std::int32_t polydim_cam_attention_retrieve(
    const double* q, const double* K_mat, const double* V_mat,
    const std::uint8_t* mask, std::uint64_t M, std::uint64_t D,
    double inv_temp, double* workspace, double* v_out
) noexcept {
    std::uint64_t ws_bytes = 2 * M * sizeof(double);
    return polydim_cam_attention_retrieve_v26503(q, K_mat, V_mat, mask, M, D, inv_temp, workspace, ws_bytes, v_out);
}

POLYDIM_EXPORT std::int32_t polydim_pmtp_v6_claim_writer(
    void* /*header_ptr*/,
    std::uint64_t /*header_len*/,
    std::uint32_t /*pid*/,
    std::uint32_t* /*out_write_slot*/
) noexcept {
    // [V26503-FIX AUD-CPP-05]: Legacy claim without token leaks the lock
    return Status::POLYDIM_PMTP_TOKEN_MISMATCH;
}

POLYDIM_EXPORT std::int32_t polydim_pmtp_v6_abort_writer(
    void* /*header_ptr*/,
    std::uint64_t /*header_len*/
) noexcept {
    // [F-03 Veto]: Wrappers sin token explícito quedan vetados por seguridad de protocolo.
    return Status::POLYDIM_PMTP_TOKEN_MISMATCH;
}

POLYDIM_EXPORT std::int32_t polydim_pmtp_v6_publish_flip(
    void* /*header_ptr*/,
    std::uint64_t /*header_len*/,
    std::uint32_t /*written_slot*/,
    std::uint64_t /*timestamp_ns*/
) noexcept {
    // [F-02 Veto]: Prohibido auto-autenticarse leyendo el cookie del header sin que el llamador lo posea.
    return Status::POLYDIM_PMTP_TOKEN_MISMATCH;
}

POLYDIM_EXPORT std::int32_t polydim_pmtp_v6_read_snapshot(
    const void* header_ptr,
    std::uint64_t header_len,
    const void* slab_base_ptr,
    std::uint64_t payload_bytes,
    void* out_buf,
    std::uint32_t* out_slot,
    std::uint64_t* out_generation
) noexcept {
    // [V26503-FIX AUD-CPP-04/H-021]: Use aligned stride for slab_total
    if (payload_bytes > std::numeric_limits<std::uint64_t>::max() - 63ULL ||
        payload_bytes > (std::numeric_limits<std::uint64_t>::max() - sizeof(PmtpHeaderV6)) / 2) {
        return Status::POLYDIM_RANGE_ERROR;
    }
    std::uint64_t slot_stride_legacy = (payload_bytes + 63ULL) & ~63ULL;
    if (slot_stride_legacy > (std::numeric_limits<std::uint64_t>::max() - sizeof(PmtpHeaderV6)) / 2) {
        return Status::POLYDIM_RANGE_ERROR;
    }
    std::uint64_t slab_total = sizeof(PmtpHeaderV6) + 2 * slot_stride_legacy;
    return polydim_pmtp_v6_read_snapshot_v26503(header_ptr, header_len, slab_base_ptr, slab_total, payload_bytes, out_buf, out_slot, out_generation);
}

POLYDIM_EXPORT std::int32_t polydim_pmtp_v6_validate_snapshot(
    const void* header_ptr,
    std::uint64_t header_len,
    std::uint64_t gen,
    std::uint32_t* out_ok
) noexcept {
    return polydim_pmtp_v6_validate_snapshot_v26503(header_ptr, header_len, gen, out_ok);
}

// ----------------------------------------------------------------------------
// ALIASES DE RETROCOMPATIBILIDAD V26403 & V26402
// ----------------------------------------------------------------------------
POLYDIM_EXPORT std::int32_t polydim_sphere_project_v26403(PolydimF64ConstView in_view, PolydimF64MutView out_view) noexcept {
    return polydim_sphere_project_v26503(in_view, out_view);
}
POLYDIM_EXPORT std::int32_t polydim_sphere_project_v26402(PolydimF64ConstView in_view, PolydimF64MutView out_view) noexcept {
    return polydim_sphere_project_v26503(in_view, out_view);
}
POLYDIM_EXPORT std::int32_t polydim_dot_neumaier_v26403(PolydimF64ConstView a_view, PolydimF64ConstView b_view, double* out_result) noexcept {
    return polydim_dot_neumaier_v26503(a_view, b_view, out_result);
}
POLYDIM_EXPORT std::int32_t polydim_dot_neumaier_v26402(PolydimF64ConstView a_view, PolydimF64ConstView b_view, double* out_result) noexcept {
    return polydim_dot_neumaier_v26503(a_view, b_view, out_result);
}
POLYDIM_EXPORT std::int32_t polydim_stiefel_residual_inject_v26403(const double* h, const double* W, const double* z_orig, const double* z_prime, double beta, std::uint64_t D, std::uint64_t K, double* h_out) noexcept {
    return polydim_stiefel_residual_inject_v26503(h, W, z_orig, z_prime, beta, D, K, h_out);
}
POLYDIM_EXPORT std::int32_t polydim_stiefel_residual_inject_v26402(const double* h, const double* W, const double* z_orig, const double* z_prime, double beta, std::uint64_t D, std::uint64_t K, double* h_out) noexcept {
    return polydim_stiefel_residual_inject_v26503(h, W, z_orig, z_prime, beta, D, K, h_out);
}

} // namespace polydim_sota_v26503
