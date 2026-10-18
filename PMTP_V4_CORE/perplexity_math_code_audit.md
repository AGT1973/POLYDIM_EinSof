The submission contains a sound systems-level observation and a plausible numerical-stability improvement, but the entropy-loss claim is not presently valid as a Shannon-theoretic result. The dissertation should distinguish carefully among **buffer-lifetime correctness**, **geometric estimation error**, **quantization distortion**, **mutual information**, and **bitwise reproducibility**.

## Part 1 — Code vulnerabilities and mitigation

### 1. Windows shared-memory `BufferError`

The reported failure is real: `SharedMemory.buf` is a `memoryview`, and NumPy arrays or slices derived from it may retain exported buffer references. Calling `close()` while such references remain alive can therefore raise `BufferError: cannot close exported pointers exist`.

The proposed operation

```python
header = bytes(self.shm.buf[:128])
```

is a genuine decoupling operation. The resulting `bytes` object owns an independent immutable copy and no longer exports or retains the shared-memory buffer. This is preferable to retaining a `memoryview` or NumPy view. Python documents `buf` as a memory view and specifies that `close()` should occur only after access to the block is no longer needed.[2]

However, the mitigation is sufficient only if **all** exported references are released, not merely the header reference. In particular, the implementation must account for:

- NumPy arrays created from `shm.buf`.
- Slices and views derived from those arrays.
- Temporary expressions whose lifetimes extend beyond the apparent statement.
- `memoryview` objects held by helper functions, iterators, or closures.
- Foreign-function-interface objects or C extensions retaining the buffer.
- Array metadata objects whose `.base` chain ultimately references the shared memory.

A robust lifecycle should resemble:

```python
def close(self):
    # Stop all users before this point.
    self.array = None
    self.view = None
    self.shm_buf = None

    gc.collect()  # defensive only; not the primary correctness mechanism

    self.shm.close()
    # Call unlink only when ownership policy permits it.
```

The order is important:

1. Stop producers and consumers.
2. Ensure no worker can still access the block.
3. Delete all views and arrays.
4. Close the local shared-memory handle.
5. Unlink only according to an explicitly defined ownership protocol.

On Windows, `unlink()` has no practical independent deletion effect in the usual POSIX sense; the block is removed when all handles are closed.[2] Thus, a design that mechanically calls both `close()` and `unlink()` should document platform-specific semantics rather than claim that both operations perform equivalent cleanup.

The mitigation is therefore **standard in principle, generally leak-free when ownership and lifetimes are controlled, but not automatically sufficient**. It should be tested under:

- repeated allocation and teardown;
- concurrent worker shutdown;
- exceptions during array construction;
- process termination;
- retained slices and transposed views;
- Windows-specific handle inspection;
- stress loops checking resident memory and handle counts.

A stronger dissertation claim would be:

> “The implementation prevents buffer-export lifetime violations by copying metadata out of shared memory and releasing all NumPy and memory-view aliases before closing the mapping. On Windows, reclamation is governed by closure of all mapping handles; therefore leak freedom depends on complete process and handle lifecycle management.”

That is more defensible than stating that `bytes(...)` alone guarantees leak freedom.

### 2. F-string LaTeX escaping

The issue is syntactic rather than mathematical. In an f-string, `{...}` denotes a Python expression. Consequently, literal LaTeX braces must be doubled:

```python
rf"\textbf{{0.00 (PMTP)}}"
```

This produces:

```text
\textbf{0.00 (PMTP)}
```

The raw-string prefix avoids Python interpreting backslash sequences such as `\t`. The formulation should distinguish the two mechanisms:

- `{{` and `}}` escape literal braces in an f-string.
- `r` prevents ordinary backslash escape processing.

If the string contains interpolated values, the safe pattern is:

```python
rf"\textbf{{{value:.2f} (PMTP)}}"
```

Here the outer doubled braces are literal LaTeX braces, while `{value:.2f}` is the actual Python interpolation.

## Part 2 — Mathematical formulations

### 1. Chordal/geodesic distance

For unit vectors \(x,y\in S^{D-1}\), the exact angular geodesic distance is

\[
\theta=\arccos(x^\top y).
\]

The Euclidean chord length satisfies

\[
\|x-y\|_2=2\sin\left(\frac{\theta}{2}\right),
\]

so, for unit-norm vectors,

\[
\theta
=
2\arcsin\left(\frac{\|x-y\|_2}{2}\right).
\]

The submitted formula

\[
\theta
=
2\arcsin\left(
\frac{\|x-x_{\mathrm{rec}}\|_2}
{2\|x_{\mathrm{rec}}\|_2}
\right)
\]

is exact only under a particular normalization interpretation. If \(x\) and \(x_{\mathrm{rec}}\) are not both unit vectors, dividing by \(2\|x_{\mathrm{rec}}\|_2\) does not generally recover the spherical angle between them. The angle between arbitrary nonzero vectors should be defined using normalized vectors:

\[
\widehat{x}=\frac{x}{\|x\|_2},
\qquad
\widehat{y}=\frac{x_{\mathrm{rec}}}{\|x_{\mathrm{rec}}\|_2}.
\]

Then use either

\[
\theta
=
2\arcsin\left(
\frac{\|\widehat{x}-\widehat{y}\|_2}{2}
\right),
\]

or, preferably for the full angular range,

\[
\theta
=
2\operatorname{atan2}
\left(
\frac{\|\widehat{x}-\widehat{y}\|_2}{2},
\frac{\|\widehat{x}+\widehat{y}\|_2}{2}
\right).
\]

The `atan2` form is generally preferable because it behaves robustly near both coincident and antipodal points; equivalent haversine-style formulas are commonly recommended for avoiding the poor conditioning of `arccos` near \(1\).[3][5][8]

For already normalized vectors, an especially useful implementation is:

```python
u = x / np.linalg.norm(x)
v = y / np.linalg.norm(y)

d = np.linalg.norm(u - v)
s = np.linalg.norm(u + v)

theta = 2.0 * np.arctan2(0.5 * d, 0.5 * s)
```

The following qualifications are essential:

- `arcsin` requires its argument to lie in \([0,1]\); rounding can produce a value slightly above \(1\), so clipping is needed.
- The chordal distance itself may suffer cancellation if `x - y` is formed from nearly identical floating-point vectors.
- A zero reported angle does not prove mathematical identity; it proves only that the computed representation produced zero under the selected metric and precision.
- If the two arrays are byte-identical FP64 objects, zero angular error relative to that same representation is expected, but that is a reproducibility statement, not proof of zero error relative to an underlying real-valued source.
- The claimed value \(1.641\times10^{-9}\) radians must be independently reproducible from the exact vector generation, normalization, formatting, parser, norm algorithm, and rounding mode.

The formula is therefore **mathematically legitimate after explicit normalization**, and the numerical motivation is sound, but the wording “chordal formulation” is incomplete. It is more accurately a **geodesic angle recovered from chordal distance**.

The dissertation should report at least:

\[
\theta_{\mathrm{ref}},
\quad
\theta_{\mathrm{REST}},
\quad
\theta_{\mathrm{PMTP}},
\quad
\|\Delta x\|_2,
\quad
\|\Delta x\|_\infty,
\quad
\frac{\|x-x_{\mathrm{rec}}\|_2}{\|x\|_2},
\]

along with the normalization convention and uncertainty or floating-point error analysis.

### 2. DPI and the proposed entropy-loss formula

The expression

\[
\Delta H_{1D}
=
\frac12D\log_2
\left(
\frac{\mathrm{MSE}_{1D}}{\varepsilon_{\mathrm{mach}}^2}
\right)
\]

does not, by itself, represent mutual-information loss, Shannon entropy loss, or a consequence of the data-processing inequality.

There are several dimensional and conceptual problems.

#### Dimensional inconsistency

If

\[
\mathrm{MSE}_{1D}\approx 2.69\times10^{-18},
\]

then MSE has units of squared signal amplitude. But \(\varepsilon_{\mathrm{mach}}^2\) is the square of a relative floating-point spacing. Unless the signal has been explicitly normalized and both quantities are defined in the same coordinate system, their ratio is not a well-defined information-theoretic quantity.

Moreover, if the intended reference is FP64 roundoff, the appropriate comparison depends on the operation and scale. Machine epsilon is not a universal additive noise variance.

#### Incorrect use of the DPI

The data-processing inequality states, for a Markov chain

\[
X\to Y\to Z,
\]

that

\[
I(X;Z)\le I(X;Y).
\]

It does not imply that the difference in mutual information equals a logarithm of the ratio of two MSE values. Such a relationship requires a specified probabilistic channel and distributional assumptions.

#### No random variables or channel model

A valid mutual-information claim requires definitions such as:

- \(X\): original random vector;
- \(Y\): serialized or quantized representation;
- \(\widehat{X}\): reconstruction;
- a stochastic or ensemble model for \(X\);
- a conditional distribution \(p(\widehat{x}\mid x)\);
- a distortion measure;
- an expectation over an explicitly specified distribution.

For continuous variables, differential entropy \(h(X)\) is not the same as discrete Shannon entropy \(H(X)\), and it is coordinate- and density-dependent. It can also be negative. Consequently, “bits lost” cannot be inferred from MSE alone.

Rate-distortion theory instead defines

\[
R(D)
=
\inf_{p(\widehat{x}\mid x):
\mathbb{E}[d(X,\widehat{X})]\le D}
I(X;\widehat{X}),
\]

where the source distribution and distortion measure are explicit.[1][7][10] A scalar MSE does not determine \(R(D)\) without those additional assumptions.

#### Possible interpretation as a heuristic

The factor

\[
\frac12\log_2\left(\frac{\sigma_1^2}{\sigma_2^2}\right)
\]

can arise in Gaussian-channel or high-rate quantization approximations. But then the dissertation must state the assumptions, for example:

- independent Gaussian coordinates;
- additive independent Gaussian reconstruction noise;
- known signal variance;
- high-rate approximation;
- distortion measured per coordinate;
- a specified baseline channel.

Even under such assumptions, multiplying by \(D\) gives a model-dependent aggregate approximation, not an exact entropy deficit. The sign also deserves attention: because

\[
\frac{2.69\times10^{-18}}{(2.22\times10^{-16})^2}
\]

is much larger than \(1\), the displayed formula produces a positive number, but that positivity does not establish that information was lost. It merely reflects the chosen ratio.

### Recommended replacement language

The current claim should not say:

> “REST loses 12,851,097 Shannon bits by the DPI, while PMTP loses zero bits.”

A defensible formulation is:

> “The REST serialization introduces an empirical reconstruction error with one-dimensional MSE approximately \(2.69\times10^{-18}\) under the stated benchmark. This quantity is a distortion measure, not an entropy deficit. Without a probabilistic source model and a specified reconstruction channel, no exact mutual-information loss or number of Shannon bits lost can be inferred from the MSE alone.”

If a theoretical information measure is required, use one of these alternatives.

**Rate-distortion formulation**

Define \(X\), \(\widehat X\), and \(d(X,\widehat X)\), then report an upper bound or estimate of

\[
R(D)
=
\inf I(X;\widehat X).
\]

For a Gaussian source with a stated covariance model and squared-error distortion, invoke the corresponding Gaussian rate-distortion function and clearly label it as model-dependent.

**Quantization-noise formulation**

Report

\[
D
=
\frac1D\mathbb{E}\|X-\widehat X\|_2^2
\]

or the empirical analogue, together with a normalized signal-to-noise ratio:

\[
\mathrm{SNR}
=
10\log_{10}
\frac{\mathbb{E}\|X\|_2^2}
{\mathbb{E}\|X-\widehat X\|_2^2}.
\]

If quantization noise is modeled as uniform with step size \(\Delta\), state the model and use

\[
\sigma_q^2=\frac{\Delta^2}{12}
\]

only where its assumptions apply.

**Differential-entropy formulation**

If the reconstruction error \(E=X-\widehat X\) is modeled as Gaussian, one may report the model-based entropy

\[
h(E)
=
\frac12\log_2\left((2\pi e)^D\det\Sigma_E\right)
\]

in bits, but this is the differential entropy of an assumed error distribution—not “bits lost.” For isotropic error \(\Sigma_E=\sigma^2 I\),

\[
h(E)
=
\frac{D}{2}\log_2(2\pi e\sigma^2).
\]

This value is not invariant under coordinate rescaling and should not be confused with discrete Shannon entropy.

### PMTP-v4 and SHA-256

SHA-256 equality establishes that two byte sequences are equal with respect to the tested digest, subject to the usual cryptographic collision assumption. It supports the claim of **byte-level reproducibility** or **serialization invariance**.

It does not establish

\[
\Delta H_{\mathrm{PMTP}}=0
\]

in an information-theoretic sense. Exact reproduction can imply zero empirical reconstruction error relative to the serialized FP64 representation:

\[
\widehat X = X_{\mathrm{serialized}},
\qquad
\|X_{\mathrm{serialized}}-\widehat X\|=0.
\]

That is a deterministic fidelity statement. It does not imply zero entropy loss relative to the original physical, real-valued, or pre-quantized source.

## Overall certification judgment

- **Windows buffer mitigation:** technically sound in principle, but certification requires proof that every exported alias is released and that ownership/teardown behavior is correct across processes.
- **F-string escaping:** correct; document doubled braces and raw-string handling separately.
- **Geodesic computation:** sound after explicit normalization; prefer an `atan2` formulation and report its conditioning and clipping behavior.
- **REST angular error:** plausible but requires a reproducible benchmark protocol and a distinction between representation error and true source error.
- **“12,851,097 bits lost”:** not certifiable as stated. It should be removed or relabeled as a heuristic model-based quantity.
- **PMTP “zero entropy loss”:** replace with “zero observed byte-level reconstruction error” or “bit-exact serialization invariance.”

The dissertation can make a strong and rigorous claim about **lifecycle safety, numerical stability, and deterministic fidelity**, but it should not present an MSE ratio as an exact Shannon entropy deficit without a complete probabilistic channel model.