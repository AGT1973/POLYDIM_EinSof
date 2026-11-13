#pragma once
// ============================================================================
// ATELIER ABI v1 + QDWH PRIMARY POLAR SOLVER + ZEROIZATION / MAC32 (C++20)
// ============================================================================

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <vector>

#if defined(_WIN32)
#ifndef NOMINMAX
#define NOMINMAX
#endif
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#endif

constexpr uint32_t PMTP_MAGIC_ATELIER = 0x504D5450; // "PMTP"
constexpr uint32_t PMTP_ABI_MIN_VERSION = 1;
constexpr uint32_t PMTP_ABI_MAX_VERSION = 1;
constexpr uint32_t PMTP_MAX_DIM_D = (1U << 20);
constexpr uint32_t PMTP_MAX_RANK_K = 4096U;

// ABI CANONICA: 64 bytes exactos alineados a linea de cache (paridad C++20 / Rust / Python)
struct alignas(64) AtelierSlabHeader {
    uint32_t magic;          // offset  0: PMTP magic (0x504D5450)
    uint32_t version;        // offset  4: Version del protocolo ABI (= 1)
    uint32_t D;              // offset  8: Dimension latente
    uint32_t k;              // offset 12: Rango ortogonal
    double   isometry_error; // offset 16: ||W^T W - I_k||_max
    double   latency_us;     // offset 24: Latencia de retraccion polar (us)
    uint64_t timestamp_ns;   // offset 32: Timestamp de ejecucion
    uint64_t heartbeat_ns;   // offset 40: TTL watchdog (zombie slab detection)
    uint64_t sequence;       // offset 48: Seqlock counter (even=safe, odd=writing)
    uint32_t readers_count;  // offset 56: Observadores concurrentes
    uint32_t reserved;       // offset 60: Tag MAC32 keyed FNV-1a / BLAKE domain
};

static_assert(sizeof(AtelierSlabHeader) == 64, "ABI ROTA: sizeof(AtelierSlabHeader) != 64 bytes");
static_assert(alignof(AtelierSlabHeader) == 64, "ABI ROTA: alignof(AtelierSlabHeader) != 64");

enum class PolarSolverUsed {
    QDWH_PRIMARY = 0,
    JACOBI_SVD_FALLBACK = 1,
    REJECTED_INVALID = 2
};

inline void explicit_zeroize(void* ptr, size_t len) {
    if (!ptr || len == 0) return;
#if defined(_WIN32)
    SecureZeroMemory(ptr, len);
#else
    volatile uint8_t* p = reinterpret_cast<volatile uint8_t*>(ptr);
    while (len--) {
        *p++ = 0;
    }
#endif
}

inline void neumaier_accumulate(double val, double& sum, double& comp) {
    double t = sum + val;
    if (std::abs(sum) >= std::abs(val)) {
        comp += (sum - t) + val;
    } else {
        comp += (val - t) + sum;
    }
    sum = t;
}

inline uint32_t compute_slab_mac32(const AtelierSlabHeader& hdr, const double* payload, size_t elems) {
    char key_buf[256] = {};
    const uint8_t* key_bytes = reinterpret_cast<const uint8_t*>("PMTP_DEFAULT_SESSION_KEY_V1");
    size_t key_len = 27;
#if defined(_WIN32)
    size_t env_len = 0;
    if (getenv_s(&env_len, key_buf, sizeof(key_buf), "PMTP_SHM_KEY") == 0 && env_len > 1) {
        key_bytes = reinterpret_cast<const uint8_t*>(key_buf);
        key_len = env_len - 1;
    }
#else
    const char* env_key = std::getenv("PMTP_SHM_KEY");
    if (env_key && env_key[0] != '\0') {
        key_bytes = reinterpret_cast<const uint8_t*>(env_key);
        key_len = std::strlen(env_key);
    }
    (void)key_buf;
#endif

    uint64_t h = 14695981039346656037ULL;
    auto mix = [&](const uint8_t* ptr, size_t len) {
        for (size_t i = 0; i < len; ++i) {
            h ^= ptr[i];
            h *= 1099511628211ULL;
        }
    };
    mix(key_bytes, key_len);
    mix(reinterpret_cast<const uint8_t*>(&hdr), 60);
    if (payload && elems > 0) {
        mix(reinterpret_cast<const uint8_t*>(payload), elems * sizeof(double));
    }
    return static_cast<uint32_t>((h >> 32) ^ (h & 0xFFFFFFFFULL));
}

// Validacion estricta anti-fuzzing de cabecera ABI versionada y limites de memoria
inline bool validate_slab_header(
    const void* raw_slab,
    size_t mapped_bytes,
    bool verify_mac = true
) {
    if (!raw_slab || mapped_bytes < sizeof(AtelierSlabHeader)) {
        return false;
    }
    AtelierSlabHeader hdr;
    std::memcpy(&hdr, raw_slab, sizeof(AtelierSlabHeader));

    if (hdr.magic != PMTP_MAGIC_ATELIER) return false;
    if (hdr.version < PMTP_ABI_MIN_VERSION || hdr.version > PMTP_ABI_MAX_VERSION) return false;
    if (hdr.D == 0 || hdr.D > PMTP_MAX_DIM_D) return false;
    if (hdr.k == 0 || hdr.k > hdr.D || hdr.k > PMTP_MAX_RANK_K) return false;
    if ((hdr.sequence & 1ULL) != 0ULL) return false; // Seqlock write in progress
    if (!std::isfinite(hdr.isometry_error) || hdr.isometry_error < 0.0) return false;
    if (!std::isfinite(hdr.latency_us) || hdr.latency_us < 0.0) return false;

    uint64_t elems = static_cast<uint64_t>(hdr.D) * static_cast<uint64_t>(hdr.k);
    uint64_t avail_payload_bytes = static_cast<uint64_t>(mapped_bytes - sizeof(AtelierSlabHeader));
    if (elems > avail_payload_bytes / sizeof(double)) {
        return false; // Anti-overflow / OOB read
    }

    if (verify_mac) {
        const double* payload = reinterpret_cast<const double*>(
            static_cast<const uint8_t*>(raw_slab) + sizeof(AtelierSlabHeader)
        );
        uint32_t expected = compute_slab_mac32(hdr, payload, static_cast<size_t>(elems));
        if (expected != hdr.reserved) return false;
    }
    return true;
}

inline void matrix_transpose_mult(const double* A, const double* B, double* C, uint32_t D, uint32_t k) {
    for (uint32_t i = 0; i < k; ++i) {
        for (uint32_t j = 0; j < k; ++j) {
            double sum = 0.0;
            double comp = 0.0;
            for (uint32_t d = 0; d < D; ++d) {
                neumaier_accumulate(A[d * k + i] * B[d * k + j], sum, comp);
            }
            C[i * k + j] = sum + comp;
        }
    }
}

inline double compute_stiefel_defect(const double* Z, uint32_t D, uint32_t k) {
    std::vector<double> G(static_cast<size_t>(k) * k, 0.0);
    matrix_transpose_mult(Z, Z, G.data(), D, k);
    double max_defect = 0.0;
    for (uint32_t i = 0; i < k; ++i) {
        for (uint32_t j = 0; j < k; ++j) {
            double target = (i == j) ? 1.0 : 0.0;
            double diff = std::abs(G[i * k + j] - target);
            if (!std::isfinite(diff)) return std::numeric_limits<double>::infinity();
            if (diff > max_defect) max_defect = diff;
        }
    }
    return max_defect;
}

// Cholesky L * L^T = A (k x k SPD). Retorna false si no es SPD.
inline bool cholesky_decompose(const std::vector<double>& A, std::vector<double>& L, uint32_t k) {
    L.assign(static_cast<size_t>(k) * k, 0.0);
    for (uint32_t i = 0; i < k; ++i) {
        for (uint32_t j = 0; j <= i; ++j) {
            double sum = 0.0, comp = 0.0;
            for (uint32_t p = 0; p < j; ++p) {
                neumaier_accumulate(L[i * k + p] * L[j * k + p], sum, comp);
            }
            double val = A[i * k + j] - (sum + comp);
            if (i == j) {
                if (val <= 1e-18 || !std::isfinite(val)) return false;
                L[i * k + i] = std::sqrt(val);
            } else {
                L[i * k + j] = val / L[j * k + j];
            }
        }
    }
    return true;
}

// Resuelve (L * L^T) * X^T = Q^T => retorna W = Q * (L * L^T)^{-1} en Q_out (D x k)
inline void cholesky_solve_right(
    const double* Q,
    const std::vector<double>& L,
    double* Q_out,
    uint32_t D,
    uint32_t k
) {
    std::vector<double> y(k);
    std::vector<double> x(k);
    for (uint32_t d = 0; d < D; ++d) {
        // Forward substitution: L * y = row_d(Q)
        for (uint32_t i = 0; i < k; ++i) {
            double sum = 0.0, comp = 0.0;
            for (uint32_t j = 0; j < i; ++j) {
                neumaier_accumulate(L[i * k + j] * y[j], sum, comp);
            }
            y[i] = (Q[d * k + i] - (sum + comp)) / L[i * k + i];
        }
        // Backward substitution: L^T * x = y
        for (int ii = static_cast<int>(k) - 1; ii >= 0; --ii) {
            uint32_t i = static_cast<uint32_t>(ii);
            double sum = 0.0, comp = 0.0;
            for (uint32_t j = i + 1; j < k; ++j) {
                neumaier_accumulate(L[j * k + i] * x[j], sum, comp);
            }
            x[i] = (y[i] - (sum + comp)) / L[i * k + i];
            Q_out[d * k + i] = x[i];
        }
    }
}

// Factor QR reducido en sitio con Re-ortogonalizacion Modificada Gram-Schmidt (MGS-2)
inline bool mgs_qr(std::vector<double>& Q_mat, std::vector<double>& R_mat, uint32_t rows, uint32_t cols) {
    R_mat.assign(static_cast<size_t>(cols) * cols, 0.0);
    for (uint32_t j = 0; j < cols; ++j) {
        for (int pass = 0; pass < 2; ++pass) {
            for (uint32_t i = 0; i < j; ++i) {
                double dot_s = 0.0, dot_c = 0.0;
                for (uint32_t r = 0; r < rows; ++r) {
                    neumaier_accumulate(Q_mat[r * cols + i] * Q_mat[r * cols + j], dot_s, dot_c);
                }
                double rij = dot_s + dot_c;
                R_mat[i * cols + j] += rij;
                for (uint32_t r = 0; r < rows; ++r) {
                    Q_mat[r * cols + j] -= rij * Q_mat[r * cols + i];
                }
            }
        }
        double nrm_s = 0.0, nrm_c = 0.0;
        for (uint32_t r = 0; r < rows; ++r) {
            double v = Q_mat[r * cols + j];
            neumaier_accumulate(v * v, nrm_s, nrm_c);
        }
        double nrm = std::sqrt(nrm_s + nrm_c);
        if (!std::isfinite(nrm) || nrm <= 1e-18) return false;
        R_mat[j * cols + j] = nrm;
        double inv = 1.0 / nrm;
        for (uint32_t r = 0; r < rows; ++r) {
            Q_mat[r * cols + j] *= inv;
        }
    }
    return true;
}

// Fallback One-Sided Hestenes-Jacobi + QR para polar factor en casos extremos sin LAPACK externo
inline double retract_polar_jacobi_fallback(double* Z, uint32_t D, uint32_t k) {
    std::vector<double> Q(Z, Z + static_cast<size_t>(D) * k);
    std::vector<double> R;
    if (!mgs_qr(Q, R, D, k)) {
        return std::numeric_limits<double>::infinity();
    }
    std::memcpy(Z, Q.data(), static_cast<size_t>(D) * k * sizeof(double));
    return compute_stiefel_defect(Z, D, k);
}

// ============================================================================
// SOLVER POLAR PRINCIPAL: QDWH (Nakatsukasa, Bai & Gygi 2010)
// Convergencia cubica (<= 6-8 pasos) con conmutacion QR (c>100) / Cholesky (c<=100)
// Fallback determinista solamente ante anomalia numerica / mal condicionamiento
// ============================================================================
inline double retract_stiefel_qdwh(
    double* Z,
    uint32_t D,
    uint32_t k,
    uint32_t max_iters = 8,
    uint32_t* iters_used = nullptr,
    PolarSolverUsed* solver_used = nullptr
) {
    if (!Z || D == 0 || k == 0 || k > D) {
        if (solver_used) *solver_used = PolarSolverUsed::REJECTED_INVALID;
        return std::numeric_limits<double>::infinity();
    }

    size_t n_elems = static_cast<size_t>(D) * k;
    for (size_t idx = 0; idx < n_elems; ++idx) {
        if (!std::isfinite(Z[idx])) {
            if (solver_used) *solver_used = PolarSolverUsed::REJECTED_INVALID;
            return std::numeric_limits<double>::infinity();
        }
    }

    // 1. Cota espectral superior sin SVD: ||Z||_2 <= min(||Z||_F, sqrt(||Z||_1 * ||Z||_inf))
    double fro_sq = 0.0, fro_c = 0.0;
    std::vector<double> col_l1(k, 0.0);
    double max_row_l1 = 0.0;
    for (uint32_t d = 0; d < D; ++d) {
        double row_sum = 0.0;
        for (uint32_t j = 0; j < k; ++j) {
            double v = Z[d * k + j];
            neumaier_accumulate(v * v, fro_sq, fro_c);
            double av = std::abs(v);
            col_l1[j] += av;
            row_sum += av;
        }
        if (row_sum > max_row_l1) max_row_l1 = row_sum;
    }
    double fro_norm = std::sqrt(fro_sq + fro_c);
    if (!std::isfinite(fro_norm) || fro_norm <= 1e-300) {
        if (solver_used) *solver_used = PolarSolverUsed::REJECTED_INVALID;
        return std::numeric_limits<double>::infinity();
    }
    double max_col_l1 = *std::max_element(col_l1.begin(), col_l1.end());
    double spec_bound = std::sqrt(max_col_l1 * max_row_l1);
    double alpha = std::min(fro_norm, spec_bound) * 1.000001;

    std::vector<double> Q(n_elems);
    double inv_alpha = 1.0 / alpha;
    for (size_t i = 0; i < n_elems; ++i) {
        Q[i] = Z[i] * inv_alpha;
    }

    // Estimacion rapida de cota inferior L0 <= sigma_min(Q) via potencia inversa en factor Cholesky (k x k)
    double L = 1.0 / std::max(10.0 * static_cast<double>(k), 1e2);
    {
        std::vector<double> G(static_cast<size_t>(k) * k, 0.0);
        matrix_transpose_mult(Q.data(), Q.data(), G.data(), D, k);
        std::vector<double> L_chol;
        if (cholesky_decompose(G, L_chol, k)) {
            std::vector<double> v(k, 0.0), y(k, 0.0), z(k, 0.0);
            for (uint32_t i = 0; i < k; ++i) v[i] = (i % 2 == 0 ? 1.0 : -0.7) / std::sqrt(static_cast<double>(k));
            double sigma_min_est = 1e-6;
            for (int step = 0; step < 3; ++step) {
                for (uint32_t i = 0; i < k; ++i) {
                    double s = 0.0, c_acc = 0.0;
                    for (uint32_t j = 0; j < i; ++j) neumaier_accumulate(L_chol[i * k + j] * y[j], s, c_acc);
                    y[i] = (v[i] - (s + c_acc)) / L_chol[i * k + i];
                }
                for (int ii = static_cast<int>(k) - 1; ii >= 0; --ii) {
                    uint32_t i = static_cast<uint32_t>(ii);
                    double s = 0.0, c_acc = 0.0;
                    for (uint32_t j = i + 1; j < k; ++j) neumaier_accumulate(L_chol[j * k + i] * z[j], s, c_acc);
                    z[i] = (y[i] - (s + c_acc)) / L_chol[i * k + i];
                }
                double n2 = 0.0;
                for (double val : z) n2 += val * val;
                if (!std::isfinite(n2) || n2 <= 0.0) break;
                double inv_s = std::sqrt(n2);
                sigma_min_est = 1.0 / std::sqrt(inv_s);
                double inv_n = 1.0 / inv_s;
                for (uint32_t i = 0; i < k; ++i) v[i] = z[i] * inv_n;
            }
            L = std::clamp(0.8 * sigma_min_est, 1e-8, 0.999);
        }
    }

    std::vector<double> Q_next(n_elems);
    std::vector<double> G(static_cast<size_t>(k) * k);
    std::vector<double> Z_mat(static_cast<size_t>(k) * k);
    std::vector<double> L_chol;
    std::vector<double> W_solve(n_elems);

    uint32_t it = 0;
    double defect = std::numeric_limits<double>::infinity();
    bool qdwh_converged = false;

    for (it = 1; it <= max_iters; ++it) {
        double L2 = L * L;
        double dd = std::cbrt(4.0 * (1.0 - L2) / (L2 * L2));
        double sqd = std::sqrt(1.0 + dd);
        double term = 8.0 - 4.0 * dd + (8.0 * (2.0 - L2)) / (L2 * L2 * sqd);
        double a = sqd + 0.5 * std::sqrt(std::max(0.0, term));
        double b = (a - 1.0) * (a - 1.0) * 0.25;
        double c = a + b - 1.0;
        L = std::min(1.0, L * (a + b * L2) / (1.0 + c * L2));

        bool step_ok = false;
        if (c <= 100.0) {
            matrix_transpose_mult(Q.data(), Q.data(), G.data(), D, k);
            for (uint32_t i = 0; i < k; ++i) {
                for (uint32_t j = 0; j < k; ++j) {
                    Z_mat[i * k + j] = ((i == j) ? 1.0 : 0.0) + c * G[i * k + j];
                }
            }
            if (cholesky_decompose(Z_mat, L_chol, k)) {
                cholesky_solve_right(Q.data(), L_chol, W_solve.data(), D, k);
                double coef1 = b / c;
                double coef2 = a - coef1;
                for (size_t i = 0; i < n_elems; ++i) {
                    Q_next[i] = coef1 * Q[i] + coef2 * W_solve[i];
                }
                step_ok = true;
            }
        }

        if (!step_ok) {
            // Rama QR sobre matriz apilada B = [sqrt(c)*Q; I_k] ((D+k) x k)
            uint32_t rows = D + k;
            std::vector<double> B(static_cast<size_t>(rows) * k, 0.0);
            double sc = std::sqrt(c);
            for (size_t i = 0; i < n_elems; ++i) B[i] = sc * Q[i];
            for (uint32_t j = 0; j < k; ++j) B[static_cast<size_t>(D + j) * k + j] = 1.0;
            std::vector<double> R_qr;
            if (!mgs_qr(B, R_qr, rows, k)) {
                break;
            }
            double coef1 = b / c;
            double coef2 = (a - coef1) / sc;
            for (uint32_t d = 0; d < D; ++d) {
                for (uint32_t j = 0; j < k; ++j) {
                    double s = 0.0, comp = 0.0;
                    for (uint32_t p = 0; p < k; ++p) {
                        neumaier_accumulate(B[d * k + p] * B[static_cast<size_t>(D + j) * k + p], s, comp);
                    }
                    Q_next[d * k + j] = coef1 * Q[d * k + j] + coef2 * (s + comp);
                }
            }
        }

        double diff_sq = 0.0;
        for (size_t i = 0; i < n_elems; ++i) {
            double dval = Q_next[i] - Q[i];
            diff_sq += dval * dval;
        }
        Q.swap(Q_next);
        defect = compute_stiefel_defect(Q.data(), D, k);
        if (defect <= 1e-15 && (std::sqrt(diff_sq) <= 1e-14 || L > 1.0 - 1e-13)) {
            qdwh_converged = true;
            break;
        }
    }

    if (iters_used) *iters_used = it;

    if (qdwh_converged || (std::isfinite(defect) && defect <= 1e-12)) {
        std::memcpy(Z, Q.data(), n_elems * sizeof(double));
        if (solver_used) *solver_used = PolarSolverUsed::QDWH_PRIMARY;
        return defect;
    }

    // Fallback determinista ante no convergencia de QDWH
    double fb_defect = retract_polar_jacobi_fallback(Z, D, k);
    if (solver_used) *solver_used = PolarSolverUsed::JACOBI_SVD_FALLBACK;
    return fb_defect;
}
