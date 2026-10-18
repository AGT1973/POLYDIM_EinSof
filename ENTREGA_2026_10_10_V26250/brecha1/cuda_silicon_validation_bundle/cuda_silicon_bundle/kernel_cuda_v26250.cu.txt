// ============================================================================
// POLYDIM EINSOF — STIEFEL CAYLEY NATIVE CUDA C++20 CORE V26250 HARDENED
// ============================================================================
//
// Purpose:
//   Production-grade NVIDIA GPU Stiefel Manifold Cayley Retraction in pure
//   C++20/CUDA using cuBLAS and cuSOLVER under Rule 27 (Silicon Contract)
//   and Rule 22 (Ghost Protocol / PMTP Monolithic Memory Pool).
//
// Manifold Contract:
//   St(D, K) = { X in R^(D x K) : X^T @ X = I_K }
//   1 <= K <= 64,  K <= D <= 10_000_000,  FP64 IEEE-754 binary64
//
// Hardening Remediations V26250:
//   1. Full cuBLAS / cuSOLVER Cayley-Woodbury Orchestration (K-01):
//      Replaced empty stub with exact O(D*K^2 + K^3) Sherman-Morrison-Woodbury
//      Cayley retraction:
//        U = [Z, X] in R^(D x 2K),  V = [X, -Z] in R^(D x 2K)
//        G = V^T @ U in R^(2K x 2K),  B = V^T @ X in R^(2K x K)
//        M = I_{2K} - (tau/2) * G
//        Solve M @ W = B via cusolverDnDgetrf + getrs (LU decomposition)
//        R = X + (tau/2) * U @ W via cublasDgemm
//   2. Explicit Workspace Parameter (K-02):
//      Added d_workspace and workspace_bytes to FFI signature, strictly
//      enforcing the Monolithic Memory Pool and eliminating dynamic cudaMalloc.
//   3. Sign-Invariant Spectral Guards (K-03):
//      Replaced denom > 1e-15 with std::abs(denom) > 1e-15 in Lyapunov kernels
//      to correctly support general non-convex spectra.
// ============================================================================

#include <cuda_runtime.h>
#include <cublas_v2.h>
#include <cusolverDn.h>

#include <cstdint>
#include <cmath>
#include <algorithm>
#include <limits>

#if defined(_WIN32) || defined(__CYGWIN__)
#define POLYDIM_EXPORT extern "C" __declspec(dllexport)
#else
#define POLYDIM_EXPORT extern "C" __attribute__((visibility("default")))
#endif

namespace polydim_v26150 {

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

constexpr std::int64_t kMaxDimension = 10'000'000;
constexpr std::int64_t kMaxK         = 64;

#define CUDA_CHECK(expr) do { \
    cudaError_t err_ = (expr); \
    if (err_ != cudaSuccess) return polydim_v26150::POLYDIM_NUMERICAL_FAILURE; \
} while(0)

#define CUBLAS_CHECK(expr) do { \
    cublasStatus_t stat_ = (expr); \
    if (stat_ != CUBLAS_STATUS_SUCCESS) return polydim_v26150::POLYDIM_NUMERICAL_FAILURE; \
} while(0)

#define CUSOLVER_CHECK(expr) do { \
    cusolverStatus_t stat_ = (expr); \
    if (stat_ != CUSOLVER_STATUS_SUCCESS) return polydim_v26150::POLYDIM_NUMERICAL_FAILURE; \
} while(0)

// Fused U = [Z, X] and V = [X, -Z] packing kernel
__global__ void k_pack_uv(
    std::int64_t D,
    int K,
    const double* __restrict__ X,
    const double* __restrict__ Z,
    double* __restrict__ U,
    double* __restrict__ V
) {
    std::int64_t row = blockIdx.x * blockDim.x + threadIdx.x;
    if (row < D) {
        for (int j = 0; j < K; ++j) {
            // Column-major indexing: index = row + col * D
            double x_val = X[row + static_cast<std::int64_t>(j) * D];
            double z_val = Z[row + static_cast<std::int64_t>(j) * D];

            // U = [Z, X]
            U[row + static_cast<std::int64_t>(j) * D]       = z_val;
            U[row + static_cast<std::int64_t>(j + K) * D]   = x_val;

            // V = [X, -Z]
            V[row + static_cast<std::int64_t>(j) * D]       = x_val;
            V[row + static_cast<std::int64_t>(j + K) * D]   = -z_val;
        }
    }
}

// In-place formation of system matrix: M = I_{2K} - alpha * G
__global__ void k_form_woodbury_system(
    int r,
    double alpha,
    double* __restrict__ G
) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    if (row < r && col < r) {
        std::size_t idx = static_cast<std::size_t>(row) + static_cast<std::size_t>(col) * r;
        double g_val = G[idx];
        double eye_val = (row == col) ? 1.0 : 0.0;
        G[idx] = eye_val - alpha * g_val;
    }
}

// Sign-invariant Lyapunov solver (K-03: supports indefinite spectra)
__global__ void k_lyapunov_elemwise_solve(
    const double* __restrict__ eigvals,
    const double* __restrict__ Q_rhs_Q,
    double* __restrict__ lyap_work,
    int k
) {
    int r = blockIdx.y * blockDim.y + threadIdx.y;
    int c = blockIdx.x * blockDim.x + threadIdx.x;
    if (r < k && c < k) {
        double denom = eigvals[r] + eigvals[c];
        lyap_work[r * k + c] = (std::abs(denom) > 1e-15) ? (Q_rhs_Q[r * k + c] / denom) : 0.0;
    }
}

__global__ void k_compute_ginv(
    const double* __restrict__ Q,
    const double* __restrict__ eigvals,
    double* __restrict__ Ginv,
    int k
) {
    int r = blockIdx.y * blockDim.y + threadIdx.y;
    int c = blockIdx.x * blockDim.x + threadIdx.x;
    if (r < k && c < k) {
        double sum = 0.0;
        for (int i = 0; i < k; ++i) {
            double inv_lam = (std::abs(eigvals[i]) > 1e-15) ? (1.0 / eigvals[i]) : 0.0;
            sum += Q[r * k + i] * inv_lam * Q[c * k + i];
        }
        Ginv[r * k + c] = sum;
    }
}

} // namespace polydim_v26150

// Exported Stiefel Cayley Retraction with Monolithic Workspace
POLYDIM_EXPORT std::int32_t polydim_stiefel_retract_cuda_v26250(
    cublasHandle_t blas,
    cusolverDnHandle_t solver,
    const double* d_X,
    const double* d_Z,
    double* d_out,
    std::int64_t D,
    std::int64_t K,
    double step,
    void* d_workspace,
    std::size_t workspace_bytes,
    cudaStream_t stream
) {
    using namespace polydim_v26150;

    if (!d_X || !d_Z || !d_out || !d_workspace) {
        return POLYDIM_INVALID_ARGUMENT;
    }
    if (D < 1 || K < 1 || K > kMaxK || D < K || D > kMaxDimension) {
        return POLYDIM_RANGE_ERROR;
    }
    if (!std::isfinite(step)) {
        return POLYDIM_NONFINITE_INPUT;
    }

    int k = static_cast<int>(K);
    int r = 2 * k;

    // Minimum required layout in monolithic workspace:
    // U: [D, 2K] -> 2 * D * K * sizeof(double)
    // V: [D, 2K] -> 2 * D * K * sizeof(double)
    // G: [2K, 2K] -> 4 * K * K * sizeof(double)
    // B: [2K, K]  -> 2 * K * K * sizeof(double)
    // piv: [2K]   -> 2 * K * sizeof(int)
    // info: [1]   -> 1 * sizeof(int)
    std::size_t u_bytes    = static_cast<std::size_t>(2 * D * k) * sizeof(double);
    std::size_t v_bytes    = static_cast<std::size_t>(2 * D * k) * sizeof(double);
    std::size_t g_bytes    = static_cast<std::size_t>(r * r) * sizeof(double);
    std::size_t b_bytes    = static_cast<std::size_t>(r * k) * sizeof(double);
    std::size_t piv_bytes  = static_cast<std::size_t>(r) * sizeof(int);
    std::size_t info_bytes = sizeof(int);

    std::size_t static_needed = u_bytes + v_bytes + g_bytes + b_bytes + piv_bytes + info_bytes;
    if (workspace_bytes < static_needed) {
        return POLYDIM_RANGE_ERROR;
    }

    // Partition monolithic workspace
    std::uint8_t* raw_ws = static_cast<std::uint8_t*>(d_workspace);
    double* d_U = reinterpret_cast<double*>(raw_ws);
    double* d_V = reinterpret_cast<double*>(raw_ws + u_bytes);
    double* d_G = reinterpret_cast<double*>(raw_ws + u_bytes + v_bytes);
    double* d_B = reinterpret_cast<double*>(raw_ws + u_bytes + v_bytes + g_bytes);
    int* d_piv  = reinterpret_cast<int*>(raw_ws + u_bytes + v_bytes + g_bytes + b_bytes);
    int* d_info = reinterpret_cast<int*>(raw_ws + u_bytes + v_bytes + g_bytes + b_bytes + piv_bytes);

    void* d_solver_work = static_cast<void*>(raw_ws + static_needed);
    std::size_t solver_work_bytes = workspace_bytes - static_needed;

    // Stream binding
    if (blas)   cublasSetStream(blas, stream);
    if (solver) cusolverDnSetStream(solver, stream);

    // Step 1: Pack U = [Z, X] and V = [X, -Z]
    int threads = 256;
    int blocks = static_cast<int>((D + threads - 1) / threads);
    k_pack_uv<<<blocks, threads, 0, stream>>>(D, k, d_X, d_Z, d_U, d_V);
    CUDA_CHECK(cudaGetLastError());

    // Step 2: Compute G = V^T @ U (r x r) via cuBLAS gemm
    const double alpha_one = 1.0;
    const double beta_zero = 0.0;
    CUBLAS_CHECK(cublasDgemm(
        blas, CUBLAS_OP_T, CUBLAS_OP_N,
        r, r, static_cast<int>(D),
        &alpha_one, d_V, static_cast<int>(D),
        d_U, static_cast<int>(D),
        &beta_zero, d_G, r
    ));

    // Step 3: Compute B = V^T @ X (r x K) via cuBLAS gemm
    CUBLAS_CHECK(cublasDgemm(
        blas, CUBLAS_OP_T, CUBLAS_OP_N,
        r, k, static_cast<int>(D),
        &alpha_one, d_V, static_cast<int>(D),
        d_X, static_cast<int>(D),
        &beta_zero, d_B, r
    ));

    // Step 4: Form M = I_{2K} - (step / 2.0) * G in place
    dim3 block_2d(16, 16);
    dim3 grid_2d((r + 15) / 16, (r + 15) / 16);
    double half_tau = 0.5 * step;
    k_form_woodbury_system<<<grid_2d, block_2d, 0, stream>>>(r, half_tau, d_G);
    CUDA_CHECK(cudaGetLastError());

    // Step 5: Factor M (d_G) and Solve M @ W = B (d_B) via cuSOLVER LU
    CUSOLVER_CHECK(cusolverDnDgetrf(
        solver, r, r, d_G, r,
        static_cast<double*>(d_solver_work),
        d_piv, d_info
    ));

    CUSOLVER_CHECK(cusolverDnDgetrs(
        solver, CUBLAS_OP_N, r, k,
        d_G, r, d_piv, d_B, r, d_info
    ));

    // Step 6: Reconstruct R = X + step * U @ W (Wen-Yin Woodbury theorem: factor 2 cancels half_tau)
    // Copy X to d_out first
    CUDA_CHECK(cudaMemcpyAsync(d_out, d_X, static_cast<std::size_t>(D * k) * sizeof(double), cudaMemcpyDeviceToDevice, stream));

    // d_out = step * U @ W + 1.0 * d_out
    CUBLAS_CHECK(cublasDgemm(
        blas, CUBLAS_OP_N, CUBLAS_OP_N,
        static_cast<int>(D), k, r,
        &step, d_U, static_cast<int>(D),
        d_B, r,
        &alpha_one, d_out, static_cast<int>(D)
    ));

    return POLYDIM_OK;
}

// Backward compatibility symbol (reports missing workspace rather than empty stub)
POLYDIM_EXPORT std::int32_t polydim_stiefel_retract_cuda_v26150(
    const double* d_X,
    const double* d_Z,
    double* d_out,
    std::int64_t D,
    std::int64_t K,
    double step,
    cudaStream_t stream
) {
    // Fail-closed: V26150 signature lacks monolithic workspace pointer
    return polydim_v26150::POLYDIM_INVALID_ARGUMENT;
}
