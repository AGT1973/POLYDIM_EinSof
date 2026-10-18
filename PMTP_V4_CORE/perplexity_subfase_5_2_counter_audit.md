# CONTRA-AUDITORÍA PERPLEXITY SONAR-PRO: RESOLUCIÓN DEFINITIVA CAYLEY & KULISCH

The previous reviewer was wrong about **Problem 1**: for the unscaled Cayley curve with a fixed skew-symmetric generator \(A\), there is no periodic oscillation. Its eigenphases approach \(\pm\pi\), and the matrix has the real limit \(2P_{\ker A}-I\). The main correction concerns **Problem 2**: \(4288\) bits is a conventional Kulisch size for a particular accumulator design, but it is not the minimal width for every interpretation of “exactly accumulate \(2^{64}\) binary64 products.” The required width depends on whether subnormals, infinities/NaNs, signed cancellation, and a final carry/overflow bit are included.

## 1. Cayley asymptotic limit

Let \(A\in\mathbb R^{m\times m}\) satisfy \(A^{T}=-A\), and define

\[
C(t)=(I-\tfrac t2A)^{-1}(I+\tfrac t2A),\qquad t\ge 0.
\]

Since the eigenvalues of \(A\) are \(0\) and pairs \(\pm i\lambda_j\), \(\lambda_j>0\), \(I-\tfrac t2A\) is invertible for every real \(t\).

For an eigenvector \(v\) satisfying \(Av=i\lambda v\),

\[
C(t)v
=
\frac{1+\frac i2t\lambda}{1-\frac i2t\lambda}v.
\]

Put \(x=\tfrac12t\lambda\). Then

\[
c(x)=\frac{1+ix}{1-ix}
=\frac{(1+ix)^2}{1+x^2}
=
\frac{1-x^2}{1+x^2}
+i\frac{2x}{1+x^2}.
\]

Therefore

\[
c(x)=e^{\,2i\arctan x}.
\]

For \(\lambda>0\), \(x\to+\infty\), so

\[
2\arctan x\longrightarrow\pi,
\qquad
c(x)\longrightarrow e^{i\pi}=-1.
\]

For the conjugate eigenvalue \(-i\lambda\),

\[
\frac{1-\frac i2t\lambda}{1+\frac i2t\lambda}
=e^{-2i\arctan(\frac12t\lambda)}
\longrightarrow e^{-i\pi}=-1.
\]

Thus the answer to the scalar question is unequivocally

\[
\boxed{\displaystyle
\lim_{t\to+\infty}
\frac{1+\frac i2t\lambda}{1-\frac i2t\lambda}
=-1
}.
\]

There is no oscillation. The phase is

\[
\theta(t)=2\arctan(\tfrac12t\lambda),
\]

which increases monotonically from \(0\) to \(\pi\) when \(\lambda>0\). The modulus is identically one. This differs fundamentally from the exponential flow \(e^{tA}\), whose nonzero spectral modes are \(e^{\pm i\lambda t}\) and genuinely rotate forever.

### Definitive matrix theorem

Let \(P_0\) denote the orthogonal projector onto \(\ker A\). Then

\[
\boxed{\displaystyle
\lim_{t\to+\infty}
(I-\tfrac t2A)^{-1}(I+\tfrac t2A)
=
2P_0-I
}.
\]

Because \(A\) is real skew-symmetric,

\[
\mathbb R^m=\ker A\oplus\operatorname{range}(A)
\]

orthogonally, and

\[
P_{\operatorname{range}(A)}=I-P_0.
\]

On \(\ker A\), \(C(t)\) is exactly the identity. On every two-dimensional invariant rotation plane corresponding to \(\lambda_j\), its matrix is

\[
\begin{pmatrix}
\frac{1-x_j^2}{1+x_j^2} & -\frac{2x_j}{1+x_j^2}\\
\frac{2x_j}{1+x_j^2} & \frac{1-x_j^2}{1+x_j^2}
\end{pmatrix},
\qquad x_j=\frac{t\lambda_j}{2},
\]

which converges to \(-I_2\). Consequently,

\[
C(t)\longrightarrow I_{\ker A}\oplus(-I_{\operatorname{range}(A)})
=P_0-(I-P_0)
=2P_0-I.
\]

An equivalent algebraic proof uses the spectral decomposition of the real skew-symmetric matrix. Since every nonzero eigenvalue of \(A\) has the form \(\pm i\lambda_j\), the scalar rational function

\[
r_t(z)=\frac{1+\frac t2z}{1-\frac t2z}
\]

satisfies

\[
r_t(0)=1,\qquad
r_t(\pm i\lambda_j)\to -1.
\]

Functional calculus then gives the stated projector limit.

The convergence is even \(O(t^{-1})\) on \(\operatorname{range}(A)\). Indeed,

\[
\frac{1+ix}{1-ix}+1=\frac{2}{1-ix},
\]

so

\[
\left|
\frac{1+ix}{1-ix}+1
\right|
=
\frac{2}{\sqrt{1+x^2}}
=O(x^{-1}).
\]

If \(A\) has smallest positive singular value \(\sigma_{\min}^+(A)\), then

\[
\|C(t)-(2P_0-I)\|_2
\le
\frac{4}{t\,\sigma_{\min}^+(A)}
\]

for \(t>0\), up to the exact choice of norm bound.

### Why the oscillation claim is false

The claim confuses two different maps:

\[
e^{tA}
\quad\text{versus}\quad
(I-\tfrac t2A)^{-1}(I+\tfrac t2A).
\]

For \(e^{tA}\), the spectral factors are

\[
e^{\pm i\lambda t},
\]

which are periodic and generally have no limit.

For the Cayley map, the factors are

\[
\frac{1\pm i\lambda t/2}{1\mp i\lambda t/2}
=
e^{\pm2i\arctan(\lambda t/2)}.
\]

The phase is bounded and monotone, not linear in \(t\). It approaches the endpoint \(\pm\pi\), where both conjugate factors converge to the same real value \(-1\).

The theorem assumes:

- \(A\) is fixed as \(t\to+\infty\);
- \(A\) is finite-dimensional and real skew-symmetric;
- \(t\) approaches \(+\infty\) along the real line.

It does not assert numerical stability of directly forming the formula for extremely large \(t\).

## 2. Numerical behavior for large \(t\)

Mathematically, the limit is benign. Numerically, direct evaluation can be poor because the terms \(I\pm \tfrac t2A\) become badly scaled, and solving the associated linear system can lose relative accuracy in the limiting regime. The issue is conditioning and representation, not mathematical oscillation.

Useful alternatives are:

- **Polar retraction:** compute \(Y=X+Z\), then orthogonalize by
  \[
  R_X(Z)=Y(Y^TY)^{-1/2}.
  \]
  A stable implementation uses a QR or polar-decomposition algorithm rather than explicitly forming the inverse square root.

- **QR retraction:** compute a thin QR factorization
  \[
  X+Z=QR,
  \]
  and choose the signs of \(R\)'s diagonal consistently. This is usually the most robust general-purpose choice.

- **Householder products:** represent the orthogonal transformation by Householder reflectors. This avoids a large ill-scaled solve and is attractive when structured transformations or rank updates are available.

- **Scaled Cayley evaluation:** replace \(A\) by a scaled matrix \(B=\alpha A\), with \(\alpha\) chosen so that \(\|\alpha tA\|\) remains moderate, and evaluate the transform using a stable linear solve or Schur form.

- **Schur/block evaluation:** reduce \(A\) orthogonally to \(2\times2\) skew blocks and apply the scalar formula to each block. This is particularly transparent and avoids cancellation in a dense global formula.

- **Asymptotic switching:** when \(t\sigma_{\min}^+(A)\) is large, use
  \[
  C(t)\approx 2P_{\ker A}-I
  \]
  together with a controlled \(O(t^{-1})\) error bound.

- **Avoid explicit Sherman–Morrison–Woodbury formulas** when the low-rank update is nearly singular after scaling. Use QR, Householder QR, or a backward-stable solve instead.

A “Cayley–Padé” method is meaningful only if the Padé approximation is evaluated stably. The \([1/1]\) Padé approximant to \(e^{tA}\) is exactly the Cayley expression, so changing the name does not remove large-scale numerical issues. Higher-order rational approximants can improve accuracy for exponential propagation, but they do not alter the exact asymptotic theorem above.

## 3. Binary64 facts needed for a Kulisch accumulator

Assume finite IEEE-754 binary64 inputs and exact real multiplication.

Binary64 has:

- sign bit: \(1\);
- exponent field: \(11\) bits;
- precision: \(p=53\) significand bits for normal numbers;
- unbiased normal exponent range:
  \[
  e\in[-1022,1023];
  \]
- minimum positive subnormal:
  \[
  2^{-1074};
  \]
- minimum positive normal:
  \[
  2^{-1022};
  \]
- maximum finite value:
  \[
  (2-2^{-52})2^{1023}
  =(2^{53}-1)2^{971}.
  \]

Every finite binary64 number can be written as

\[
x=s\,M\,2^{-1074},
\]

where \(s\in\{-1,0,1\}\) and \(M\) is an integer satisfying

\[
0\le M\le (2^{53}-1)2^{2097}.
\]

For a product \(xy\),

\[
xy=s_xs_y\,M_xM_y\,2^{-2148}.
\]

The exact product has at most \(106\) significant binary bits, although its normalized exponent range is more conveniently described as follows:

- minimum positive nonzero product:
  \[
  2^{-2148};
  \]
- maximum finite product:
  \[
  \bigl((2^{53}-1)2^{971}\bigr)^2
  <2^{2048}.
  \]

Thus all finite binary64 products lie in the half-open magnitude range

\[
2^{-2148}\le |xy|<2^{2048}.
\]

The product lattice has spacing \(2^{-2148}\). Therefore a fixed-point accumulator that represents products exactly must use units of \(2^{-2148}\).

## 4. Width for a sum of \(N=2^{64}\) products

Let

\[
S=\sum_{j=1}^{N}x_jy_j,
\qquad N=2^{64}.
\]

A magnitude bound is

\[
|S|
<
N\,2^{2048}
=
2^{64}2^{2048}
=
2^{2112}.
\]

Since the smallest product quantum is \(2^{-2148}\), the scaled integer

\[
K=2^{2148}S
\]

satisfies, in magnitude,

\[
|K|<2^{2112+2148}=2^{4260}.
\]

Therefore:

- \(4260\) magnitude bits suffice to represent nonnegative values strictly below \(2^{4260}\);
- a signed two’s-complement register needs \(4261\) bits to represent every integer in
  \[
  [-2^{4260},2^{4260}-1].
  \]

This gives the mathematically minimal signed width under the assumptions:

1. all inputs are finite;
2. products are exact;
3. at most \(2^{64}\) products are accumulated;
4. the accumulator is a signed fixed-point integer with unit \(2^{-2148}\);
5. the bound \(<2^{2048}\) for an individual product is used;
6. no extra design guard bits are required.

Hence the core exact-width result is

\[
\boxed{4261\text{ signed bits}}
\]

for the broad worst-case sum bound, with \(4260\) fractional-scale/magnitude positions and one sign/carry position.

There is a subtle endpoint issue. The largest binary64 value is strictly less than \(2^{1024}\), so an individual product is strictly less than \(2^{2048}\), and a sum of \(2^{64}\) such products is strictly less than \(2^{2112}\). That strict inequality is why \(4261\), rather than \(4262\), signed bits suffice in the conventional two’s-complement interpretation.

## 5. Where 4196, 4224, 4258, 4261, and 4288 come from

The frequently cited \(4196\)-bit figure is

\[
4196=2(1023)+2(53)+2(1022).
\]

It corresponds to covering the full binary64 dynamic range in a product-oriented fixed-point layout, but it does **not** include the additional \(64\) bits needed for summing \(2^{64}\) terms.

Adding those \(64\) growth bits gives

\[
4196+64=4260.
\]

A signed representation then commonly requires one additional sign/carry bit:

\[
4260+1=4261.
\]

Thus:

\[
\boxed{4196\text{ bits}}
\]

is a product-range accumulator width under one convention;

\[
\boxed{4260\text{ bits}}
\]

is the corresponding unsigned magnitude width after allowing \(2^{64}\)-term growth;

\[
\boxed{4261\text{ bits}}
\]

is the natural minimal signed fixed-point width.

The value \(4224\) is \(66\) words of \(64\) bits and is therefore a convenient rounded implementation width near, but below, \(4261\); it cannot represent the full worst-case exact sum under the assumptions above.

The value \(4258\) can arise from a different endpoint or sign convention, for example by omitting one or more extreme bits or using a non-two’s-complement sign-magnitude layout. It is not the canonical worst-case signed width for all finite binary64 products and \(2^{64}\) summands.

The value \(4288\) is

\[
4288=67\cdot64
\]

and is the traditional Kulisch accumulator size cited in the literature for binary64 products.[2][3] A standard derivation is

\[
4288
=
4196+92.
\]

The additional \(92\) bits are a design margin: \(64\) bits for the maximum number of accumulated terms plus approximately \(28\) further bits for implementation guard space, carry handling, or a conservative register layout. One published formulation explicitly gives the decomposition \(L=k+4196\) with \(k=92\), yielding \(L=4288\).[8] Other literature reports \(4196\) as the range-covering length and \(4288\) as the enlarged practical Kulisch register.[4][6]

Therefore, the uncompromising conclusion is:

\[
\boxed{
4288\text{ bits is a conventional conservative Kulisch design width, not a uniquely forced mathematical minimum.}
}
\]

For exact accumulation of \(2^{64}\) finite binary64 products, the clean mathematical minimum is

\[
\boxed{4261\text{ signed bits}}
\]

under the fixed-point model stated above. A \(4288\)-bit implementation is safe and convenient because it rounds to \(67\) 64-bit words and includes substantial margin.

## 6. Recommended Lean-ready theorem statements

A suitable abstract theorem should separate the floating-point encoding from the accumulator arithmetic.

### Product-lattice lemma

Define the scaled integer representation of every finite binary64 value by

\[
\operatorname{enc}(x)=x\,2^{1074}\in\mathbb Z.
\]

Then for finite binary64 \(x,y\),

\[
xy\,2^{2148}
=
\operatorname{enc}(x)\operatorname{enc}(y)\in\mathbb Z.
\]

A Lean-style statement is:

```lean
theorem binary64_product_is_integer
    (x y : ℝ)
    (hx : IsFiniteBinary64 x)
    (hy : IsFiniteBinary64 y) :
    ∃ k : ℤ, x * y = (k : ℝ) * 2 ^ (-2148 : ℤ)
```

The stronger magnitude lemma is:

```lean
theorem binary64_product_bound
    (x y : ℝ)
    (hx : IsFiniteBinary64 x)
    (hy : IsFiniteBinary64 y) :
    |x * y| < 2 ^ (2048 : ℤ)
```

### \(2^{64}\)-term accumulation lemma

```lean
theorem binary64_sum_bound
    (N : ℕ)
    (hN : N ≤ 2 ^ 64)
    (x : Fin N → ℝ)
    (y : Fin N → ℝ)
    (hx : ∀ i, IsFiniteBinary64 (x i))
    (hy : ∀ i, IsFiniteBinary64 (y i)) :
    |∑ i, x i * y i| < 2 ^ (2112 : ℤ)
```

The exact scaled-integer form is:

```lean
theorem binary64_sum_scaled_integer
    (N : ℕ)
    (x y : Fin N → ℝ)
    (hx : ∀ i, IsFiniteBinary64 (x i))
    (hy : ∀ i, IsFiniteBinary64 (y i)) :
    ∃ K : ℤ,
      (∑ i, x i * y i) = (K : ℝ) * 2 ^ (-2148 : ℤ)
```

For \(N\le 2^{64}\), the bound is

```lean
theorem binary64_sum_scaled_bound
    (N : ℕ)
    (hN : N ≤ 2 ^ 64)
    ... :
    |K| < 2 ^ (4260 : ℕ)
```

Finally, the signed-width representability theorem is:

```lean
theorem exact_accumulator_width_4261
    (K : ℤ)
    (hK : |K| < 2 ^ 4260) :
    ∃ z : Int4261, z = K
```

Here `Int4261` should be defined as the signed integer interval

\[
[-2^{4260},\,2^{4260}-1].
\]

If the implementation uses a \(4288\)-bit unsigned word array, the formal theorem should instead prove an embedding

\[
\operatorname{Int}_{4261}\hookrightarrow \operatorname{Word}_{4288},
\]

with the remaining \(27\) bits treated as explicit zero/sign-extension margin.

## Final arbitration

- **Problem 1:** the Cayley transform does converge:
  \[
  \lim_{t\to+\infty}C(t)=2P_{\ker A}-I.
  \]
  The oscillation objection applies to \(e^{tA}\), not to the Cayley rational transform.

- **Problem 2:** \(4288\) bits is a legitimate conservative Kulisch implementation width and is documented as such.[2][3][8] But under a precise fixed-point model for at most \(2^{64}\) finite binary64 products, the mathematically minimal signed width is \(4261\) bits; \(4196\) covers the product range before term-count growth, and \(4260\) is the corresponding unsigned magnitude count.

- **Formalization requirement:** Lean must state explicitly whether it models finite values only, whether infinities and NaNs are excluded, whether the accumulator is signed or unsigned, whether the bound is strict, and whether extra guard/carry bits are part of the representation. Without those declarations, “the exact Kulisch width” is not a well-posed single number.