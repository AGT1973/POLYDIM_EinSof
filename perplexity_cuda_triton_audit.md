Let \(r=2K\), \(X,Z\in\mathbb R^{D\times K}\), and define

\[
U=[Z\;\;X]\in\mathbb R^{D\times r},\qquad
V=[X\;\;-Z]\in\mathbb R^{D\times r}.
\]

Then

\[
UV^T=ZX^T-XZ^T=A,
\]

and \(A^T=-A\). Write \(\alpha=\tau/2\).

## 1. Cayley–Woodbury derivation

The Cayley equation is

\[
(I-\alpha A)R=(I+\alpha A)X.
\]

Using \(A=UV^T\),

\[
(I-\alpha UV^T)R=X+\alpha UV^TX.
\]

The Woodbury identity gives

\[
(I-\alpha UV^T)^{-1}
=
I+\alpha U(I-\alpha V^TU)^{-1}V^T.
\]

Therefore

\[
R
=
X+\alpha U(I-\alpha V^TU)^{-1}V^TX.
\]

Define \(W\in\mathbb R^{r\times K}\) by

\[
\boxed{
(I_r-\alpha V^TU)W=V^TX
}
\]

so that

\[
\boxed{
R_X(\tau Z)=X+\alpha UW.
}
\]

This is exact, not an approximation. The inner matrix is

\[
V^TU
=
\begin{bmatrix}
X^TZ & X^TX\\
-Z^TZ & -Z^TX
\end{bmatrix}
=
\begin{bmatrix}
X^TZ & I_K\\
-Z^TZ & -Z^TX
\end{bmatrix}
\]

when \(X^TX=I_K\).

The right-hand side is

\[
V^TX=
\begin{bmatrix}
X^TX\\
-Z^TX
\end{bmatrix}
=
\begin{bmatrix}
I_K\\
-Z^TX
\end{bmatrix}.
\]

No positive-definiteness assumption is required. Since \(A\) is real skew-symmetric, its eigenvalues are purely imaginary, so \(I-\alpha A\) is nonsingular for every real finite \(\tau\). Equivalently, the reduced system is nonsingular whenever the factorization is mathematically consistent.

## 2. Exact workspace contract

Assume double precision and column-major storage, as expected by cuBLAS and the dense cuSOLVER routines. cuBLAS uses column-major matrix semantics, and `cusolverDnDgetrs` consumes the pivot array produced by `getrf`.[3][7]

The mandatory persistent device buffers are:

| Buffer | Logical shape | Elements | Bytes |
|---|---:|---:|---:|
| \(U\) | \(D\times 2K\) | \(2DK\) | \(16DK\) |
| \(V\) | \(D\times 2K\) | \(2DK\) | \(16DK\) |
| \(G=V^TU\) | \(2K\times2K\) | \(4K^2\) | \(32K^2\) |
| \(B=V^TX\), later \(W\) | \(2K\times K\) | \(2K^2\) | \(16K^2\) |
| pivot array | \(2K\) integers | \(2K\) | \(8K\), if `int` |
| `devInfo` | scalar | 1 | 4 |

Thus, excluding \(U,V\), the mathematical workspace is

\[
\boxed{
(4K^2+2K^2)\cdot 8 + 8K+4
=
48K^2+8K+4\text{ bytes}
}
\]

for `double` matrices and 32-bit pivots.

If \(U\) and \(V\) are materialized in the pool, add

\[
\boxed{32DK\text{ bytes}}.
\]

If the implementation overwrites \(G\) with its LU factors and overwrites \(B\) with \(W\), no additional factor or solution buffers are required.

The cuSOLVER temporary workspace is implementation- and toolkit-dependent and must be queried, not guessed:

```cpp
int lwork = 0;
CUSOLVER_CHECK(cusolverDnDgetrf_bufferSize(
    solver, r, r, G, r, &lwork));
```

Allocate `lwork` doubles from the monolithic pool. The exact byte count is

```cpp
size_t solver_bytes = sizeof(double) * static_cast<size_t>(lwork);
```

The documented `getrf` implementation may use an \(r^2\)-scale workspace; the actual requirement must come from the installed cuSOLVER version.[6][8]

For \(K\le64\), \(r\le128\), so 32-bit dimensions are sufficient.

## 3. Certified cuBLAS/cuSOLVER orchestration

The following assumes:

- `X`, `Z`, and `R` are \(D\times K\), column-major;
- `U`, `V` are \(D\times 2K\);
- `G` is \(2K\times2K\);
- `B` is \(2K\times K\);
- `G` is overwritten by LU;
- `B` is overwritten by \(W\);
- all operations execute on one CUDA stream;
- every API return code and `devInfo` is checked.

### Exact C++ contract

```cpp
struct CayleyWorkspaceD {
    double* U;       // [D, 2K], column-major
    double* V;       // [D, 2K], column-major
    double* G;       // [2K, 2K], column-major; overwritten by LU
    double* B;       // [2K, K], column-major; overwritten by W
    double* solver_work;
    int*    piv;     // [2K]
    int*    info;    // scalar device memory
    int     lwork;   // number of doubles in solver_work
};

cudaError_t cayley_stiefel(
    cublasHandle_t blas,
    cusolverDnHandle_t solver,
    int64_t D,
    int K,
    double tau,
    const double* X,       // device, [D,K]
    const double* Z,       // device, [D,K]
    double* R,             // device, [D,K]
    CayleyWorkspaceD ws,
    cudaStream_t stream);
```

The construction of \(U,V\) can be performed by a fused packing kernel:

```cpp
__global__ void pack_uv(
    int64_t D, int K,
    const double* __restrict__ Z,
    const double* __restrict__ X,
    double* __restrict__ U,
    double* __restrict__ V);
```

For row \(i\) and \(0\le j<K\),

```text
U[i,j]   = Z[i,j]
U[i,j+K] = X[i,j]
V[i,j]   = X[i,j]
V[i,j+K] = -Z[i,j]
```

All indexing involving \(D\) should use `int64_t`; BLAS dimensions and leading dimensions remain `int` only where the library contract requires them.

### GEMM sequence

Set

\[
G\leftarrow V^TU.
\]

```cpp
const int r = 2 * K;
const double one  = 1.0;
const double zero = 0.0;
const double neg_alpha = -0.5 * tau;

CUBLAS_CHECK(cublasDgemm(
    blas,
    CUBLAS_OP_T, CUBLAS_OP_N,
    r, r, D,
    &one,
    V, D,
    U, D,
    &zero,
    ws.G, r));
```

Set

\[
B\leftarrow V^TX.
\]

```cpp
CUBLAS_CHECK(cublasDgemm(
    blas,
    CUBLAS_OP_T, CUBLAS_OP_N,
    r, K, D,
    &one,
    V, D,
    X, D,
    &zero,
    ws.B, r));
```

Transform \(G\) into

\[
M=I_r-\alpha G.
\]

A small custom kernel is preferable because it avoids an extra matrix allocation:

```cpp
__global__ void form_system(
    int r, double alpha, double* G)
{
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    int row = blockIdx.y * blockDim.y + threadIdx.y;

    if (row < r && col < r) {
        double gij = G[row + static_cast<size_t>(col) * r];
        G[row + static_cast<size_t>(col) * r] =
            (row == col ? 1.0 : 0.0) - alpha * gij;
    }
}
```

Then factor and solve:

```cpp
CUSOLVER_CHECK(cusolverDnDgetrf(
    solver,
    r, r,
    ws.G, r,
    ws.solver_work,
    ws.piv,
    ws.info));

CUSOLVER_CHECK(cusolverDnDgetrs(
    solver,
    CUBLAS_OP_N,
    r, K,
    ws.G, r,
    ws.piv,
    ws.B, r,
    ws.info));
```

The operation is \(MW=B\), so `CUBLAS_OP_N` is required. The factorization and solve APIs use the pivot output from `getrf`.[3]

Finally,

\[
R=X+\alpha UW.
\]

```cpp
CUBLAS_CHECK(cublasDgemm(
    blas,
    CUBLAS_OP_N, CUBLAS_OP_N,
    D, K, r,
    &alpha,
    ws.U, D,
    ws.B, r,
    &one,
    R, D));
```

For strict error handling, copy `info` to host only after the relevant stream work has completed, or use an asynchronous status mechanism. A nonzero `info` indicates a singular or otherwise failed factorization/solve.

### Aliasing contract

The following aliasing is safe:

- `G` may be overwritten by LU after both GEMMs complete.
- `B` may be overwritten by `getrs`.
- `R` may alias neither `U` nor `V` unless the final GEMM is specially staged.
- `X` and `Z` must remain valid through construction of \(U,V\) and the two reductions.
- `B` must not alias `X`, `Z`, or `U`.

## 4. Complexity

The two tall-skinny products cost

\[
V^TU:\quad O(D(2K)^2)=O(DK^2),
\]

\[
V^TX:\quad O(D(2K)K)=O(DK^2).
\]

The final product costs

\[
UW:\quad O(D(2K)K)=O(DK^2).
\]

The reduced LU factorization costs

\[
O((2K)^3)=O(K^3),
\]

and the \(K\) right-hand-side solve costs \(O(K^3)\). Hence

\[
\boxed{
T=O(DK^2+K^3)
}
\]

with storage

\[
\boxed{
O(DK+K^2)
}
\]

when \(U,V\) are materialized. Since \(D\gg K\), the tall-skinny GEMMs dominate.

A fused implementation can avoid materializing \(U,V\), but then the corresponding kernels must generate the block columns of \(U,V\) on demand. The mathematical workspace falls to the \(O(K^2)\) quantities, at the cost of custom reduction kernels.

## 5. Why the Lyapunov elementwise solve was invalid

The Cayley problem is a linear system involving the skew-symmetric operator \(A\):

\[
(I-\alpha A)R=(I+\alpha A)X.
\]

It is not a Lyapunov equation of the form

\[
LX+XL^T=Q.
\]

For a real skew-symmetric \(A\),

\[
\lambda_j(A)\in i\mathbb R,
\]

not \(\mathbb R_{>0}\). Any elementwise denominator derived from a diagonal or eigenbasis assumption, such as

\[
\lambda_i+\lambda_j
\quad\text{or}\quad
1-\alpha\lambda_i,
\]

cannot be treated as a strictly positive real scalar in the original coordinate basis. The denominator test

```text
denom > 1e-15
```

therefore rejects valid modes, accepts an invalid spectral model, or both.

There are three distinct errors in that formulation:

- The Cayley operator is \(I-\alpha A\), not a positive Lyapunov operator.
- \(A\) is generally not diagonal in the computational basis.
- Real skew-symmetric matrices have imaginary conjugate eigenpairs, so “positive eigenvalue” logic is inapplicable.

The correct robustness condition is nonsingularity of \(I-\alpha A\). For real \(\alpha\),

\[
x^T(I-\alpha A)x=x^Tx
\]

because \(x^TAx=0\). In fact,

\[
\|(I-\alpha A)x\|_2^2
=
\|x\|_2^2+\alpha^2\|Ax\|_2^2
\ge \|x\|_2^2,
\]

so the operator has smallest singular value at least \(1\). The reduced Woodbury system inherits nonsingularity from the determinant identity

\[
\det(I-\alpha UV^T)
=
\det(I-\alpha V^TU).
\]

## 6. Stiefel invariance

Let

\[
Q(\alpha)=(I-\alpha A)^{-1}(I+\alpha A).
\]

Since \(A^T=-A\),

\[
Q(\alpha)^TQ(\alpha)=I.
\]

Therefore

\[
R^TR
=
X^TQ(\alpha)^TQ(\alpha)X
=
X^TX
=
I_K.
\]

Thus the exact Cayley transform preserves the Stiefel constraint up to floating-point error. A production implementation should optionally report

\[
\|R^TR-I_K\|_F
\]

and, if required by the algorithm, apply a separate re-orthogonalization policy.

## 7. Triton determinism

A floating-point sum is not associative:

\[
(a+b)+c\ne a+(b+c)
\]

in IEEE-754 arithmetic because each addition rounds. `tl.atomic_add` permits multiple program instances to update the same destination in an order determined by scheduling, warp issue, memory contention, and hardware execution. Consequently, two executions can produce different rounding paths and different low bits. Atomics provide update atomicity, not a canonical summation order.[1]

For bit-exact reproducibility, use a fixed reduction tree.

### Two-pass contract

Pass 1: each program instance owns a deterministic contiguous tile and computes a local reduction:

\[
s_b=\operatorname{reduce}_{j\in\mathcal T_b} a_j
\]

using a fixed `tl.sum` tree. Store one partial per block.

Pass 2: launch a single-program or otherwise deterministically partitioned reduction over the partial array:

\[
s=\operatorname{reduce}_{b=0}^{B-1}s_b.
\]

No inter-block atomic accumulation is used. The launch geometry, tile size, reduction axis, and accumulation dtype must remain fixed. If inputs are `float32`, accumulation in `float64` improves accuracy but does not make an alternative reduction tree bit-identical to the reference tree.

For a matrix \(X\in\mathbb R^{D\times K}\), a deterministic inner-product kernel can use one logical output per \((p,q)\) pair and reduce the \(D\) dimension in fixed blocks. Projection quantities such as

\[
X^TZ,\qquad Z^TZ
\]

then require \(O(K^2)\) outputs, each formed by a fixed two-pass reduction.

A representative Triton signature is:

```python
@triton.jit
def dot_pass1(
    x_ptr, y_ptr, partial_ptr,
    N, stride_x, stride_y, stride_partial,
    BLOCK_SIZE: tl.constexpr,
):
    ...
```

```python
@triton.jit
def dot_pass2(
    partial_ptr, out_ptr,
    NUM_PARTIALS,
    stride_partial,
    BLOCK_SIZE: tl.constexpr,
):
    ...
```

For \(K\le64\), the second pass is small and can often be executed by one program instance per output scalar.

## 8. Triton OOB masking contract

For a one-dimensional tile,

```python
offs = pid * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
mask = offs < N
x = tl.load(x_ptr + offs, mask=mask, other=0.0)
```

Every load that may address a partial tile must carry the mask. The neutral value must be zero for sums and dot products.

Stores must also be masked:

```python
tl.store(out_ptr + offs, values, mask=mask)
```

A complete representative kernel is:

```python
import triton
import triton.language as tl


@triton.jit
def dot_partial_kernel(
    x_ptr, y_ptr, partial_ptr,
    N,
    BLOCK_SIZE: tl.constexpr,
):
    pid = tl.program_id(0)
    offs = pid * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
    mask = offs < N

    x = tl.load(x_ptr + offs, mask=mask, other=0.0)
    y = tl.load(y_ptr + offs, mask=mask, other=0.0)

    # Fixed local reduction tree for this program instance.
    s = tl.sum(x * y, axis=0)

    tl.store(partial_ptr + pid, s)
```

The final reduction must bound every partial load:

```python
@triton.jit
def dot_finalize_kernel(
    partial_ptr, out_ptr,
    NUM_PARTIALS,
    BLOCK_SIZE: tl.constexpr,
):
    offs = tl.arange(0, BLOCK_SIZE)
    mask = offs < NUM_PARTIALS

    p = tl.load(partial_ptr + offs, mask=mask, other=0.0)
    total = tl.sum(p, axis=0)

    # Exactly one scalar is written.
    if tl.program_id(0) == 0:
        tl.store(out_ptr, total)
```

For a strided matrix tile, the same rule applies independently:

```python
rows = row_pid * BLOCK_M + tl.arange(0, BLOCK_M)
cols = col_pid * BLOCK_N + tl.arange(0, BLOCK_N)

mask = (rows[:, None] < D) & (cols[None, :] < K)

x = tl.load(
    x_ptr + rows[:, None] * stride_x0 + cols[None, :] * stride_x1,
    mask=mask,
    other=0.0,
)

tl.store(
    out_ptr + rows[:, None] * stride_o0 + cols[None, :] * stride_o1,
    out,
    mask=mask,
)
```

Never rely on padding, allocation size, or launch geometry to make an unmasked address safe. When \(D\not\equiv0\pmod{\text{BLOCK\_SIZE}}\), the final tile necessarily contains lanes with `offs >= D`; those lanes must be masked on both load and store. Triton exposes masked `load`, `store`, reductions, and atomic operations as separate language primitives.[1]

The complete hardened design is therefore:

\[
\boxed{
\text{deterministic fixed-tree reductions}
+
\text{masked every potentially partial memory operation}
+
\text{small dense Woodbury solve}
}
\]

with total Cayley complexity \(O(DK^2+K^3)\), no dynamic device allocation, and a workspace contract that can be satisfied entirely from a preallocated monolithic pool.