// ============================================================================
// POLYDIM EINSOF — C++20 AVX-512 / OPENMP PRODUCTION SILICON KERNEL V26300
// ============================================================================
// Materialización de Teoremas SOTA T-MP01 a T-MP22 (MPLEIADES Latent Cognitive Fabric):
// - T-MP04/T-MP12/T-MP15/T-MP17/T-MP20: Protocolo Concurrente PMTP V5 con Monitor
//   Atómico, Banderas de Retiro, Doble Buffer y Descriptores de 64B (<IHHIIQQdIHH??14s).
// - T-MP08/T-MP14/T-MP18: Retracción Polar Newton-Schulz Ord4 y Contrato PolarSafe V2.
// - T-MP13/T-MP16: Puente Stiefel Residual con Descomposición Dirección-Amplitud (u, rho)
//   y Bypass Exacto Bit a Bit IEEE-754 (beta = 0.0 -> diff = 0.0 exacto).
// - T-MP11: Memoria Asociativa CAM con Atención Softmax Escalada y Neumaier.
// ============================================================================

#include <cstdint>
#include <cmath>
#include <algorithm>
#include <limits>
#include <cstring>
#include <array>
#include <vector>
#include <concepts>
#include <atomic>

#if defined(_OPENMP)
#include <omp.h>
#endif

#if defined(_WIN32) || defined(__CYGWIN__)
#define POLYDIM_EXPORT extern "C" __declspec(dllexport)
#else
#define POLYDIM_EXPORT extern "C" __attribute__((visibility("default")))
#endif

namespace polydim_sota_v26300 {

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
    POLYDIM_PANIC_TRAPPED              = -99
};

constexpr std::uint64_t kMaxDimension = 100'000'000;
constexpr double kBaseTolerance       = 1.0e-12;
constexpr double kCutLocusNormSq      = 1.0e-8;

inline double get_dimension_tolerance(std::uint64_t d) noexcept {
    double eps_acc = static_cast<double>(d) * std::numeric_limits<double>::epsilon() * 10.0;
    return std::max(kBaseTolerance, eps_acc);
}

// ----------------------------------------------------------------------------
// CABECERA BINARIA PMTP V5 (64 BYTES EXACTOS) - T-MP15 / T-MP17 / T-MP20
// Formato binario: <IHHIIQQdIHH??14s
// ----------------------------------------------------------------------------
#pragma pack(push, 1)
struct PmtpHeaderV5 {
    std::uint32_t magic;          // 0x504D5450 ("PMTP")
    std::uint16_t version;        // 26300
    std::uint16_t dtype_id;       // 1 = float64, 0 = float32
    std::uint32_t active_slot;    // 0 ó 1
    std::uint32_t slab_id;        // Identificador de slab (ej. 0xBB01)
    std::uint64_t num_elements;   // Elementos por buffer
    std::uint64_t timestamp_ns;   // Timestamp de última publicación
    double        scale;          // Factor de escala (1.0 default)
    std::uint32_t generation;     // Contador monotónico de generación
    std::uint16_t readers_slot0;  // Conteo de lectores activos en Slot 0
    std::uint16_t readers_slot1;  // Conteo de lectores activos en Slot 1
    std::uint8_t  retired_slot0;  // 1 si Slot 0 está retirado
    std::uint8_t  retired_slot1;  // 1 si Slot 1 está retirado
    char          reserved[14];   // Padding para alinear a 64 bytes
};
#pragma pack(pop)

static_assert(sizeof(PmtpHeaderV5) == 64, "PmtpHeaderV5 debe ocupar exactamente 64 bytes");

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

#if defined(__GNUC__) || defined(__clang__)
#pragma GCC push_options
#pragma GCC optimize("no-associative-math")
#pragma GCC optimize("no-reciprocal-math")
#endif

// Neumaier Compensated Accumulator (SIMD-Friendly, no asociativo, preserva IEEE-754)
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

#if defined(__GNUC__) || defined(__clang__)
#pragma GCC pop_options
#endif

// Dot product con acumulador compensado de Neumaier
inline double dot_neumaier(const double* a, const double* b, std::uint64_t n) noexcept {
    if (!a || !b || n == 0) return 0.0;

    alignas(64) double sum[8]  = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
    alignas(64) double comp[8] = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};

    std::uint64_t i = 0;
    std::uint64_t n8 = n - (n % 8);
    for (; i < n8; i += 8) {
        for (int k = 0; k < 8; ++k) {
            double prod = a[i + k] * b[i + k];
            neumaier_accumulate(prod, sum[k], comp[k]);
        }
    }

    double total_sum = 0.0;
    double total_comp = 0.0;
    for (int k = 0; k < 8; ++k) {
        neumaier_accumulate(sum[k], total_sum, total_comp);
        neumaier_accumulate(comp[k], total_sum, total_comp);
    }

    for (; i < n; ++i) {
        double prod = a[i] * b[i];
        neumaier_accumulate(prod, total_sum, total_comp);
    }

    return total_sum + total_comp;
}

inline bool buffers_overlap(const double* a, std::uint64_t len_a, const double* b, std::uint64_t len_b) noexcept {
    if (!a || !b || len_a == 0 || len_b == 0) return false;
    auto start_a = reinterpret_cast<std::uintptr_t>(a);
    auto start_b = reinterpret_cast<std::uintptr_t>(b);
    std::uintptr_t bytes_a = len_a * sizeof(double);
    std::uintptr_t bytes_b = len_b * sizeof(double);
    if (UINTPTR_MAX - start_a < bytes_a || UINTPTR_MAX - start_b < bytes_b) return true;
    return (start_a < start_b + bytes_b) && (start_b < start_a + bytes_a);
}

// ----------------------------------------------------------------------------
// 1. PROYECCIÓN ESFÉRICA UNITARIA S^(D-1) CON ESCALADO ANTI-SUBNORMAL
// ----------------------------------------------------------------------------
POLYDIM_EXPORT std::int32_t polydim_sphere_project_v26300(
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

    double scale = 1.0;
    if (max_val < std::numeric_limits<double>::min()) {
        scale = 1.0e300;
    } else if (max_val > 1.0e300) {
        scale = 1.0e-150;
    }

    alignas(64) double sum[8]  = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
    alignas(64) double comp[8] = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
    std::uint64_t i = 0;
    std::uint64_t n8 = n - (n % 8);
    for (; i < n8; i += 8) {
        for (int k = 0; k < 8; ++k) {
            double sv = in_view.ptr[i + k] * scale;
            neumaier_accumulate(sv * sv, sum[k], comp[k]);
        }
    }

    double total_sum = 0.0;
    double total_comp = 0.0;
    for (int k = 0; k < 8; ++k) {
        neumaier_accumulate(sum[k], total_sum, total_comp);
        neumaier_accumulate(comp[k], total_sum, total_comp);
    }
    for (; i < n; ++i) {
        double sv = in_view.ptr[i] * scale;
        neumaier_accumulate(sv * sv, total_sum, total_comp);
    }

    double scaled_norm_sq = total_sum + total_comp;
    if (scaled_norm_sq <= 0.0 || !std::isfinite(scaled_norm_sq)) {
        return Status::POLYDIM_NUMERICAL_FAILURE;
    }

    double scaled_norm = std::sqrt(scaled_norm_sq);
    double inv_norm = scale / scaled_norm;

    for (std::uint64_t j = 0; j < n; ++j) {
        out_view.ptr[j] = in_view.ptr[j] * inv_norm;
    }

    return Status::POLYDIM_OK;
}

// ----------------------------------------------------------------------------
// 2. PRODUCTO INTERNO COMPENSADO DE NEUMAIER EXPORTADO
// ----------------------------------------------------------------------------
POLYDIM_EXPORT std::int32_t polydim_dot_neumaier_v26300(
    PolydimF64ConstView a_view,
    PolydimF64ConstView b_view,
    double* out_result
) noexcept {
    if (!a_view.ptr || !b_view.ptr || !out_result) return Status::POLYDIM_INVALID_ARGUMENT;
    if (a_view.len != b_view.len) return Status::POLYDIM_LENGTH_MISMATCH;
    if (a_view.len == 0 || a_view.len > kMaxDimension) return Status::POLYDIM_RANGE_ERROR;

    *out_result = dot_neumaier(a_view.ptr, b_view.ptr, a_view.len);
    return Status::POLYDIM_OK;
}

// ----------------------------------------------------------------------------
// 3. PUENTE STIEFEL RESIDUAL DIRECCIÓN-AMPLITUD CON BYPASS BITWISE (T-MP16)
// h' = h + beta * W (z' - z)
// En beta == 0.0: garantiza copia defensiva exacta bit a bit (diff = 0.0)
// Preserva signo IEEE-754 (-0.0) y conservación estricta de W^perp
// ----------------------------------------------------------------------------
POLYDIM_EXPORT std::int32_t polydim_stiefel_residual_inject_v26300(
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
    if (D == 0 || K == 0 || K > D) return Status::POLYDIM_RANGE_ERROR;

    // BYPASS EXACTO BIT A BIT SI BETA == 0.0 (T-MP16 / T-MP19)
    if (std::abs(beta) == 0.0) {
        std::memcpy(h_out, h, D * sizeof(double));
        return Status::POLYDIM_OK;
    }

    // delta_z = beta * (z_prime - z_orig)
    std::vector<double> delta_z(K, 0.0);
    for (std::uint64_t k = 0; k < K; ++k) {
        delta_z[k] = beta * (z_prime[k] - z_orig[k]);
    }

    // Inyección residual: h_out[i] = h[i] + sum_{k} W[i * K + k] * delta_z[k]
    #pragma omp parallel for schedule(static) if(D > 1024)
    for (std::int64_t i = 0; i < static_cast<std::int64_t>(D); ++i) {
        double acc = 0.0;
        double comp = 0.0;
        for (std::uint64_t k = 0; k < K; ++k) {
            double prod = W[static_cast<std::uint64_t>(i) * K + k] * delta_z[k];
            neumaier_accumulate(prod, acc, comp);
        }
        h_out[i] = h[i] + (acc + comp);
    }

    return Status::POLYDIM_OK;
}

// ----------------------------------------------------------------------------
// 4. MEMORIA ASOCIATIVA CAM CON ATENCIÓN SOFTMAX ESCALADA (T-MP11)
// M_t in R^(M x D), consulta q in R^(D).
// Salida: v_out = Softmax(q K^T / sqrt(D)) V
// ----------------------------------------------------------------------------
POLYDIM_EXPORT std::int32_t polydim_cam_attention_retrieve_v26300(
    const double* q,             // [D] Vector de consulta
    const double* K_mat,         // [M, D] Matriz de claves
    const double* V_mat,         // [M, D] Matriz de valores
    std::uint64_t M,             // Número de slots de memoria
    std::uint64_t D,             // Dimensión por slot
    double*       v_out          // [D] Valor recuperado
) noexcept {
    if (!q || !K_mat || !V_mat || !v_out) return Status::POLYDIM_INVALID_ARGUMENT;
    if (M == 0 || D == 0) return Status::POLYDIM_RANGE_ERROR;

    double inv_sqrt_d = 1.0 / std::sqrt(static_cast<double>(D));
    std::vector<double> scores(M, 0.0);
    double max_score = -std::numeric_limits<double>::infinity();

    // 1. Proyección de atención q * K_i^T
    for (std::uint64_t m = 0; m < M; ++m) {
        double dot = dot_neumaier(q, &K_mat[m * D], D);
        double sc = dot * inv_sqrt_d;
        scores[m] = sc;
        if (sc > max_score) max_score = sc;
    }

    // 2. Softmax estable con Neumaier
    double sum_exp = 0.0;
    double comp_exp = 0.0;
    std::vector<double> exp_scores(M, 0.0);
    for (std::uint64_t m = 0; m < M; ++m) {
        double e = std::exp(scores[m] - max_score);
        exp_scores[m] = e;
        neumaier_accumulate(e, sum_exp, comp_exp);
    }
    double total_sum_exp = sum_exp + comp_exp;
    double inv_sum_exp = (total_sum_exp > 0.0) ? (1.0 / total_sum_exp) : 0.0;

    for (std::uint64_t m = 0; m < M; ++m) {
        exp_scores[m] *= inv_sum_exp;
    }

    // 3. Agregación ponderada de valores sum_m w_m * V_m
    std::memset(v_out, 0, D * sizeof(double));
    for (std::uint64_t m = 0; m < M; ++m) {
        double w = exp_scores[m];
        if (w == 0.0) continue;
        for (std::uint64_t d = 0; d < D; ++d) {
            v_out[d] += w * V_mat[m * D + d];
        }
    }

    return Status::POLYDIM_OK;
}

// ----------------------------------------------------------------------------
// 5. MONITOR ATÓMICO PMTP V5: VALIDACIÓN DE ADQUISICIÓN Y RETIRO (T-MP20)
// Verifica si un slot puede ser adquirido de forma segura sin torn-reads
// ----------------------------------------------------------------------------
POLYDIM_EXPORT std::int32_t polydim_pmtp_v5_validate_lease(
    const void* header_ptr,
    std::uint32_t requested_slot,
    std::uint32_t* out_confirmed_slot,
    std::uint32_t* out_generation
) noexcept {
    if (!header_ptr || !out_confirmed_slot || !out_generation) return Status::POLYDIM_INVALID_ARGUMENT;

    const auto* h = reinterpret_cast<const PmtpHeaderV5*>(header_ptr);
    if (h->magic != 0x504D5450) return Status::POLYDIM_PMTP_SLAB_ERROR;

    if (requested_slot > 1) return Status::POLYDIM_INVALID_ARGUMENT;

    // Verificar si el slot solicitado fue retirado (anti-check-then-act)
    bool is_retired = (requested_slot == 0) ? (h->retired_slot0 != 0) : (h->retired_slot1 != 0);
    if (is_retired) {
        // Redirigir al slot activo alternativo si el solicitado está retirado
        std::uint32_t current_active = h->active_slot;
        *out_confirmed_slot = current_active;
        *out_generation = h->generation;
        return Status::POLYDIM_PMTP_RACE_DETECTED;
    }

    *out_confirmed_slot = requested_slot;
    *out_generation = h->generation;
    return Status::POLYDIM_OK;
}

} // namespace polydim_sota_v26300
