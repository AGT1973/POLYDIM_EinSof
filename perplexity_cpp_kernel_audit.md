**Verdict:** the proposed architecture is directionally correct, but the numerical claims require qualification. Eight-way partitioning preserves compensated-summation stability only if each lane is a genuine Neumaier accumulator and the final reduction is performed with a correctly ordered, non-overlapping treatment of the lane residuals. The tangency fix must be scale-aware; neither proposed absolute floor is universally rigorous.

## 1. Eight-way Neumaier accumulation

Let

\[
s=\sum_{i=1}^{n}x_i,\qquad
A=\sum_{i=1}^{n}|x_i|,\qquad
\kappa=\frac{A}{|s|}.
\]

\(\kappa\) is the intrinsic condition number of summation: it is independent of the algorithm and becomes arbitrarily large near cancellation.[1][7]

For a correctly implemented Neumaier accumulator, a representative bound is

\[
|\widehat{s}-s|
\le
u|s|+\left(0.75n^2+n\right)u^2A,
\qquad 3nu\le 1,
\]

where \(u\) is unit roundoff.[10] Thus

\[
\frac{|\widehat{s}-s|}{|s|}
\le
u+\left(0.75n^2+n\right)u^2\kappa .
\]

Therefore, the statement “\(O(u)+O(nu^2)\)” is an acceptable asymptotic summary only under a specific error model and with constants suppressed; rigorous bounds generally contain an \(n^2u^2\) term for the standard algorithmic analysis.[10]

### Eight lanes

Partition the terms into \(p=8\) subsequences \(I_k\), and compute

\[
s_k=\sum_{i\in I_k}x_i,\qquad
A_k=\sum_{i\in I_k}|x_i|.
\]

If each lane has length \(m_k\), then its compensated error satisfies approximately

\[
|e_k|
\lesssim
u|s_k|+C m_k^2u^2A_k.
\]

The final reduction must then add the **lane estimates and their corrections**. If the resulting sequence has \(16\) quantities,

\[
(s_0,c_0,s_1,c_1,\ldots,s_7,c_7),
\]

and these are accumulated by Neumaier, then a safe bound has the form

\[
|\widehat{s}-s|
\lesssim
\sum_{k=0}^{7}|e_k|
+
u|s|
+
C(16)^2u^2
\left(
\sum_{k=0}^{7}|s_k|+\sum_{k=0}^{7}|c_k|
\right).
\]

Since

\[
\sum_k A_k=A,
\]

and \(m_k\approx n/8\), the lane-local second-order contribution is approximately

\[
8\left(\frac{n}{8}\right)^2u^2A
=
\frac{n^2u^2A}{8},
\]

rather than the scalar \(n^2u^2A\), while the final reduction contributes only a fixed-size \(O(u^2A)\) term. Thus the eight-way algorithm remains compensated and asymptotically stable; it does **not**, however, have exactly the same rounding path or bitwise result as scalar Neumaier.

The robust conclusion is

\[
|\widehat{s}-s|
\le
C_1u|s|+C_2(n^2+1)u^2A,
\]

and hence

\[
\frac{|\widehat{s}-s|}{|s|}
\le
C_1u+C_2(n^2+1)u^2\kappa.
\]

For fixed \(n\) and \(\kappa\), this is \(O(u)\). For highly ill-conditioned cancellation, no summation algorithm can guarantee a small relative error because \(\kappa\) itself is large.[1][4]

### Required correction to the proposed cascade

The cascade

```cpp
neumaier_accumulate(sum[k],  total_sum, total_comp);
neumaier_accumulate(comp[k], total_sum, total_comp);
```

is numerically defensible **only if**:

1. `comp[k]` is treated as an independently rounded residual, not as an exact correction.
2. The accumulator accepts signed values and uses the magnitude comparison required by Neumaier:
   \[
   \text{if } |s|\ge |x|,\quad
   c\mathrel{+}= (s-s_{\rm new})+x;
   \]
   otherwise
   \[
   c\mathrel{+}= (x-s_{\rm new})+s.
   \]
3. The final value is
   \[
   \widehat{s}= \operatorname{fl}(total\_sum+total\_comp).
   \]
4. The lane processing order is deterministic if reproducibility is required.
5. Overflow, underflow, NaNs, and infinities are handled explicitly.

A stronger design is to combine each lane as an expansion \((s_k,c_k)\) using an error-free transformation or a dedicated compensated pairwise reduction, rather than pretending the correction terms are ordinary data. The proposed method is stable, but “preserves the exact scalar-Neumaier bound” is too strong.

## 2. OpenMP logical reduction

The construct

```cpp
bool has_nan = false;

#pragma omp parallel for reduction(||:has_nan)
for (std::int64_t i = 0; i < n; ++i) {
    double res = ...;
    if (!std::isfinite(res))
        has_nan = true;
}
```

is OpenMP-conforming for a scalar logical variable: `||` is a standard reduction operator, and the reduction variable must be a scalar arithmetic type.[3][5][8] The logical reduction is preferable to a shared flag because each thread updates a private copy and OpenMP combines the copies without a data race.

Use a scalar `int` rather than relying on implementation details of `bool` if maximum portability across compiler versions is required:

```cpp
int invalid = 0;

#pragma omp parallel for reduction(|:invalid)
for (...) {
    const double y = ...;
    invalid |= !std::isfinite(y);
}
```

For the exact requested form, `reduction(||:has_nan)` is standard. Compiler support still depends on enabling OpenMP correctly: GCC and Clang require their OpenMP runtime/toolchain configuration, while MSVC supports the standard scalar reduction syntax but has more limited OpenMP feature coverage than GCC/Clang.[2][3][5]

The finite test must cover every value whose invalidity matters, including the norm, denominator, tangent coefficient, and every normalized output. A reduction flag detects invalid values; it does not prevent propagation of an earlier NaN unless the computation explicitly guards against it.

## 3. Relative tangency tolerance on \(S^{D-1}\)

For a unit sphere and tangent vector \(v\), the exact condition is

\[
x^\top v=0,\qquad \|x\|_2=1.
\]

The geometrically meaningful defect is the normalized residual

\[
\rho(x,v)
=
\frac{|x^\top v|}
{\|x\|_2\|v\|_2}.
\]

For normalized \(x\),

\[
\rho(x,v)=\frac{|x^\top v|}{\|v\|_2}.
\]

A scale-invariant relative tangency test is therefore

\[
|x^\top v|
\le
\tau_{\rm rel}\,\|x\|_2\|v\|_2
+
\tau_{\rm abs}\,\|x\|_2\,s_v,
\]

where \(s_v\) is a problem-defined scale for the vector family. If \(v\) is known to be nonzero and not subnormal, use

\[
|x^\top v|
\le
\tau_{\rm rel}\,\|v\|_2.
\]

The original test

\[
|x^\top v|\le \tau\max(1,\|v\|)
\]

is not relative for \(\|v\|\ll1\): it imposes an absolute tolerance of approximately \(\tau\), so the admissible angular defect can be

\[
\frac{|x^\top v|}{\|v\|}
\lesssim \frac{\tau}{\|v\|},
\]

which diverges as \(\|v\|\to0\).

The proposed replacement

\[
\tau(\|v\|+\delta)
\]

is scale-aware only when \(\delta\) is justified by a specified absolute error model. Likewise,

\[
\max(10^{-15},\tau\|v\|)
\]

introduces an absolute floor that can still permit a relative defect of

\[
\frac{10^{-15}}{\|v\|},
\]

which is unbounded for infinitesimal \(v\). It is therefore not a rigorous relative criterion.

For floating-point computation, use a two-regime test:

\[
|\,\operatorname{fl}(x^\top v)\,|
\le
\tau_{\rm rel}\|x\|_2\|v\|_2
+
\gamma_D\,\|x\|_\infty\|v\|_1,
\]

where

\[
\gamma_D=\frac{Du}{1-Du},
\qquad Du<1.
\]

This accounts for dot-product rounding. For \(D=10^7\) in binary64,

\[
Du\approx 1.11\times10^{-9},
\]

so the dimensional accumulation term is not negligible. A compensated or pairwise dot product reduces the practical constant and growth rate, but the tolerance must still include the implemented reduction error.

For \(\|v\|\) below a declared scale threshold \(v_{\min}\), relative tangency is mathematically ill-conditioned and should not be asserted. The correct policy is:

\[
\|v\|<v_{\min}
\quad\Longrightarrow\quad
\text{classify as zero/degenerate direction, not “tangent”.}
\]

## Final verification verdict

- **Eight-way Neumaier:** valid and SIMD-friendly; preserves compensated \(O(u)\)-type behavior for fixed condition number, but the rigorous bound is of the form \(O(u|s|)+O(n^2u^2A)\), not unconditionally \(O(u)+O(nu^2)\).
- **Condition number:** unchanged intrinsically:
  \[
  \kappa=\frac{\sum|x_i|}{|\sum x_i|}.
  \]
  The eight-way scheme changes algorithmic rounding constants, not the problem conditioning.
- **Cascaded lane combination:** sound if lane corrections are accumulated with a correct Neumaier implementation and the final result is `total_sum + total_comp`.
- **OpenMP flag:** `reduction(||:has_nan)` is conforming for a scalar logical reduction; it removes the race.
- **Tangency tolerance:** use normalized residual
  \[
  |x^\top v|/(\|x\|\|v\|)
  \]
  with a floating-point error allowance. Neither an unconditional `max(1, ||v||)` nor an arbitrary absolute floor is a rigorous relative criterion for infinitesimal vectors.