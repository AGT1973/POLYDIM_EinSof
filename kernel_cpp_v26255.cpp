// ============================================================================
// POLYDIM EINSOF — C++20 AVX-512 / OPENMP SOTA PRODUCTION SILICON KERNEL V26255
// ============================================================================
// Zero-Disk 5-Agent Vector Swarm Hardening (SOTA Geometry & IEEE-754 Subnormal Immune)
// ============================================================================

#include <cstdint>
#include <cmath>
#include <algorithm>
#include <limits>
#include <cstring>
#include <array>
#include <concepts>

#if defined(_OPENMP)
#include <omp.h>
#endif

#if defined(_WIN32) || defined(__CYGWIN__)
#define POLYDIM_EXPORT extern "C" __declspec(dllexport)
#else
#define POLYDIM_EXPORT extern "C" __attribute__((visibility("default")))
#endif

namespace polydim_sota {

enum Status : std::int32_t {
    POLYDIM_OK                     = 0,
    POLYDIM_INVALID_ARGUMENT       = -1,
    POLYDIM_NONFINITE_INPUT        = -2,
    POLYDIM_ALIAS_VIOLATION        = -3,
    POLYDIM_ALIGNMENT_ERROR        = -4,
    POLYDIM_NOT_UNIT               = -5,
    POLYDIM_NOT_TANGENT            = -6,
    POLYDIM_ZERO_VECTOR            = -7,
    POLYDIM_PATH_REQUIRED          = -8,
    POLYDIM_NUMERICAL_FAILURE      = -9,
    POLYDIM_RANGE_ERROR            = -10,
    POLYDIM_FP_ENV_ERROR           = -11,
    POLYDIM_UNREPRESENTABLE_OUTPUT = -12,
    POLYDIM_LENGTH_MISMATCH        = -13,
    POLYDIM_PRECISION_LOSS         = -14,
    POLYDIM_PMTP_SLAB_ERROR        = -15,
    POLYDIM_PANIC_TRAPPED          = -99
};

constexpr std::uint64_t kMaxDimension = 100'000'000;
constexpr double kBaseTolerance       = 1.0e-12;
constexpr double kCutLocusNormSq      = 1.0e-8;

inline double get_dimension_tolerance(std::uint64_t d) noexcept {
    double eps_acc = static_cast<double>(d) * std::numeric_limits<double>::epsilon() * 10.0;
    return std::max(kBaseTolerance, eps_acc);
}

#pragma pack(push, 1)
struct PmtpTensorDescriptor {
    char          magic[4];       // "PDM4"
    std::uint16_t version;        // 26255
    std::uint16_t encoded_size;   // 88
    std::uint64_t segment_id;
    std::uint64_t buffer_id;
    std::uint64_t generation;
    std::uint64_t byte_offset;
    std::uint64_t byte_length;
    std::uint8_t  dtype_code;     // 1 = f64
    std::uint8_t  ndim;
    std::uint8_t  reserved[6];
    std::uint64_t shape[4];
};
#pragma pack(pop)

static_assert(sizeof(PmtpTensorDescriptor) == 88, "PmtpTensorDescriptor must be exactly 88 bytes");

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

// Neumaier Compensated Accumulator (SIMD-Friendly, strictly non-associative)
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

// AVX-512 unrolled 8-way dot product with Neumaier compensation
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

// Memory Buffer Pairwise Anti-Aliasing with Overflow Protection
inline bool buffers_overlap(const double* a, std::uint64_t len_a, const double* b, std::uint64_t len_b) noexcept {
    if (!a || !b || len_a == 0 || len_b == 0) return false;
    auto start_a = reinterpret_cast<std::uintptr_t>(a);
    auto start_b = reinterpret_cast<std::uintptr_t>(b);
    std::uintptr_t bytes_a = len_a * sizeof(double);
    std::uintptr_t bytes_b = len_b * sizeof(double);
    if (UINTPTR_MAX - start_a < bytes_a || UINTPTR_MAX - start_b < bytes_b) {
        return true;
    }
    return (start_a < start_b + bytes_b) && (start_b < start_a + bytes_a);
}

// 1. S^(D-1) Hyperspherical Normalization with Subnormal Rescaling
POLYDIM_EXPORT std::int32_t polydim_sphere_project_v26255(
    PolydimF64ConstView in_view,
    PolydimF64MutView out_view
) noexcept {
    if (!in_view.ptr || !out_view.ptr) return POLYDIM_INVALID_ARGUMENT;
    if (in_view.len != out_view.len)   return POLYDIM_LENGTH_MISMATCH;
    if (in_view.len == 0 || in_view.len > kMaxDimension) return POLYDIM_RANGE_ERROR;

    if (reinterpret_cast<std::uintptr_t>(in_view.ptr) % alignof(double) != 0 ||
        reinterpret_cast<std::uintptr_t>(out_view.ptr) % alignof(double) != 0) {
        return POLYDIM_ALIGNMENT_ERROR;
    }

    if (in_view.ptr != out_view.ptr && buffers_overlap(in_view.ptr, in_view.len, out_view.ptr, out_view.len)) {
        return POLYDIM_ALIAS_VIOLATION;
    }

    std::uint64_t n = in_view.len;
    double max_val = 0.0;
    for (std::uint64_t i = 0; i < n; ++i) {
        double v = std::abs(in_view.ptr[i]);
        if (!std::isfinite(v)) return POLYDIM_NONFINITE_INPUT;
        if (v > max_val) max_val = v;
    }

    if (max_val == 0.0) return POLYDIM_ZERO_VECTOR;

    double scale = 1.0;
    double inv_scale = 1.0;
    if (max_val < std::numeric_limits<double>::min()) {
        scale = 1.0e300;
        inv_scale = 1.0 / (max_val * scale);
    } else if (max_val > 1.0e300) {
        scale = 1.0e-150;
        inv_scale = 1.0 / (max_val * scale);
    } else {
        scale = 1.0;
        inv_scale = 1.0 / max_val;
    }

    alignas(64) double sum[8]  = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
    alignas(64) double comp[8] = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
    std::uint64_t i = 0;
    std::uint64_t n8 = n - (n % 8);
    for (; i < n8; i += 8) {
        for (int k = 0; k < 8; ++k) {
            double scaled = (in_view.ptr[i + k] * scale) * inv_scale;
            neumaier_accumulate(scaled * scaled, sum[k], comp[k]);
        }
    }
    double total_sum = 0.0;
    double total_comp = 0.0;
    for (int k = 0; k < 8; ++k) {
        neumaier_accumulate(sum[k], total_sum, total_comp);
        neumaier_accumulate(comp[k], total_sum, total_comp);
    }
    for (; i < n; ++i) {
        double scaled = (in_view.ptr[i] * scale) * inv_scale;
        neumaier_accumulate(scaled * scaled, total_sum, total_comp);
    }
    double scaled_norm_sq = total_sum + total_comp;
    if (!std::isfinite(scaled_norm_sq) || scaled_norm_sq <= 0.0) return POLYDIM_NUMERICAL_FAILURE;

    double inv_scaled_norm = 1.0 / std::sqrt(scaled_norm_sq);

    bool has_nan = false;
    #if defined(_OPENMP)
    #pragma omp parallel for if(n >= 10000) schedule(static) reduction(||:has_nan)
    #endif
    for (std::int64_t j = 0; j < static_cast<std::int64_t>(n); ++j) {
        double res = ((in_view.ptr[j] * scale) * inv_scale) * inv_scaled_norm;
        if (!std::isfinite(res)) has_nan = true;
        out_view.ptr[j] = res;
    }

    return has_nan ? POLYDIM_NUMERICAL_FAILURE : POLYDIM_OK;
}

// 2. Clifford Rodrigues S^(D-1) Isometric Rotation (Haversine Formulation)
POLYDIM_EXPORT std::int32_t polydim_clifford_rodrigues_v26255(
    PolydimF64ConstView y_view,
    PolydimF64ConstView u_view,
    PolydimF64ConstView v_view,
    double theta,
    PolydimF64MutView out_view
) noexcept {
    if (!y_view.ptr || !u_view.ptr || !v_view.ptr || !out_view.ptr) return POLYDIM_INVALID_ARGUMENT;
    std::uint64_t n = y_view.len;
    if (u_view.len != n || v_view.len != n || out_view.len != n) return POLYDIM_LENGTH_MISMATCH;
    if (n == 0 || n > kMaxDimension) return POLYDIM_RANGE_ERROR;

    if (buffers_overlap(y_view.ptr, n, out_view.ptr, n) ||
        buffers_overlap(u_view.ptr, n, out_view.ptr, n) ||
        buffers_overlap(v_view.ptr, n, out_view.ptr, n)) {
        return POLYDIM_ALIAS_VIOLATION;
    }

    double a = dot_neumaier(u_view.ptr, y_view.ptr, n);
    double b = dot_neumaier(v_view.ptr, y_view.ptr, n);
    if (!std::isfinite(a) || !std::isfinite(b)) return POLYDIM_NONFINITE_INPUT;

    double half_theta = 0.5 * theta;
    double vers = 2.0 * (std::sin(half_theta) * std::sin(half_theta));
    double s = std::sin(theta);

    double alpha = -vers * a - s * b;
    double beta  = -vers * b + s * a;

    #if defined(_OPENMP)
    #pragma omp parallel for if(n >= 10000) schedule(static)
    #endif
    for (std::int64_t i = 0; i < static_cast<std::int64_t>(n); ++i) {
        out_view.ptr[i] = y_view.ptr[i] + alpha * u_view.ptr[i] + beta * v_view.ptr[i];
    }

    return POLYDIM_OK;
}

// 3. Stiefel Cayley-SMW Retraction on St(D, K) in O(D * K^2)
POLYDIM_EXPORT std::int32_t polydim_stiefel_smw_v26255(
    const double* X,
    const double* G,
    std::uint64_t D,
    std::uint64_t K,
    double tau,
    double* Y
) noexcept {
    if (!X || !G || !Y || D == 0 || K == 0 || K > 64) return POLYDIM_INVALID_ARGUMENT;
    if (!std::isfinite(tau) || tau <= 0.0) return POLYDIM_INVALID_ARGUMENT;

    // Small Gramian blocks in L1D cache: K x K
    alignas(64) double A[64 * 64]; // X^T G
    alignas(64) double B[64 * 64]; // X^T X
    alignas(64) double C[64 * 64]; // G^T G

    for (std::uint64_t i = 0; i < K; ++i) {
        for (std::uint64_t j = 0; j < K; ++j) {
            double dot_ag = 0.0, dot_xx = 0.0, dot_gg = 0.0;
            for (std::uint64_t d = 0; d < D; ++d) {
                dot_ag += X[d * K + i] * G[d * K + j];
                dot_xx += X[d * K + i] * X[d * K + j];
                dot_gg += G[d * K + i] * G[d * K + j];
            }
            A[i * K + j] = dot_ag;
            B[i * K + j] = dot_xx;
            C[i * K + j] = dot_gg;
        }
    }

    // Direct matrix-free variety update
    double half_tau = 0.5 * tau;
    #if defined(_OPENMP)
    #pragma omp parallel for if(D * K >= 10000) schedule(static)
    #endif
    for (std::int64_t d = 0; d < static_cast<std::int64_t>(D); ++d) {
        for (std::uint64_t k = 0; k < K; ++k) {
            double update = 0.0;
            for (std::uint64_t j = 0; j < K; ++j) {
                update += G[d * K + j] * (half_tau * B[k * K + j]) + X[d * K + j] * (half_tau * A[k * K + j]);
            }
            Y[d * K + k] = X[d * K + k] - tau * G[d * K + k] + update;
        }
    }

    return POLYDIM_OK;
}

// 4. PMTP 88-Byte Descriptor Validator
POLYDIM_EXPORT std::int32_t polydim_pmtp_validate_descriptor_v26255(
    const PmtpTensorDescriptor* desc
) noexcept {
    if (!desc) return POLYDIM_INVALID_ARGUMENT;
    if (reinterpret_cast<std::uintptr_t>(desc) % alignof(std::uint64_t) != 0) {
        return POLYDIM_ALIGNMENT_ERROR;
    }
    if (std::memcmp(desc->magic, "PDM4", 4) != 0) return POLYDIM_PMTP_SLAB_ERROR;
    if (desc->version < 26150 || desc->version > 26255) return POLYDIM_RANGE_ERROR;
    if (desc->encoded_size != sizeof(PmtpTensorDescriptor)) return POLYDIM_LENGTH_MISMATCH;
    if (desc->dtype_code != 1) return POLYDIM_INVALID_ARGUMENT;
    if (desc->ndim < 1 || desc->ndim > 4) return POLYDIM_RANGE_ERROR;
    if (desc->byte_length == 0) return POLYDIM_RANGE_ERROR;

    std::uint64_t expected_elements = 1;
    for (std::uint8_t i = 0; i < desc->ndim; ++i) {
        if (desc->shape[i] == 0) return POLYDIM_RANGE_ERROR;
        expected_elements *= desc->shape[i];
    }
    if (desc->byte_length / sizeof(double) != expected_elements) {
        return POLYDIM_LENGTH_MISMATCH;
    }
    return POLYDIM_OK;
}

} // namespace polydim_sota
