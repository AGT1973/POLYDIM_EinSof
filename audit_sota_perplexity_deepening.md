Overall, none of the four formulations provides the claimed guarantees as written. They are useful engineering motifs, but each conflates **norm control with stability**, **finite-dimensional compression with associative memory**, or **geometric alignment with semantic equivalence**.

## 1. Adaptive Gain Normalization

Let
\[
a=h+\beta d,\qquad d=W(z'-z),
\]
and define
\[
h'=\|h\|_2\frac{a}{\|a\|_2}.
\]

This exactly preserves \(\|h'\|_2=\|h\|_2\), provided \(h\neq0\) and \(a\neq0\). It does **not** preserve RMS unless RMS is defined using the same vector norm and dimensional normalization. It also does not preserve layerwise activation statistics, tokenwise covariance, LayerNorm inputs, attention logits, or downstream perplexity.

The actual angular change is
\[
\cos\theta
=
\frac{\langle h,h+\beta d\rangle}
{\|h\|_2\|h+\beta d\|_2}.
\]
Thus the intervention controls norm but can rotate \(h\) arbitrarily. If \(d\) is nearly opposite to \(h\), the denominator can approach zero and the map becomes numerically singular. If \(h+\beta d=0\), the formulation is undefined.

For a prescribed relative perturbation
\[
\frac{\|h'-h\|_2}{\|h\|_2}\le \varepsilon,
\]
a sufficient condition is
\[
\beta\|d\|_2\le \varepsilon\|h\|_2.
\]
Since radial rescaling can only reduce some components of the raw perturbation, this bound is conservative but valid. A uniform bound independent of \(d\) is impossible unless \(\|d\|\) is bounded.

A non-singular implementation should use
\[
h'=\|h\|_2\,
\frac{h+\beta d}{\max(\|h+\beta d\|_2,\delta)}
\]
together with an explicit fallback when the norm is below \(\delta\). Better still, normalize the steering direction:
\[
d=\frac{W(z'-z)}{\|W(z'-z)\|_2+\delta},
\]
and choose
\[
\beta_t=\alpha\frac{\|h_t\|_2}{\|d_t\|_2+\delta}.
\]

There is no universal exact value or interval for \(\beta\). It depends on layer, token position, model scale, direction quality, and the local Jacobian of the remaining network. Empirical activation-steering work, including RepE-style representation control and later latent collaboration methods, generally supports additive or learned interventions, but does not establish that radial norm projection preserves perplexity or semantics.[3][5]

The relevant local stability quantity is not merely \(\|h'\|\), but
\[
\|J_{F}(h')\|\,\|h'-h\|,
\]
where \(F\) is the downstream computation. A useful test-time constraint is therefore
\[
\|h'-h\|_2\le \varepsilon_t
\]
plus monitoring of logit KL divergence, attention-logit shifts, and task loss.

**Correction:** treat AGN as a bounded intervention operator, not a stability theorem. Use trust-region steering:
\[
\min_{\Delta}
-\langle g,\Delta\rangle
\quad
\text{s.t.}\quad
\|\Delta\|_2\le r,\quad
\|h+\Delta\|_2=\|h\|_2,
\]
with \(r\) calibrated on held-out prompts.

## 2. Skew flow plus potential descent

The proposed dynamics are
\[
\dot z=S(z)z-\gamma\nabla V(z),
\qquad
S(z)=A(z)-A(z)^\top.
\]

The skew term satisfies
\[
z^\top S(z)z=0,
\]
so it preserves \(\|z\|_2^2\) **only when the gradient term is absent**. With the potential term,
\[
\frac{d}{dt}\frac12\|z\|_2^2
=
-\gamma z^\top\nabla V(z),
\]
which is generally nonzero. Therefore the flow is not intrinsically confined to \(S^{D-1}\).

The Lyapunov derivative for \(V\) is
\[
\dot V
=
\nabla V(z)^\top S(z)z
-\gamma\|\nabla V(z)\|_2^2.
\]
The first term does not vanish in general. Skew-symmetry only gives orthogonality to \(z\), not orthogonality to \(\nabla V(z)\). Consequently,
\[
\dot V\le0
\]
is not guaranteed.

A correct constrained flow on the sphere uses the tangent projection
\[
P_z=I-zz^\top
\]
for \(\|z\|=1\):
\[
\dot z
=
S(z)z
-\gamma P_z\nabla V(z).
\]
Then
\[
z^\top\dot z=0,
\]
and
\[
\dot V
=
\nabla V^\top S(z)z
-\gamma\|P_z\nabla V\|_2^2.
\]
To eliminate the first term, require
\[
\nabla V(z)^\top S(z)z=0,
\]
or use a projected rotational field constructed to be tangent to level sets of \(V\). The simplest guaranteed descent system is
\[
\dot z=-\gamma P_z\nabla V(z).
\]

Even with \(\dot V\le0\), asymptotic convergence to a unique minimum requires compactness, regularity, isolated equilibria, and a suitable strictness condition. Nonconstant \(V\) can still admit stationary points, invariant sets, and—in systems with non-gradient rotational components—periodic orbits. LaSalle’s invariance principle gives convergence to the largest invariant subset of
\[
\{z:\dot V=0\},
\]
not automatically to one minimum.

For discrete integration with step size \(\eta\), the Euler update
\[
z_{k+1}=z_k+\eta S_kz_k
\]
has
\[
\|z_{k+1}\|_2^2
=
\|z_k\|_2^2+\eta^2\|S_kz_k\|_2^2,
\]
so it expands unless corrected. Use an exact exponential or Cayley rotation:
\[
R_k=\operatorname{Cay}(\eta S_k)
=
(I-\tfrac{\eta}{2}S_k)^{-1}
(I+\tfrac{\eta}{2}S_k),
\]
which is orthogonal for skew \(S_k\). Apply projected descent separately and renormalize or use a Riemannian integrator.

No implication
\[
\dot V\le0\Longrightarrow \rho(J)\le1
\]
exists. Spectral-radius control is a property of the discrete-time Jacobian:
\[
\rho\!\left(D\Psi(z^\star)\right)<1.
\]
For continuous time, local exponential stability requires Jacobian eigenvalues with strictly negative real parts, modulo tangent-space constraints. Pure skew dynamics have imaginary eigenvalues and are neutrally stable, not asymptotically stable.

**Correction:** specify a discrete map \(\Psi\), prove invariant-set preservation, and establish
\[
\rho(D\Psi(z^\star)|_{T_{z^\star}S^{D-1}})<1.
\]
No-limit-cycle claims require additional gradient-like structure or a strict Lyapunov function.

## 3. HiPPO–Cayley memory

The state dimension \(N=64\) is constant, so the recurrent state has \(O(1)\) storage with respect to sequence length. That does not mean it can retain \(100{,}000\) arbitrary associative memories.

A linear state
\[
\dot c=-Ac+Bu
\]
stores the input history through a rank-\(N\) summary. For arbitrary sequences of length \(T\), exact retrieval of \(T\) independent items requires memory capacity scaling with \(T\), not fixed \(N\). At best, a HiPPO state preserves a structured approximation to a recent or weighted history.

A Cayley transform preserves stability or orthogonality properties of the transformed operator; it does not create additional information capacity. In particular, an orthogonal recurrence
\[
c_{k+1}=Qc_k,\qquad Q^\top Q=I
\]
prevents norm decay, but it also prevents asymptotic forgetting and does not guarantee separability of stored memories. Finite precision, input interference, observability, and readout conditioning remain limiting factors.

For a discrete linear system
\[
c_{k+1}=Fc_k+Bu_k,
\]
retrieval of a past input \(u_{k-\tau}\) depends on
\[
F^\tau B.
\]
Long-horizon recoverability requires these modes to remain both nonvanishing and distinguishable. Orthogonality preserves norms but does not ensure that the vectors \(F^\tau B\) are linearly independent or well-conditioned. With one input channel and \(N=64\), the reachable subspace is at most 64-dimensional.

The appropriate comparison with CAM is therefore not “catastrophic forgetting versus no forgetting,” but:

- HiPPO: compact, online, structured approximation of temporal history.
- CAM: content-indexed retrieval with explicit storage and much better exact recall for sparse associative items.
- Fixed \(N=64\): bounded information capacity, regardless of the number of time steps.

**Correction:** state a task-specific memory guarantee. For example, define a retrieval error
\[
\sup_{\tau\le T}
\mathbb E\left[
\|\hat u_{t-\tau}-u_{t-\tau}\|^2
\right]
\le\varepsilon,
\]
then analyze observability/conditioning of the finite-horizon Gramian
\[
\mathcal O_T
=
\sum_{\tau=0}^{T-1}
(F^\tau)^\top C^\top C F^\tau.
\]
If the task requires \(K\) independent associative bindings, allocate capacity proportional to \(K\), use external or differentiable CAM, or introduce compression/error guarantees. Cayley discretization alone cannot establish 100k-step associative recall.

## 4. Stiefel/Gromov–Wasserstein coupling

Let
\[
U_i\in\mathrm{St}(D_i,d),
\qquad
U_i^\top U_i=I_d,
\]
with \(d=1024\). This preserves inner products **inside the selected \(d\)-dimensional subspace**. It does not preserve the full geometry of \(\mathbb R^{D_i}\), because
\[
U_iU_i^\top
\]
is a rank-\(d\) projector when \(d<D_i\).

For a latent \(z_i\), the discarded component is
\[
(I-U_iU_i^\top)z_i.
\]
The reconstruction error under projection is exactly
\[
\|z_i-U_iU_i^\top z_i\|_2
=
\|(I-U_iU_i^\top)z_i\|_2.
\]
Thus semantic preservation requires the task-relevant information to lie predominantly in the chosen subspace. Orthogonality alone provides no such guarantee.

A cycle map such as
\[
\Phi_{21}\Phi_{12}(z_1)\approx z_1
\]
also does not prove semantic mutual information preservation. Cycle consistency can be satisfied by degenerate or distribution-specific bijections, especially when the training support is finite. It can preserve geometry while permuting semantic labels, or reconstruct \(z_1\) while the intermediate representation loses information and the decoder exploits side information or learned priors.

Gromov–Wasserstein alignment is useful because it compares internal distance structures between spaces of different dimensions; it does not identify a unique semantic correspondence. GW objectives have symmetries, can admit multiple optimal couplings, and are sensitive to metric choice, normalization, sampling, outliers, and entropic regularization.[1][2][4]

The claim of “lossless information exchange” therefore requires a much stronger statement than cycle loss. A sufficient empirical/theoretical package would include:

\[
I(Y;z_i)-I(Y;\Phi_{ji}(z_i))\le\varepsilon
\]
for task labels \(Y\), or a task-performance bound;

\[
\sup_{z\in\mathcal Z}
\|\Phi_{ji}(z)-\Phi_{ji}(z')\|
\le L\|z-z'\|
\]
for Lipschitz control;

\[
\| \Phi_{ij}(\Phi_{ji}(z))-z\|
\le\varepsilon
\]
on an explicitly defined support, not merely training samples;

and a projection residual bound
\[
\mathbb E\|(I-U_iU_i^\top)z_i\|^2\le\delta.
\]

For heterogeneous LLMs, coordinate systems are not generally linearly related. Layer choice, tokenization, positional encoding, normalization, anisotropy, and model-specific feature superposition can make a single global Stiefel map inadequate. A nonlinear adapter, multi-layer alignment, shared autoencoder, or conditional map may be required. The canonical dimension \(1024\) should be selected from rate–distortion or task-retention curves, not fixed a priori.

**Correction:** formulate the objective as constrained task-preserving representation transfer:
\[
\min_{\Phi_{12},\Phi_{21}}
\mathcal L_{\mathrm{task}}
+\lambda_{\mathrm{GW}}\mathcal L_{\mathrm{GW}}
+\lambda_{\mathrm{cyc}}\mathcal L_{\mathrm{cyc}}
+\lambda_{\mathrm{dist}}\mathcal L_{\mathrm{dist}}
\]
subject to measured projection, reconstruction, and downstream-performance bounds. Stiefel constraints can regularize the maps, but they cannot by themselves guarantee semantic mutual information.

## Bottom line

- **AGN:** exact norm preservation, but no perplexity or semantic guarantee; \(\beta\) must be trust-region controlled.
- **Symplectic flow:** skew terms conserve quadratic energy only in isolation; the proposed potential descent is not generally Lyapunov-decreasing, and \(\rho(J)\le1\) does not follow.
- **HiPPO–Cayley:** \(O(1)\) state storage and long-horizon numerical stability, but not arbitrary 100k-step associative memory.
- **GW–Stiefel coupling:** dimension-agnostic geometric alignment, but neither semi-orthogonality nor cycle consistency implies semantic or information preservation.

The common correction is to replace qualitative claims with explicit bounds on intervention radius, invariant sets, Jacobian spectra, observability/conditioning, projection residuals, and task-level information retention.