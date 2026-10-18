# AUDITORÍA PERPLEXITY SONAR-PRO: SUBFASE 5.2 (LEAN 4 FORMAL VERIFICATION)

The three formulations are not equally admissible. **Formulation 1 is essentially correct after fixing conventions; Formulation 2 has a serious algebraic error in the stated asymptotic limit; Formulation 3 cites a real 4288-bit engineering bound but does not prove it with the displayed arithmetic, and the claim as stated needs substantial qualification.**

## 1. Grassmann quotient and chordal projection metric

Let
\[
\operatorname{St}(K,D)
=
\{X\in\mathbb R^{D\times K}:X^{\mathsf T}X=I_K\},
\]
with \(K\le D\), and let \(O(K)\) act on the right by \(X\mapsto XQ\). Then
\[
\operatorname{Gr}(K,D)\cong \operatorname{St}(K,D)/O(K)
\]
is the standard quotient realization of the real Grassmann manifold.

For \(X\in\operatorname{St}(K,D)\), define
\[
\Pi_X=XX^{\mathsf T}.
\]
This is the orthogonal projector onto \(\operatorname{range}(X)\), because
\[
\Pi_X^{\mathsf T}=\Pi_X,\qquad
\Pi_X^2=X(X^{\mathsf T}X)X^{\mathsf T}=XX^{\mathsf T}=\Pi_X.
\]

The projector is gauge-invariant:
\[
\Pi_{XQ}
=
XQQ^{\mathsf T}X^{\mathsf T}
=
XX^{\mathsf T}
\qquad(Q\in O(K)).
\]
Consequently,
\[
d_{\mathrm c}([X],[Y])
=
\frac1{\sqrt2}\|XX^{\mathsf T}-YY^{\mathsf T}\|_{\mathrm F}
\]
is well-defined on quotient classes.

For rank-\(K\) orthogonal projectors,
\[
\|\Pi_X-\Pi_Y\|_{\mathrm F}^2
=
\operatorname{tr}(\Pi_X)+\operatorname{tr}(\Pi_Y)
-2\operatorname{tr}(\Pi_X\Pi_Y).
\]
Since \(\operatorname{tr}(\Pi_X)=\operatorname{tr}(\Pi_Y)=K\) and
\[
\operatorname{tr}(\Pi_X\Pi_Y)
=
\|X^{\mathsf T}Y\|_{\mathrm F}^2,
\]
one obtains
\[
d_{\mathrm c}(X,Y)^2
=
K-\|X^{\mathsf T}Y\|_{\mathrm F}^2.
\]

If \(\sigma_i(X^{\mathsf T}Y)=\cos\theta_i\), where \(\theta_i\) are the principal angles, then
\[
d_{\mathrm c}(X,Y)^2
=
\sum_{i=1}^K(1-\cos^2\theta_i)
=
\sum_{i=1}^K\sin^2\theta_i.
\]
This is the standard chordal, or projection-Frobenius, metric.[1][3][6][9]

### Required thesis corrections

- State explicitly that \(K\le D\).
- Distinguish the Stiefel convention \(\operatorname{St}(K,D)\subseteq\mathbb R^{D\times K}\) from alternative notation \(\operatorname{St}(D,K)\).
- Define the metric on equivalence classes:
  \[
  d_{\mathrm c}([X],[Y])
  =
  \frac1{\sqrt2}\|XX^{\mathsf T}-YY^{\mathsf T}\|_{\mathrm F}.
  \]
- Do not call this the canonical Riemannian distance. The canonical Grassmann geodesic distance is
  \[
  d_{\mathrm{geo}}(X,Y)=\left(\sum_i\theta_i^2\right)^{1/2};
  \]
  the chordal metric is an extrinsic metric induced by the projector embedding.
- The formula \(\sqrt{K-\|X^{\mathsf T}Y\|_{\mathrm F}^2}\) depends on both frames being orthonormal.

### Lean-ready lemmas

A suitable formal development should begin with matrices indexed by finite types, for example \(X:\mathrm{Matrix}\,\iota\,\kappa\,\mathbb R\), with finite dimensions \(D,K\).

Useful lemmas are:

```lean
def IsStiefel (X : Matrix ι κ ℝ) : Prop :=
  X.transpose ⬝ X = 1

def projector (X : Matrix ι κ ℝ) : Matrix ι ι ℝ :=
  X ⬝ X.transpose
```

Then prove:

```lean
theorem projector_transpose
    (hX : IsStiefel X) :
    (projector X).transpose = projector X := by
  ...

theorem projector_idempotent
    (hX : IsStiefel X) :
    projector X ⬝ projector X = projector X := by
  ...

theorem projector_gauge_invariant
    (hX : IsStiefel X) (Q : Matrix κ κ ℝ)
    (hQ : Q.transpose ⬝ Q = 1) :
    projector (X ⬝ Q) = projector X := by
  ...

theorem frobenius_projector_sq
    (hX : IsStiefel X) (hY : IsStiefel Y) :
    ‖projector X - projector Y‖_F ^ 2
      = 2 * (K - ‖X.transpose ⬝ Y‖_F ^ 2) := by
  ...
```

In Lean, avoid introducing principal angles initially. The projector identity is algebraically simpler and can serve as the foundational definition. Principal-angle equivalence should be a later theorem requiring singular-value machinery.

---

## 2. Cayley–SMW retraction and the claimed limit

The stated asymptotic formula is **not correct in general**.

Let
\[
W(t)=tA,
\qquad
A^{\mathsf T}=-A,
\]
and define
\[
C(t)
=
(I-\tfrac12tA)^{-1}(I+\tfrac12tA).
\]
Because \(A\) is skew-symmetric, \(C(t)\) is orthogonal whenever the inverse exists. The Cayley trajectory is
\[
R_X(tZ)=C(t)X.
\]

On \(\ker A\), \(C(t)\) acts as the identity:
\[
C(t)v=v\qquad(v\in\ker A).
\]
On \(\operatorname{range}(A)\), the eigenvalues of \(A\) are purely imaginary, so the Cayley factors remain unit-modulus but generally oscillate as \(t\to\infty\). Therefore \(C(t)\), and usually \(C(t)X\), **does not have a limit**.

For example, if
\[
A=
\begin{pmatrix}
0&-1\\
1&0
\end{pmatrix},
\]
then \(C(t)\) is a planar rotation whose angle varies with \(t\); it does not converge as \(t\to\infty\).

The expression
\[
2P_{\ker(A)}-I
\]
is indeed an orthogonal involution, but it is not the generic limit of the Cayley transform.

Let \(P=P_{\ker A}\). Since \(P\) is an orthogonal projector,
\[
H:=2P-I
\]
satisfies
\[
H^{\mathsf T}=H,
\qquad
H^2=I,
\qquad
H^{\mathsf T}H=I.
\]
Thus \(H\) is an orthogonal symmetric involution. It acts as \(+I\) on \(\ker A\) and \(-I\) on \((\ker A)^\perp=\overline{\operatorname{range}(A)}\). It is a reflection across \(\ker A\), equivalently a Householder-type reflection across that subspace.

However, the Cayley transform does not converge to \(H\). The actual pointwise behavior is:

- On \(\ker A\), \(C(t)v=v\).
- On \(\operatorname{range}(A)\), \(C(t)\) generally oscillates.
- A limit exists only under additional conditions, for example if the component of \(X\) in the nonzero spectral subspace is absent, or if a different regularized/asymptotic construction is being used.

A valid statement is therefore:

\[
\lim_{t\to\infty}C(t)X
=
X
\quad\text{if }AX=0.
\]

More generally, if one considers a **damped** Cayley-type operator, a resolvent limit, or a specifically defined generalized reflector, then a projection/reflection limit may arise, but that must be stated as a separate theorem with its own definition.

### SMW and numerical stability

Suppose
\[
A=UV^{\mathsf T},
\qquad U,V\in\mathbb R^{D\times r},
\]
with \(r\le 2K\). The Sherman–Morrison–Woodbury identity gives
\[
(I-\alpha UV^{\mathsf T})^{-1}
=
I+\alpha U(I-\alpha V^{\mathsf T}U)^{-1}V^{\mathsf T},
\]
provided the small matrix \(I-\alpha V^{\mathsf T}U\) is invertible.

This reduces a \(D\times D\) solve to an \(r\times r\) solve, but it does **not** by itself guarantee numerical stability. As \(t\to\infty\), \(\alpha=t/2\), and the small matrix may become badly conditioned or suffer cancellation. In particular, forming
\[
I+\alpha U(I-\alpha V^{\mathsf T}U)^{-1}V^{\mathsf T}
\]
can be unstable even though the exact Cayley operator is orthogonal.

The mathematically and numerically stronger implementation is to solve
\[
(I-\tfrac12tA)Y=(I+\tfrac12tA)X
\]
without explicitly forming an inverse, preferably using:

- a structured skew-symmetric factorization;
- QR-based solves;
- an orthogonal/unitary Schur representation;
- or a carefully scaled low-rank solve.

The key exact property is not an alleged limiting reflector but
\[
C(t)^{\mathsf T}C(t)=I.
\]
Indeed, with \(B=\tfrac12tA\) and \(B^{\mathsf T}=-B\),
\[
C(t)^{\mathsf T}
=
(I+B)^{\mathsf T}(I-B)^{-\mathsf T}
=
(I-B)(I+B)^{-1},
\]
and hence
\[
C(t)^{\mathsf T}C(t)=I.
\]

### Lean-ready corrections

The central formal lemmas should be:

```lean
theorem cayley_orthogonal
    (hA : A.transpose = -A)
    (hinv : IsUnit (1 - c • A)) :
    ((1 - c • A)⁻¹ ⬝ (1 + c • A)).transpose ⬝
      ((1 - c • A)⁻¹ ⬝ (1 + c • A)) = 1 := by
  ...
```

For the kernel:

```lean
theorem cayley_apply_kernel
    (hAv : A ⬝ᵥ v = 0) :
    ((1 - c • A)⁻¹ ⬝ (1 + c • A)) ⬝ᵥ v = v := by
  ...
```

For the reflector:

```lean
def reflector (P : Matrix ι ι ℝ) :=
  2 • P - 1

theorem reflector_orthogonal
    (hPself : P.transpose = P)
    (hPid : P ⬝ P = P) :
    (reflector P).transpose ⬝ reflector P = 1 := by
  ...

theorem reflector_involution
    (hPself : P.transpose = P)
    (hPid : P ⬝ P = P) :
    reflector P ⬝ reflector P = 1 := by
  ...
```

Do **not** formalize the false theorem
\[
\lim_{t\to\infty}R_X(tZ)=(2P_{\ker A}-I)X
\]
without additional hypotheses or a revised definition.

---

## 3. The 4288-bit Kulisch bound

The number 4288 is a recognized classical engineering size for an exact binary64 dot-product accumulator.[2][4][5][7][10] But the displayed derivation is not a valid proof as written.

### Errors in the proposed arithmetic

1. The minimum positive binary64 exponent is \(-1074\) when values are represented as integer multiples of \(2^{-1074}\). The minimum **normal** exponent is \(-1022\).

2. The maximum finite binary64 value is strictly less than \(2^{1024}\), with leading exponent \(1023\). Thus using \(+1024\) is appropriate as an upper scale bound, but it must not be called the exponent of a finite value.

3. The product scale ranges approximately from
   \[
   2^{-2148}
   \quad\text{to}\quad
   2^{2048},
   \]
   but the minimum product of two nonzero binary64 values is actually \(2^{-2148}\), while the maximum finite product can overflow binary64 even though its exact real value is below \(2^{2048}\).

4. The line
   \[
   (1022+1023)+106+64+1=4258
   \]
   is arithmetically false:
   \[
   1022+1023+106+64+1=2216,
   \]
   not \(4258\).

5. The stated \(4288\)-bit result follows numerically from
   \[
   67\cdot64=4288,
   \]
   but not from the displayed equation.

6. “Strictly precludes intermediate arithmetic overflow and underflow” is too broad. An exact fixed-point superaccumulator can avoid overflow provided its signed range and carry conventions are sized correctly, but the final conversion back to binary64 can overflow or underflow, and IEEE exceptional inputs must be excluded or handled separately.

### What a correct proof must specify

For each finite binary64 number \(x\), write
\[
x=s_x m_x 2^{e_x},
\]
where \(s_x\in\{-1,1\}\), \(m_x\) is an integer significand, and the exponent is normalized to a common exact lattice.

A convenient common unit for products is \(2^{-2148}\). Each exact product \(x_i y_i\) can then be represented as an integer multiple of \(2^{-2148}\). The largest product requires a bounded number of bits above that lattice origin. The accumulator width must cover:

- the complete product significand;
- the full exponent displacement;
- the sum of up to \(N\) terms;
- one or more sign/carry guard bits;
- and the chosen signed representation convention.

The \(N\)-term summation contributes
\[
\lceil\log_2 N\rceil
\]
additional magnitude bits. For \(N\le2^{64}\), this is at most \(64\) bits, assuming the bound is formulated for a sum of at most \(2^{64}\) terms and not \(2^{64}+1\) terms.

A rigorous theorem must therefore define the accumulator representation and prove an explicit inequality of the form
\[
|S|<2^{W-1}
\]
for a signed \(W\)-bit accumulator, or the corresponding unsigned-plus-sign range. Without that representation-level definition, “4288 bits” is not a formal theorem.

The literature’s 4288-bit figure should consequently be presented as a standard Kulisch design parameter, not as established by the arithmetic currently shown.[2][4][5][10]

### Lean formalization strategy

Do not formalize IEEE binary64 initially as machine floating-point operations. Formalize finite binary floating-point values as exact sign–integer–exponent triples:

```lean
structure BinFloat where
  sign : Int
  mantissa : Nat
  exponent : Int
  finite : Prop
```

Then define exact real interpretation:

```lean
def BinFloat.value (x : BinFloat) : ℚ :=
  x.sign * x.mantissa * (2 : ℚ) ^ x.exponent
```

For a product:

```lean
theorem exact_product_on_lattice
    (hx : IsBinary64 x) (hy : IsBinary64 y) :
    ∃ n : Int, x.value * y.value = n * (2 : ℚ) ^ (-2148) := by
  ...
```

For summation:

```lean
theorem exact_dot_product_bound
    (hN : N ≤ 2 ^ 64)
    (hterms : ∀ i, IsBinary64 (x i) ∧ IsBinary64 (y i)) :
    ∃ s : Int,
      dotProductExact x y = s * (2 : ℚ) ^ (-2148) ∧
      |s| < 2 ^ B := by
  ...
```

Only after proving a concrete bound \(B\) should one instantiate a word-rounded width:

```lean
def roundedWidth (B : Nat) : Nat :=
  64 * Nat.ceil (B / 64)
```

The final theorem should distinguish:

- exact accumulation without intermediate overflow;
- exact integer carry propagation;
- conversion and rounding to binary64;
- overflow of the rounded result;
- underflow and subnormal production;
- NaN and infinity inputs.

## Final arbitration

| Formulation | Verdict | Required action |
|---|---|---|
| Grassmann quotient and chordal metric | Correct, standard, gauge-invariant | Fix notation and distinguish chordal from geodesic distance |
| Cayley–SMW asymptotic limit | False in general | Remove the claimed limit; retain orthogonality and kernel-action theorems |
| 4288-bit Kulisch bound | Engineering figure is credible, displayed proof invalid | Rebuild the exponent/range proof with an explicit signed accumulator model |

The thesis can safely adopt Formulation 1 after these refinements. Formulation 2 must be materially rewritten. Formulation 3 may retain 4288 bits as a standard design target, but it is not formally validated by the current arithmetic and should not be stated as a theorem until the exact integer encoding and overflow bound are supplied.