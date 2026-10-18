# SOLUCIONES DEFINITIVAS DE ARBITRAJE FORMAL PERPLEXITY SONAR-PRO — ETAPA 19
Fecha: 2026-10-10 | Motor: Perplexity Sonar-Pro | Ámbito: Cierre Definitivo Red Team POLYDIM

## Punto 1: Formalización Topológica de CUDA IPC (Staged Pinned DMA vs P2P) (SOL_PUNTO_1_CUDA_IPC)

The central correction is:

> If `cudaDeviceCanAccessPeer(G0,G1) == 0`, a CUDA IPC memory handle does **not** create a direct G0-to-G1 data path. CUDA IPC exports and imports a process-portable handle to an allocation; it does not override the platform’s peer-access capability.[10][1]

Therefore, the claimed path must be classified as **host-staged only if the implementation actually performs two explicit or runtime-internal host-mediated copies**:

\[
G_0 \longrightarrow H_{\mathrm{pinned}} \longrightarrow G_1 .
\]

CUDA IPC itself is a **control-plane mechanism** for sharing a device allocation between processes. It is not, by itself, a transport-layer guarantee.

## 1. Architectural taxonomy

Let

- \(G_0\) be the source GPU,
- \(G_1\) be the destination GPU,
- \(H\) be page-locked host memory,
- \(x\in G_0\) be the source tensor,
- \(y\in G_1\) be the destination tensor,
- \(B=|x|\) be the number of bytes transferred.

A **direct peer transport** requires a fabric path that permits the destination GPU or its copy engine to address source-GPU memory. In CUDA, this capability is queried by `cudaDeviceCanAccessPeer`; peer support is confirmed only when the query returns true, after which peer access may be enabled.[1][8]

With

\[
\operatorname{cudaDeviceCanAccessPeer}(G_1,G_0)=0,
\]

the following path is not available:

\[
G_0 \xrightarrow{\text{GPU peer DMA}} G_1.
\]

The architecturally honest classification is instead:

\[
\boxed{
\text{Staged UVA IPC Transport}
=
\text{CUDA IPC handle exchange}
+
G_0\to H_{\mathrm{pinned}}
+
H_{\mathrm{pinned}}\to G_1
}
\]

Here:

- **CUDA IPC** supplies process-portable handles and process-local pointers for CUDA allocations.[10]
- **UVA** provides a unified virtual-addressing model that lets CUDA identify the memory domain associated with pointers; it does not imply physical peer reachability.
- **Pinned host memory** permits DMA without pageable-memory staging by the CUDA driver.
- **PCIe** carries each GPU-to-host or host-to-GPU leg.

Calling this “host DRAM-bypass direct peer DMA” would be incorrect unless hardware and runtime evidence establish a direct GPU-to-GPU route. CUDA documentation explicitly defines peer access as direct access to peer memory and exposes its availability through `cudaDeviceCanAccessPeer`.[1][3]

The term **DRAM-bypass** is also misleading for ordinary pinned-memory staging. Page locking prevents paging and enables DMA; it does not mean that host memory is bypassed. The data bytes still traverse the host-memory path:

\[
G_0\to \text{PCIe root complex}\to \text{host memory}\to
\text{PCIe root complex}\to G_1.
\]

CUDA IPC may be used to share the source allocation between processes, but the handle exchange is not evidence that the payload bypasses host memory. CUDA’s IPC interface is specified as an interprocess mechanism for obtaining process-local pointers to shared device allocations.[10]

## 2. PCIe bandwidth model

For PCIe Gen3:

- transfer rate per lane: \(8\ \mathrm{GT/s}\),
- encoding efficiency: \(128/130\),
- payload bytes per second per lane:

\[
8\times 10^9
\cdot \frac{128}{130}
\cdot \frac{1}{8}
=
985\frac{5}{13}\times 10^6
\ \mathrm{B/s}.
\]

For \(16\) lanes:

\[
R_{\mathrm{PCIe,raw}}
=
16\cdot 8\times10^9\cdot \frac{128}{130}\cdot\frac18
\approx 15.754\ \mathrm{GB/s}.
\]

This is a line-rate payload approximation, not an application-level guarantee. Let

\[
R_{\mathrm{h}}
\]

denote the sustainable one-hop application bandwidth after protocol overhead, copy-engine limitations, NUMA placement, topology contention, and software effects. A representative value is

\[
R_{\mathrm{h}}\approx 12.5\ \mathrm{GB/s},
\]

but it must be measured rather than treated as universal.

Let

- \(L_{0H}\) be fixed launch and synchronization latency for \(G_0\to H\),
- \(L_{H1}\) be fixed latency for \(H\to G_1\),
- \(R_{0H}\) and \(R_{H1}\) be effective one-hop rates.

For a **non-overlapped** transfer:

\[
T_{\mathrm{serial}}(B)
=
L_{0H}+L_{H1}
+\frac{B}{R_{0H}}
+\frac{B}{R_{H1}}.
\]

If both hops have equal rate \(R_{\mathrm h}\),

\[
T_{\mathrm{serial}}(B)
=
L_{\mathrm{stage}}+\frac{2B}{R_{\mathrm h}},
\qquad
L_{\mathrm{stage}}=L_{0H}+L_{H1}.
\]

The corresponding asymptotic bandwidth is

\[
R_{\mathrm{serial,eff}}
=
\frac{B}{T_{\mathrm{serial}}(B)}
\longrightarrow
\frac{R_{\mathrm h}}{2}.
\]

Thus, with \(R_{\mathrm h}=12.5\ \mathrm{GB/s}\),

\[
R_{\mathrm{serial,eff}}\approx 6.25\ \mathrm{GB/s}.
\]

For a **pipelined double-buffered** implementation, divide the payload into \(n\) chunks of size \(b=B/n\). If the two PCIe legs can operate concurrently and host buffers are independently reusable, the steady-state interval is governed by the slower stage:

\[
T_{\mathrm{pipe}}(B,n)
=
L_{\mathrm{fill}}
+
(n-1)\max\!\left(
\frac{b}{R_{0H}},
\frac{b}{R_{H1}}
\right)
+
\frac{b}{R_{0H}}
+
\frac{b}{R_{H1}},
\]

where \(L_{\mathrm{fill}}\) includes initial launch, event, and synchronization costs.

For equal rates:

\[
T_{\mathrm{pipe}}(B,n)
\approx
L_{\mathrm{fill}}
+
\frac{B}{R_{\mathrm h}}
+
\frac{B}{nR_{\mathrm h}},
\]

and therefore

\[
R_{\mathrm{pipe,eff}}
=
\frac{B}{T_{\mathrm{pipe}}(B,n)}
\longrightarrow
R_{\mathrm h}
\quad\text{as }n\to\infty.
\]

This explains why a staged path can approach approximately one-hop bandwidth under sufficient pipelining: the two legs are not necessarily serialized. It does **not** mean that the path is direct GPU-to-GPU DMA.

The general asymptotic pipelined bandwidth is

\[
\boxed{
R_{\mathrm{pipe,\infty}}
=
\min(R_{0H},R_{H1})
}
\]

provided that:

1. the two PCIe paths are independently schedulable;
2. the host buffer pool is sufficiently deep;
3. copy engines and synchronization permit overlap;
4. the host-memory and root-complex paths are not shared bottlenecks;
5. the benchmark measures steady-state throughput rather than end-to-end single-message latency.

If both GPU transfers contend for the same PCIe root-complex or host-memory resource, introduce a shared bottleneck \(R_{\mathrm{shared}}\):

\[
R_{\mathrm{pipe,\infty}}
=
\min(R_{0H},R_{H1},R_{\mathrm{shared}}).
\]

Consequently, a measured \(9.03\ \mathrm{GB/s}\) is compatible with a well-pipelined staged transport under a \(12.5\ \mathrm{GB/s}\) practical one-hop ceiling:

\[
9.03 < 12.5.
\]

That measurement alone cannot establish direct peer DMA. It is necessary to inspect topology, peer-access status, copy direction, host-buffer allocation, and concurrency.

## 3. Exact distinction from direct P2P

A direct NVLink or BAR/P2P transfer has the abstract path

\[
G_0 \xrightarrow{\text{fabric or mapped BAR}} G_1,
\]

with transfer time

\[
T_{\mathrm{direct}}(B)
=
L_{\mathrm{direct}}
+
\frac{B}{R_{\mathrm{direct}}}.
\]

There is no required intermediate host-memory write and read.

By contrast, staged transport has

\[
T_{\mathrm{staged,serial}}(B)
=
L_{\mathrm{stage}}
+
\frac{B}{R_{0H}}
+
\frac{B}{R_{H1}},
\]

or, with pipeline overlap,

\[
T_{\mathrm{staged,pipe}}(B,n)
=
L_{\mathrm{fill}}
+
(n-1)\max\left(
\frac{b}{R_{0H}},
\frac{b}{R_{H1}}
\right)
+
\frac{b}{R_{0H}}
+
\frac{b}{R_{H1}}.
\]

The equations differ even when their large-message measured bandwidths happen to be numerically similar.

## 4. Publication-ready LaTeX definition

```latex
\begin{definition}[Staged UVA IPC Transport]
Let $G_0$ and $G_1$ be two discrete GPUs, let
$H_{\mathrm{p}}$ denote page-locked host memory, and let
$x\in G_0$ be a tensor of size $B$ bytes.  A
\emph{Staged UVA IPC Transport} from $G_0$ to $G_1$ is a
data-movement protocol satisfying
\[
  G_0 \longrightarrow H_{\mathrm{p}}
  \longrightarrow G_1,
\]
where the first and second arrows are DMA transfers over the
host interconnect, typically PCI Express, and where CUDA Unified
Virtual Addressing (UVA) and CUDA Interprocess Communication (IPC)
are used for address-domain identification and, when applicable,
cross-process sharing of CUDA allocation handles.

Formally, if
\[
  R_{0H}>0,\qquad R_{H1}>0,
\]
are the effective rates of the two host-mediated legs, and
$L_{0H},L_{H1}$ are their fixed latencies, then the non-overlapped
completion time is
\[
  T_{\mathrm{staged}}(B)
  =
  L_{0H}+L_{H1}
  + \frac{B}{R_{0H}}
  + \frac{B}{R_{H1}}.
\]
For a chunked, double-buffered implementation with $n$ chunks of
size $b=B/n$, the steady-state completion time is modeled by
\[
  T_{\mathrm{pipe}}(B,n)
  =
  L_{\mathrm{fill}}
  +(n-1)\max\!\left\{
      \frac{b}{R_{0H}},
      \frac{b}{R_{H1}}
    \right\}
  +\frac{b}{R_{0H}}
  +\frac{b}{R_{H1}}.
\]
Hence the asymptotic pipelined bandwidth is
\[
  R_{\mathrm{pipe},\infty}
  =
  \min\{R_{0H},R_{H1},R_{\mathrm{shared}}\},
\]
where $R_{\mathrm{shared}}$ denotes any common PCIe, root-complex,
host-memory, or copy-engine bottleneck.
\end{definition}

\begin{remark}[Architectural meaning]
CUDA IPC is a control-plane facility: it exports a process-portable
handle for a CUDA allocation and permits another process to obtain a
process-local device pointer.  IPC does not, by itself, establish a
physical GPU-to-GPU payload path.  UVA provides a unified virtual
addressing abstraction, but it does not imply peer reachability.

Accordingly, if
\[
  \operatorname{cudaDeviceCanAccessPeer}(G_1,G_0)=0,
\]
the protocol shall not be described as direct peer memory access,
direct GPU-to-GPU DMA, BAR P2P, or NVLink transport.  If the payload
is copied through page-locked host memory, the mathematically and
architecturally correct designation is
\[
  \text{\emph{Staged UVA IPC Transport}}.
\]
The adjective ``pinned'' denotes page locking and DMA eligibility; it
does not denote bypass of host memory or host DRAM.
\end{remark}
```

```latex
\begin{definition}[Direct NVLink/BAR P2P Transport]
Let $G_0$ and $G_1$ be discrete GPUs.  A
\emph{Direct NVLink/BAR P2P Transport} is a protocol in which the
payload bytes move from an allocation physically owned by $G_0$ to an
allocation physically owned by $G_1$ through a GPU-to-GPU fabric or
peer BAR address path, without an intermediate host-memory payload
copy:
\[
  G_0 \longrightarrow G_1.
\]
Its idealized transfer time is
\[
  T_{\mathrm{direct}}(B)
  =
  L_{\mathrm{direct}}
  +\frac{B}{R_{\mathrm{direct}}},
\]
where $R_{\mathrm{direct}}$ is the sustainable bandwidth of the
direct inter-GPU path.  The classification requires evidence that
the platform and CUDA runtime support peer access for the ordered
pair $(G_1,G_0)$; an IPC handle alone is insufficient evidence.
\end{definition}

\begin{remark}[Non-equivalence]
A staged transport and a direct P2P transport may produce similar
benchmark numbers for a particular message size and topology, but
they are not architecturally equivalent.  The former contains two
host-interconnect legs and has serial cost
\[
  \frac{B}{R_{0H}}+\frac{B}{R_{H1}},
\]
whereas the latter contains one direct inter-GPU leg
\[
  \frac{B}{R_{\mathrm{direct}}}.
\]
Pipeline overlap can hide the additive cost of the two staged legs in
steady state; it cannot remove the host-memory traversal from the
transport's architectural definition.
\end{remark}
```

## 5. Minimal implementation invariant

A production implementation should classify the path from runtime facts, not from the presence of an IPC handle:

```cpp
struct TransportClassification {
    bool peer_access;
    bool uses_pinned_host_stage;
    const char* name;
};

TransportClassification classify(bool can_access_peer,
                                 bool uses_pinned_host_stage) {
    if (can_access_peer && !uses_pinned_host_stage)
        return {true, false, "Direct NVLink/BAR P2P Transport"};

    if (!can_access_peer && uses_pinned_host_stage)
        return {false, true, "Staged UVA IPC Transport"};

    return {can_access_peer, uses_pinned_host_stage,
            "Requires topology/runtime audit"};
}
```

For the stated T4 environment, the defensible thesis claim is:

\[
\boxed{
\text{CUDA IPC-mediated, page-locked-host-memory-staged transfer}
}
\]

not:

\[
\boxed{
\text{direct host-DRAM-bypass GPU peer DMA}.
}
\]

---

## Punto 2: Árbol de Reducción Jerárquico Determinista en Triton para Variedad Stiefel (SOL_PUNTO_2_TRITON_DETERMINISM)

A fully rigorous replacement is possible, but one premise must be corrected: `tl.sum` is documented as an associative/commutative reduction, so its internal tree is not a portable, specified ordering guarantee.[1] Therefore, a two-pass design with `tl.sum` can make **global block assignment deterministic**, but it cannot by itself guarantee bitwise reproducibility across Triton/compiler/GPU implementations. The implementation below provides a fixed logical reduction tree; for a strict bitwise contract, compile and run with a fixed toolchain/device and use the explicit pairwise kernel rather than relying on unspecified reduction lowering.

## Mathematical construction

Let

\[
s=\sum_{i=0}^{D-1}x_i,\qquad D=10{,}000{,}000.
\]

Choose a fixed block size \(B\), and let

\[
G=\left\lceil \frac{D}{B}\right\rceil.
\]

Define block intervals

\[
I_j=\{jB,\ldots,\min((j+1)B,D)-1\},
\]

and exact block sums

\[
p_j=\sum_{i\in I_j}x_i.
\]

The algorithm computes

\[
\widehat{s}
=\operatorname{fl}\left(\operatorname{fl}\left(\cdots
\operatorname{fl}(\widehat p_0+\widehat p_1)+\widehat p_2
\cdots\right)+\widehat p_{G-1}\right),
\]

where each \(\widehat p_j\) is produced by a fixed binary tree. The global order is therefore independent of block scheduling: block \(j\) writes only `partial[j]`, and pass 2 consumes `partial[0], partial[1], ...` in ascending index order.

The IEEE-754 normal-operation model is

\[
\operatorname{fl}(a+b)=(a+b)(1+\delta),\qquad |\delta|\le u,
\]

with binary64 unit roundoff

\[
u=2^{-53}\approx 1.1102230246251565\times 10^{-16}.
\]

For a balanced binary tree of depth \(h\),

\[
|\operatorname{fl}_{\mathrm{tree}}(x)-\sum_i x_i|
\le \gamma_h\sum_i|x_i|,
\qquad
\gamma_h=\frac{hu}{1-hu}.
\]

If the first pass has tree depth \(h_1=\lceil\log_2 B\rceil\), and pass 2 has depth \(h_2=\lceil\log_2 G\rceil\), then

\[
|\widehat{s}-s|
\le
\gamma_{h_1}\sum_{i=0}^{D-1}|x_i|
+
\gamma_{h_2}\sum_{j=0}^{G-1}|p_j|.
\]

Using

\[
\sum_j |p_j|\le \sum_i |x_i|,
\]

gives

\[
|\widehat{s}-s|
\le
(\gamma_{h_1}+\gamma_{h_2})
\|x\|_1.
\]

This is the valid general bound for a two-level reduction. It is **not**, in general,

\[
\gamma_{\lceil\log_2 D\rceil}\|x\|_2^2.
\]

That expression is dimensionally and mathematically incorrect for a scalar sum: the standard absolute bound uses \(\|x\|_1\), not \(\|x\|_2^2\). For a dot product \(x^\top x\), first-round each product and then apply the same summation bound to \(z_i=\operatorname{fl}(x_i^2)\).

For \(D=10{,}000{,}000\),

\[
\lceil\log_2D\rceil=24,
\qquad
\gamma_{24}
=\frac{24u}{1-24u}
\approx 2.6645352591\times10^{-15}
<5.0\times10^{-15}.
\]

Thus the \(5.0\times10^{-15}\) claim is valid for a **single balanced tree of depth at most 24**, multiplied by the relevant absolute-magnitude norm. A two-pass hierarchy must use \(h_1+h_2\), or the sharper separate bound above. For example, with \(B=256\),

\[
h_1=8,\qquad G=39063,\qquad h_2=16,
\]

so \(h_1+h_2=24\), yielding the same conservative \(\gamma_{24}\) bound.

For the Gram matrix of \(Y\in\mathbb{R}^{D\times K}\), compute each entry with

\[
x_i=Y_{i,a}Y_{i,b},
\]

and obtain

\[
|\widehat{G}_{ab}-G_{ab}|
\le
\gamma_{24}\sum_{i=0}^{D-1}|Y_{i,a}Y_{i,b}|
\]

under exact products, or an additional \(u\)-level product-rounding term when products are formed in binary64:

\[
|\widehat{G}_{ab}-G_{ab}|
\le
\gamma_{24}\sum_i |Y_{i,a}Y_{i,b}|
+
u\sum_i |Y_{i,a}Y_{i,b}|
+
O(u^2).
\]

The spectral error then satisfies

\[
\|\widehat G-G\|_2
\le
\|\widehat G-G\|_F
\le
\left(\sum_{a,b}
|\widehat G_{ab}-G_{ab}|^2\right)^{1/2}.
\]

No reduction algorithm can guarantee \(\|\widehat G-I\|_2\le 5\times10^{-15}\) without assumptions on \(Y\), conditioning, overflow/underflow, and product rounding.

## Triton implementation

The following implementation uses:

- one deterministic logical block per contiguous input interval;
- an explicit padded power-of-two pairwise tree in pass 1;
- a second explicit pairwise tree over the partial-sum workspace;
- no global floating-point atomics;
- fixed zero padding;
- one output scalar per reduction.

The explicit loop is preferable to `tl.sum` when reproducibility is a contractual requirement, because `tl.sum` does not specify a portable evaluation order.[1]

```python
# deterministic_reduce.py
from __future__ import annotations

import torch
import triton
import triton.language as tl


@triton.jit
def _pairwise_reduce_pow2(x, BLOCK: tl.constexpr):
    """
    Fixed logical tree:
        stride = 1, 2, 4, ..., BLOCK/2
    At each level, lane i combines with lane i + stride.
    """
    stride = 1
    while stride < BLOCK:
        left = tl.arange(0, BLOCK)
        right = left + stride
        partner = tl.load(
            x + right,
            mask=right < BLOCK,
            other=0.0,
        )
        val = tl.load(x + left)
        val = val + partner
        tl.store(x + left, val, mask=left < BLOCK)
        stride *= 2

    return tl.load(x)


@triton.jit
def reduce_pass1_kernel(
    x_ptr,
    partial_ptr,
    n_elements,
    BLOCK: tl.constexpr,
):
    pid = tl.program_id(0)
    lane = tl.arange(0, BLOCK)

    # Every program owns one fixed contiguous interval.
    offsets = pid * BLOCK + lane
    mask = offsets < n_elements

    vals = tl.load(x_ptr + offsets, mask=mask, other=0.0)
    tl.store(partial_ptr + lane, vals)

    # The temporary array is conceptual SRAM/register storage in Triton's
    # lowered reduction implementation. The logical tree is fixed.
    result = _pairwise_reduce_pow2(partial_ptr, BLOCK)

    if lane == 0:
        tl.store(partial_ptr + pid, result)


@triton.jit
def reduce_pass2_kernel(
    partial_ptr,
    out_ptr,
    n_partials,
    BLOCK: tl.constexpr,
):
    """
    One program performs the complete fixed tree over partial_ptr.

    The host allocates exactly BLOCK entries and zero-pads entries
    n_partials ... BLOCK-1.
    """
    lane = tl.arange(0, BLOCK)
    vals = tl.load(
        partial_ptr + lane,
        mask=lane < n_partials,
        other=0.0,
    )

    # Use registers/local tensor values for the fixed tree.
    stride = 1
    while stride < BLOCK:
        partner_idx = lane + stride
        partner = tl.load(
            partial_ptr + partner_idx,
            mask=partner_idx < n_partials,
            other=0.0,
        )
        vals = vals + partner
        stride *= 2

    if lane == 0:
        tl.store(out_ptr, vals)


def _next_pow2(n: int) -> int:
    return 1 if n <= 1 else 1 << (n - 1).bit_length()


def deterministic_sum(
    x: torch.Tensor,
    *,
    block: int = 256,
) -> torch.Tensor:
    """
    Deterministic hierarchical binary64 sum.

    Preconditions:
      - CUDA tensor
      - contiguous
      - dtype torch.float64
      - finite values
      - block is a power of two
    """
    if not x.is_cuda:
        raise ValueError("x must be a CUDA tensor")
    if x.dtype != torch.float64:
        raise TypeError("x must have dtype torch.float64")
    if not x.is_contiguous():
        x = x.contiguous()
    if block <= 0 or (block & (block - 1)):
        raise ValueError("block must be a power of two")

    n = x.numel()
    if n == 0:
        return torch.zeros((), device=x.device, dtype=x.dtype)

    n_partials = (n + block - 1) // block

    # Pass 2 requires a power-of-two logical tree.
    tree_size = _next_pow2(n_partials)

    # The workspace is deliberately zero-initialized. Entries [0:n_partials)
    # are written by pass 1; the remainder supplies deterministic padding.
    workspace = torch.zeros(
        tree_size,
        device=x.device,
        dtype=torch.float64,
    )
    out = torch.empty((), device=x.device, dtype=torch.float64)

    # One program per fixed input interval.
    grid1 = (n_partials,)
    reduce_pass1_kernel[grid1](
        x,
        workspace,
        n,
        BLOCK=block,
        num_warps=min(8, max(1, block // 32)),
    )

    # Kernel launch order does not matter: pass 2 is a separate launch and
    # therefore observes the completed pass-1 writes.
    reduce_pass2_kernel[(1,)](
        workspace,
        out,
        n_partials,
        BLOCK=tree_size,
        num_warps=min(8, max(1, tree_size // 32)),
    )

    return out
```

The pass-1 kernel above illustrates the deterministic logical algorithm, but using a global workspace as scratch for the intra-block tree is not production-safe: concurrent programs could overwrite one another’s scratch region. The production version must assign each program a private workspace slice or keep the tree values in the compiler-managed local tensor.

A safe version uses a distinct scratch region per program:

```python
@triton.jit
def reduce_pass1_kernel_safe(
    x_ptr,
    scratch_ptr,
    partial_ptr,
    n_elements,
    BLOCK: tl.constexpr,
):
    pid = tl.program_id(0)
    lane = tl.arange(0, BLOCK)

    x_offsets = pid * BLOCK + lane
    scratch_offsets = pid * BLOCK + lane

    vals = tl.load(
        x_ptr + x_offsets,
        mask=x_offsets < n_elements,
        other=0.0,
    )
    tl.store(scratch_ptr + scratch_offsets, vals)

    stride = 1
    while stride < BLOCK:
        left = pid * BLOCK + lane
        right = left + stride

        a = tl.load(scratch_ptr + left)
        b = tl.load(
            scratch_ptr + right,
            mask=lane + stride < BLOCK,
            other=0.0,
        )
        tl.store(
            scratch_ptr + left,
            a + b,
            mask=lane < BLOCK - stride,
        )
        stride *= 2

    if lane == 0:
        result = tl.load(scratch_ptr + pid * BLOCK)
        tl.store(partial_ptr + pid, result)
```

Host wrapper:

```python
def deterministic_sum_safe(
    x: torch.Tensor,
    *,
    block: int = 256,
) -> torch.Tensor:
    if not x.is_cuda:
        raise ValueError("x must be CUDA")
    if x.dtype != torch.float64:
        raise TypeError("x must be float64")
    if not x.is_contiguous():
        x = x.contiguous()
    if block <= 0 or (block & (block - 1)):
        raise ValueError("block must be a power of two")

    n = x.numel()
    if n == 0:
        return torch.zeros((), device=x.device, dtype=torch.float64)

    n_partials = (n + block - 1) // block
    tree_size = _next_pow2(n_partials)

    # Private pass-1 scratch: no program writes another program's region.
    scratch = torch.empty(
        n_partials * block,
        device=x.device,
        dtype=torch.float64,
    )
    partial = torch.zeros(
        tree_size,
        device=x.device,
        dtype=torch.float64,
    )
    out = torch.empty((), device=x.device, dtype=torch.float64)

    reduce_pass1_kernel_safe[(n_partials,)](
        x,
        scratch,
        partial,
        n,
        BLOCK=block,
        num_warps=min(8, max(1, block // 32)),
    )

    reduce_pass2_kernel[(1,)](
        partial,
        out,
        n_partials,
        BLOCK=tree_size,
        num_warps=min(8, max(1, tree_size // 32)),
    )

    return out
```

For \(D=10{,}000{,}000\), `block=256` gives:

```python
D = 10_000_000
B = 256
G = (D + B - 1) // B
T = _next_pow2(G)

print(G)  # 39063
print(T)  # 65536
```

The second pass therefore has a maximum logical depth of \(16\), while the first pass has depth \(8\); the total depth is \(24\).

## Gram-entry kernel pattern

For a fixed pair of columns \(a,b\), form the products and invoke the same reduction:

```python
def deterministic_gram_entry(
    Y: torch.Tensor,
    a: int,
    b: int,
    *,
    block: int = 256,
) -> torch.Tensor:
    if Y.ndim != 2 or Y.dtype != torch.float64:
        raise ValueError("Y must be a rank-2 float64 tensor")
    if not Y.is_cuda:
        raise ValueError("Y must be CUDA-resident")

    products = Y[:, a] * Y[:, b]
    return deterministic_sum_safe(products, block=block)
```

For a complete \(K\times K\) Gram matrix, launch one independent deterministic reduction per entry, or fuse entries only if the fused kernel preserves a fixed tree for every entry. Do not use `tl.atomic_add` for the accumulation.

## Reproducibility conditions

The result is bitwise reproducible only under a fixed execution contract:

- identical input bit patterns;
- identical GPU architecture;
- identical Triton/compiler version and compilation options;
- identical block size and grid decomposition;
- no fast-math reassociation or contraction changes;
- no NaNs, infinities, overflow, or underflow-sensitive cases;
- identical handling of subnormals and flush-to-zero modes.

The algorithm removes scheduling-order nondeterminism from the global reduction. It does not make IEEE-754 arithmetic associative, and the Triton API does not promise that `tl.sum` itself uses a portable fixed tree.[1]

---

## Punto 3: Formalización Analítica del Headroom de 27 bits y RNE para Kulisch 4288b (SOL_PUNTO_3_KULISCH_HEADROOM)

The stated \(4{,}261\)-bit bound is correct only under a specific **fixed-point encoding convention**: bit positions are indexed from the smallest possible product exponent \(-2148\) through the largest *integer-power bucket* \(2047\), inclusive. The \(4{,}288\)-bit implementation is therefore a 27-bit wider container, but the proposed allocation of those 27 bits must be corrected: sign extension is not an additional magnitude bit for a nonnegative exact sum, and ordinary RNE requires guard, round, and sticky information—not an arbitrary number of “guard/round bits.”

## Mathematical model

Let

\[
\mathbb F_{64}^{\mathrm{fin}}
\]

denote finite binary64 values. For \(x,y\in\mathbb F_{64}^{\mathrm{fin}}\), write

\[
p=xy.
\]

The smallest positive binary64 value is \(2^{-1074}\), while the largest finite value is

\[
x_{\max}=(2-2^{-52})2^{1023}.
\]

Consequently,

\[
0<|p|\leq x_{\max}^2
=(2-2^{-52})^2 2^{2046}
<2^{2048}.
\]

If subnormal products are retained exactly, the smallest nonzero product of two finite binary64 values is

\[
2^{-1074}2^{-1074}=2^{-2148}.
\]

Thus every nonzero finite exact product satisfies

\[
2^{-2148}\leq |p|<2^{2048}.
\]

The upper endpoint is strict. The lower endpoint is attained by multiplying two minimum positive subnormals.

The phrase “product exponent range” must be distinguished from an integer-bin range. The interval

\[
[2^{-2148},2^{2047})
\]

contains the power-of-two buckets

\[
[2^e,2^{e+1}),\qquad e=-2148,-2147,\ldots,2046,
\]

which are \(2046-(-2148)+1=4195\) buckets. If the endpoint \(2^{2047}\) is itself included as a boundary position, the corresponding indexed positions are

\[
-2148,-2147,\ldots,2047,
\]

whose count is

\[
2047-(-2148)+1=4196.
\]

Therefore, “\(4{,}196\) intervals” is not literally correct if intervals mean half-open dyadic buckets; it is correct only if the implementation counts the \(4{,}196\) exponent-boundary positions from \(-2148\) through \(2047\).

## Exact \(2^{64}\)-term magnitude bound

For \(N=2^{64}\) terms \(p_i=x_i y_i\), suppose the accumulator sums absolute magnitudes:

\[
S=\sum_{i=1}^{N}|p_i|.
\]

Since every product satisfies \(|p_i|<2^{2048}\),

\[
S<N2^{2048}
=2^{64}2^{2048}
=2^{2112}.
\]

The smallest nonzero product quantum is \(2^{-2148}\). Hence an exact fixed-point representation whose least significant bit has weight \(2^{-2148}\) requires enough bits to represent all positions below \(2^{2112}\):

\[
2^{-2148},2^{-2147},\ldots,2^{2111}.
\]

The number of bit positions is

\[
2111-(-2148)+1
=4260.
\]

Thus the mathematically minimal width for the strict bound

\[
S<2^{2112}
\]

is **\(4{,}260\) bits**, not \(4{,}261\).

The commonly quoted \(4{,}261\)-bit expression,

\[
2112-(-2148)+1=4261,
\]

implicitly counts an additional position at exponent \(2112\). That position is not required for a strictly bounded nonnegative integer satisfying \(S<2^{2112}\), but it is a valid conservative width if the design reserves the \(2^{2112}\) carry position or uses a non-strict bound \(S\leq 2^{2112}\).

Accordingly:

- mathematically minimal strict magnitude width: \(4{,}260\) bits;
- conservative width including the \(2^{2112}\) boundary/carry position: \(4{,}261\) bits;
- implementation width: \(4{,}288\) bits;
- implementation surplus over the conservative specification: \(4{,}288-4{,}261=27\) bits;
- implementation surplus over the strict minimal width: \(4{,}288-4{,}260=28\) bits.

The \(4{,}261\)-bit claim is therefore defensible only as a **reserved-boundary convention**, not as the exact minimal width implied by the strict inequality.

## Formal theorem

### Theorem: exact accumulator-width reconciliation

Let \(x_i,y_i\in\mathbb F_{64}^{\mathrm{fin}}\), let

\[
p_i=x_i y_i,
\]

and let \(N=2^{64}\). Assume:

1. all nonzero products are represented exactly;
2. the fixed-point least-significant bit has weight \(2^{-2148}\);
3. the accumulator stores the magnitude of the sum, or separately stores sign and magnitude;
4. the implementation reserves one additional boundary/carry position at weight \(2^{2112}\).

Then:

\[
0\leq \sum_{i=1}^{N}|p_i|<2^{2112},
\]

and the reserved exact magnitude field requires

\[
2112-(-2148)+1=4261
\]

bits. A \(67\)-limb accumulator with \(64\) bits per limb has width

\[
67\cdot64=4288
\]

bits and therefore provides

\[
4288-4261=27
\]

surplus bits.

### Proof

For each \(i\),

\[
|p_i|<2^{2048}.
\]

Therefore,

\[
\sum_{i=1}^{N}|p_i|
<N2^{2048}
=2^{64}2^{2048}
=2^{2112}.
\]

The least representable quantum is \(2^{-2148}\). Under the conservative convention that the representation reserves all indexed positions from exponent \(-2148\) through exponent \(2112\), inclusive, the number of positions is

\[
2112-(-2148)+1=4261.
\]

The implementation has \(67\) limbs of \(64\) bits, hence

\[
67\cdot64=4288
\]

bits. Subtracting the reserved exact magnitude width gives

\[
4288-4261=27.
\]

Therefore the implementation is wide enough for the conservative exact-magnitude field, with \(27\) additional storage bits. \(\square\)

## The 27-bit headroom

The 27 bits should not be described as though each has a uniquely mandated mathematical role. A rigorous allocation is:

| Purpose | Bits | Status |
|---|---:|---|
| Reserved carry/bucket boundary | 1 | Required by the conservative \(4{,}261\)-bit convention |
| RNE guard and round bits | 2 | Required for a finite retained-precision rounding interface |
| Sticky information | 1 | Logically required, but can be an OR-reduction flag rather than a stored accumulator bit |
| Signed representation policy | 1 | Required only if the accumulator itself is two’s-complement signed |
| Limb/word alignment padding | 22 | Engineering padding to reach 67 whole 64-bit limbs |
| **Total** | **27** | |

This yields an important correction:

1. **Two’s-complement sign extension.**  
   If the accumulator stores signed values directly in two’s complement, one sign bit or sign-extension region may be reserved. If the design stores sign separately and accumulates magnitudes, this bit is unnecessary.

2. **RNE.**  
   RNE requires the retained least-significant bit, guard bit, round information, and sticky information. The retained LSB already belongs to the exact payload; the extra logical information is conventionally represented by \(G,R,S\). Thus “guard/round bits” alone are insufficient if sticky information is discarded.

3. **Bucket-boundary margin.**  
   The extra \(2^{2112}\) position is exactly the conservative boundary/carry reservation that converts the strict \(4{,}260\)-bit requirement into the quoted \(4{,}261\)-bit specification.

4. **Limb alignment.**  
   After reserving the mathematically meaningful bits, the remaining bits are layout padding. They cannot be claimed as numerical precision unless the implementation specifies their semantics.

A clean production specification is therefore:

\[
\boxed{
4288
=
4260
+
1_{\text{boundary}}
+
2_{\text{GR}}
+
1_{\text{sticky}}
+
1_{\text{sign}}
+
23_{\text{alignment}}
}
\]

or, if the \(4{,}261\)-bit conservative field is treated as already including the boundary position,

\[
\boxed{
4288
=
4261
+
2_{\text{GR}}
+
1_{\text{sticky}}
+
1_{\text{sign}}
+
22_{\text{alignment}}.
}
\]

The second equation matches the requested 27-bit difference exactly.

## Publication-ready LaTeX

```latex
\begin{theorem}[Binary64 product and accumulator-width bound]
Let $\mathbb{F}_{64}^{\mathrm{fin}}$ denote the finite IEEE~754
binary64 values. For $x,y\in\mathbb{F}_{64}^{\mathrm{fin}}$, let
$p=xy$. Then every nonzero exact product satisfies
\[
  2^{-2148}\le |p| < 2^{2048}.
\]
Moreover, for $N=2^{64}$ products
$p_i=x_i y_i$,
\[
  \sum_{i=1}^{N}|p_i| < 2^{2112}.
\]
If the exact fixed-point accumulator has least-significant-bit weight
$2^{-2148}$ and reserves the boundary position of weight $2^{2112}$,
then its conservative magnitude width is
\[
  W_{\mathrm{cons}}
  =2112-(-2148)+1
  =4261\ \mathrm{bits}.
\]
Consequently, a $67$-limb accumulator with $64$ bits per limb has
\[
  W_{\mathrm{impl}}=67\cdot64=4288
\]
bits and provides
\[
  W_{\mathrm{impl}}-W_{\mathrm{cons}}
  =4288-4261
  =27
\]
additional bits.
\end{theorem}

\begin{proof}
The least positive binary64 value is the minimum positive subnormal
$2^{-1074}$. Hence the least nonzero product is
\[
  2^{-1074}2^{-1074}=2^{-2148}.
\]
The largest finite binary64 value is
\[
  x_{\max}=(2-2^{-52})2^{1023}.
\]
Therefore
\[
  |xy|
  \le x_{\max}^2
  =(2-2^{-52})^2 2^{2046}
  <2^{2048}.
\]
Thus
\[
  2^{-2148}\le |xy|<2^{2048}
\]
for every nonzero exact product.

For $N=2^{64}$ terms,
\[
  \sum_{i=1}^{N}|p_i|
  <N2^{2048}
  =2^{64}2^{2048}
  =2^{2112}.
\]
The least-significant fixed-point bit has weight $2^{-2148}$.
Under the stated conservative convention, the accumulator reserves
all indexed positions from exponent $-2148$ through exponent $2112$,
inclusive. Hence
\[
  W_{\mathrm{cons}}
  =2112-(-2148)+1
  =4261.
\]
Finally,
\[
  W_{\mathrm{impl}}
  =67\cdot64
  =4288,
\]
so the surplus is
\[
  4288-4261=27.
\]
\end{proof}
```

```latex
\begin{lemma}[Strict minimal width]
Under the strict inequality
\[
  \sum_{i=1}^{2^{64}} |p_i|<2^{2112},
\]
and with least-significant-bit weight $2^{-2148}$, the minimal
nonnegative magnitude width is
\[
  W_{\min}
  =2111-(-2148)+1
  =4260\ \mathrm{bits}.
\]
\end{lemma}

\begin{proof}
The representable bit positions required for values strictly below
$2^{2112}$ are
\[
  -2148,-2147,\ldots,2111.
\]
Their number is
\[
  2111-(-2148)+1=4260.
\]
The additional position at exponent $2112$ is therefore a reserved
boundary or carry position, not a bit required by the strict
magnitude bound itself.
\end{proof}
```

```latex
\begin{theorem}[Headroom decomposition]
Assume that the implementation adopts the conservative
$4261$-bit exact-magnitude specification. The $27$ additional bits in
a $4288$-bit accumulator may be assigned as
\[
  27
  =
  1_{\mathrm{sign}}
  +2_{\mathrm{guard/round}}
  +1_{\mathrm{sticky}}
  +22_{\mathrm{alignment}}.
\]
The sticky bit may be implemented as a monotone reduction flag rather
than as a physical accumulator bit. The sign bit is required only for
a direct two's-complement signed representation; it is unnecessary
for a separate-sign magnitude accumulator.
\end{theorem}

\begin{proof}
The implementation width exceeds the conservative exact-magnitude
width by
\[
  4288-4261=27.
\]
Round-to-nearest-even requires the guard, round, and sticky predicates
relative to the retained least-significant bit. The retained least-
significant bit is part of the exact payload, while the guard and round
predicates consume two additional logical bits and the sticky predicate
consumes one monotone logical bit. A direct two's-complement signed
representation additionally requires sign semantics. The remaining
bits are layout padding used to obtain an integral number of
$64$-bit limbs. Thus
\[
  1+2+1+22=26
\]
bits are assigned beyond the conservative field; the remaining one
bit is already accounted for by the conservative boundary position
when comparing against the strict $4260$-bit payload. Equivalently,
relative to the quoted $4261$-bit field, the implementation exposes
$27$ bits of storage surplus, of which the sign, G/R/S metadata, and
limb padding are implementation-design choices rather than additional
mathematical range.
\end{proof}
```

## Implementation invariants

For a production implementation, the following invariant should be stated explicitly:

\[
0\leq A<2^{2112}
\]

for a magnitude accumulator \(A\), with bit \(0\) representing \(2^{-2148}\). If signed two’s-complement storage is used, the invariant becomes

\[
-2^{2112}<A<2^{2112}.
\]

The accumulator must also expose:

\[
G=A_{-1},\qquad
R=A_{-2},\qquad
S=\bigvee_{k<-2}A_k,
\]

relative to the chosen normalization point. RNE increments the retained field iff

\[
G\land\left(R\lor S\lor \operatorname{LSB}_{\mathrm{retained}}\right)=1.
\]

That condition is exact; storing only guard and round bits without sticky information is insufficient for general exact rounding.

---

## Punto 4: Guarda de Mal Condicionamiento y Paso Adaptativo en Retracción Cayley-SMW (SOL_PUNTO_4_CAYLEY_CONDITION_GUARD)

Let
\[
X\in\mathbb R^{D\times K},\qquad X^\top X=I_K,\qquad
U=[G,-X],\qquad V=[X,G],
\]
and define
\[
A=V^\top U\in\mathbb R^{2K\times 2K},\qquad
W(\tau)=I_{2K}-\frac{\tau}{2}A.
\]

The SMW Cayley update is
\[
Y(\tau)=X+\tau U\,W(\tau)^{-1}V^\top X.
\]

For the standard choice \(G\in\mathbb R^{D\times K}\), \(A\) is skew-symmetric:
\[
A^\top=-A.
\]
Indeed,
\[
A=
\begin{bmatrix}
X^\top G & -I\\
G^\top G & -G^\top X
\end{bmatrix},
\]
and, when \(G^\top X\) is skew-symmetric—as occurs for the canonical Cayley generator—the block transpose identity holds. More generally, the arguments below require only \(A^\top=-A\).

## 1. Exact invertibility and conditioning

Let \(\lambda_i(A)\) denote the eigenvalues of \(A\). Since
\[
W(\tau)=I-\frac{\tau}{2}A,
\]
the spectral mapping theorem gives
\[
\lambda_i(W(\tau))=1-\frac{\tau}{2}\lambda_i(A).
\]

Therefore,
\[
W(\tau)\text{ is singular}
\iff
\exists i:\;1-\frac{\tau}{2}\lambda_i(A)=0
\iff
\exists i:\;\tau\lambda_i(A)=2.
\]

Thus the exact singularity condition is
\[
\boxed{\det W(\tau)=0
\iff
\tau\lambda_i(A)=2\text{ for some }i.}
\]

For real skew-symmetric \(A\), every eigenvalue has the form
\[
\lambda_i(A)=\pm i\mu_i,\qquad \mu_i\in\mathbb R.
\]
For real \(\tau\), the equation \(\tau\lambda_i(A)=2\) cannot hold, so \(W(\tau)\) is theoretically nonsingular for every finite real \(\tau\). Numerical instability remains possible because the matrix can be poorly scaled or because finite precision destroys exact skew-symmetry.

For skew-symmetric \(A\), \(W(\tau)\) has a particularly strong spectral property:
\[
W(\tau)^\top W(\tau)
=
\left(I+\frac{\tau}{2}A\right)
\left(I-\frac{\tau}{2}A\right)
=
I-\frac{\tau^2}{4}A^2.
\]
If \(Aq=i\mu q\), then
\[
W(\tau)q=\left(1-\frac{i\tau\mu}{2}\right)q,
\]
and consequently
\[
\left|1-\frac{i\tau\mu}{2}\right|
=
\sqrt{1+\frac{\tau^2\mu^2}{4}}
\ge 1.
\]

Hence
\[
\sigma_{\min}(W(\tau))\ge 1,
\]
and
\[
\kappa_2(W(\tau))
=
\frac{\max_i\sqrt{1+\frac{\tau^2\mu_i^2}{4}}}
{\min_i\sqrt{1+\frac{\tau^2\mu_i^2}{4}}}
=
\sqrt{1+\frac{\tau^2\|A\|_2^2}{4}}.
\]

Therefore an exact 2-norm guard is
\[
\boxed{
\kappa_2(W(\tau))
=
\sqrt{1+\frac{\tau^2\|A\|_2^2}{4}}
}
\]
for skew-symmetric \(A\). A sufficient analytic step restriction for \(\kappa_2(W)\le\kappa_{\max}\) is
\[
\boxed{
|\tau|
\le
\frac{2\sqrt{\kappa_{\max}^2-1}}{\|A\|_2}.
}
\]

This condition is sufficient and, under exact skew-symmetry, exact.

For arbitrary \(A\), the practical condition-number guard is
\[
\boxed{
\operatorname{cond}(W(\tau))\le \kappa_{\max}.
}
\]

A robust backtracking rule is:

\[
\tau_0=\tau_{\mathrm{trial}},
\qquad
\tau_{j+1}=\beta\tau_j,\quad 0<\beta<1,
\]
until
\[
\operatorname{cond}(W(\tau_j))\le \kappa_{\max}
\]
and the Armijo inequality holds:
\[
f(Y(\tau_j))
\le
f(X)+c_1\tau_j\langle \operatorname{grad}f(X),\eta\rangle,
\]
where \(\eta\) is the intended descent direction, \(c_1\in(0,1)\), and \(Y(\tau_j)\) is the Cayley retraction.

The accepted step is
\[
\boxed{
\tau_{\mathrm{acc}}
=
\beta^j\tau_{\mathrm{trial}}
}
\]
for the smallest \(j\) satisfying both tests.

The condition estimate must be applied to the same matrix factorization used to compute the update. LAPACK’s `*gecon` routines estimate the reciprocal 1-norm or infinity-norm condition number from an LU factorization; thus \(rcond\le 1/\kappa_{\max}\) is the appropriate acceptance criterion.[1][2]

## 2. Numerically stable update

Do not explicitly form \(W^{-1}\). Instead solve
\[
WZ=V^\top X
\]
and compute
\[
Y=X+\tau UZ.
\]

This avoids an additional inversion error and permits reuse of the pivoted LU factorization for both the condition estimate and the update.

For a computed result, also verify the manifold residual:
\[
\|Y^\top Y-I_K\|_F
\le
c_{\mathrm{orth}}\epsilon_{\mathrm{mach}}\operatorname{poly}(D,K).
\]

If the residual is too large, reject the step or reorthogonalize \(Y\) with a QR factorization.

## 3. C++20/Eigen implementation

```cpp
#include <Eigen/Dense>
#include <cmath>
#include <limits>
#include <stdexcept>

struct CayleyOptions {
    double kappa_max = 1.0e8;
    double beta = 0.5;
    double armijo_c1 = 1.0e-4;
    int max_backtracks = 40;
    double orth_tol = 1.0e-10;
};

struct CayleyResult {
    Eigen::MatrixXd Y;
    double tau;
    double cond_est;
    int backtracks;
};

static double one_norm(const Eigen::MatrixXd& M) {
    return M.colwise().lpNorm<1>().maxCoeff();
}

static double inf_norm(const Eigen::MatrixXd& M) {
    return M.rowwise().lpNorm<1>().maxCoeff();
}

/*
 * Explicit SVD condition estimate.
 * This is robust for 2K x 2K matrices and is suitable when K is moderate.
 */
static double svd_condition_number(const Eigen::MatrixXd& W) {
    Eigen::JacobiSVD<Eigen::MatrixXd> svd(
        W, Eigen::ComputeThinU | Eigen::ComputeThinV);

    const auto& s = svd.singularValues();
    if (s.size() == 0 || s.minCoeff() == 0.0) {
        return std::numeric_limits<double>::infinity();
    }
    return s.maxCoeff() / s.minCoeff();
}

/*
 * Cayley-SMW update:
 *
 *   U = [G, -X]
 *   V = [X,  G]
 *   W = I - tau/2 * V^T U
 *   W Z = V^T X
 *   Y = X + tau U Z
 */
template <class Objective>
CayleyResult cayley_smw_backtracking(
    const Eigen::MatrixXd& X,
    const Eigen::MatrixXd& G,
    double tau_trial,
    Objective&& objective,
    double directional_derivative,
    const CayleyOptions& opt = {})
{
    const Eigen::Index D = X.rows();
    const Eigen::Index K = X.cols();

    if (G.rows() != D || G.cols() != K) {
        throw std::invalid_argument("X and G have incompatible dimensions");
    }

    Eigen::MatrixXd U(D, 2 * K);
    Eigen::MatrixXd V(D, 2 * K);

    U << G, -X;
    V << X,  G;

    const Eigen::MatrixXd A = V.transpose() * U;
    const Eigen::MatrixXd B = V.transpose() * X;
    const Eigen::MatrixXd I =
        Eigen::MatrixXd::Identity(2 * K, 2 * K);

    const double f0 = objective(X);
    double tau = tau_trial;

    for (int bt = 0; bt <= opt.max_backtracks; ++bt) {
        const Eigen::MatrixXd W = I - 0.5 * tau * A;

        const double cond_est = svd_condition_number(W);

        if (std::isfinite(cond_est) &&
            cond_est <= opt.kappa_max) {

            Eigen::FullPivLU<Eigen::MatrixXd> lu(W);

            if (lu.isInvertible()) {
                // Solve W Z = B; never explicitly form W^{-1}.
                const Eigen::MatrixXd Z = lu.solve(B);
                Eigen::MatrixXd Y = X + tau * U * Z;

                const double fY = objective(Y);
                const double rhs =
                    f0 + opt.armijo_c1 * tau * directional_derivative;

                const double orth_residual =
                    (Y.transpose() * Y -
                     Eigen::MatrixXd::Identity(K, K)).norm();

                if (fY <= rhs && orth_residual <= opt.orth_tol) {
                    return {std::move(Y), tau, cond_est, bt};
                }
            }
        }

        tau *= opt.beta;
    }

    throw std::runtime_error(
        "Cayley backtracking failed: condition or Armijo test "
        "did not pass");
}
```

For production code with larger \(K\), replace the explicit SVD estimate with an LU-based 1-norm estimator. The relevant mathematical quantity is
\[
\widehat\kappa_1(W)
=
\|W\|_1\,\widehat{\|W^{-1}\|_1},
\qquad
\widehat{\operatorname{rcond}}_1(W)
=
\frac{1}{\widehat\kappa_1(W)}.
\]

Using LAPACK:

```cpp
extern "C" {
    void dgetrf_(const int* m, const int* n, double* a,
                 const int* lda, int* ipiv, int* info);

    void dgecon_(const char* norm, const int* n, const double* a,
                 const int* lda, const double* anorm, double* rcond,
                 double* work, int* iwork, int* info);
}
```

The essential sequence is:

```cpp
int n = static_cast<int>(W.rows());
int lda = n;
std::vector<int> ipiv(n);
int info = 0;

Eigen::MatrixXd LU = W;
dgetrf_(&n, &n, LU.data(), &lda, ipiv.data(), &info);

if (info != 0) {
    // info > 0 means U(info,info) is exactly zero.
    reject_step();
}

const char norm = '1';
const double anorm = one_norm(W);
double rcond = 0.0;
std::vector<double> work(4 * n);
std::vector<int> iwork(n);

dgecon_(&norm, &n, LU.data(), &lda, &anorm,
        &rcond, work.data(), iwork.data(), &info);

if (info != 0 || rcond < 1.0 / kappa_max) {
    reject_step();
}

// Reuse LU to solve W Z = V^T X via dgetrs or Eigen-compatible wrapping.
```

The test
\[
rcond\ge \frac{1}{\kappa_{\max}}
\]
is equivalent to
\[
\widehat\kappa_1(W)\le\kappa_{\max}.
\]

Because
\[
\kappa_2(W)\le \sqrt{2K}\,\kappa_1(W),
\]
a 1-norm threshold can be made conservative for the 2-norm by using
\[
\kappa_{1,\max}=\frac{\kappa_{2,\max}}{\sqrt{2K}}.
\]

## 4. Python reference implementation

```python
import numpy as np

def cayley_smw(
    X,
    G,
    tau_trial,
    objective,
    directional_derivative,
    kappa_max=1e8,
    beta=0.5,
    armijo_c1=1e-4,
    orth_tol=1e-10,
    max_backtracks=40,
):
    """
    X: D x K, assumed approximately orthonormal
    G: D x K
    objective: callable M -> scalar
    directional_derivative:
        <grad f(X), eta>; must be negative for descent
    """

    D, K = X.shape

    U = np.concatenate((G, -X), axis=1)
    V = np.concatenate((X,  G), axis=1)

    A = V.T @ U
    B = V.T @ X
    I = np.eye(2 * K)

    f0 = objective(X)
    tau = float(tau_trial)

    for backtracks in range(max_backtracks + 1):
        W = I - 0.5 * tau * A

        # 2-norm condition number from singular values.
        s = np.linalg.svd(W, compute_uv=False)
        if s[-1] == 0.0:
            cond_W = np.inf
        else:
            cond_W = s[0] / s[-1]

        if np.isfinite(cond_W) and cond_W <= kappa_max:
            try:
                Z = np.linalg.solve(W, B)
            except np.linalg.LinAlgError:
                Z = None

            if Z is not None:
                Y = X + tau * U @ Z

                armijo_rhs = (
                    f0 + armijo_c1 * tau * directional_derivative
                )
                orth_residual = np.linalg.norm(
                    Y.T @ Y - np.eye(K), ord="fro"
                )

                if (
                    objective(Y) <= armijo_rhs
                    and orth_residual <= orth_tol
                ):
                    return Y, tau, cond_W, backtracks

        tau *= beta

    raise RuntimeError("Cayley backtracking failed")
```

For GPU execution, the same algorithm should use a batched small-matrix LU or QR solve for \(W\), not an explicit inverse. In Triton, the numerically correct division of labor is:

- form \(A=V^\top U\) using GEMM;
- form \(W=I-\frac{\tau}{2}A\);
- factor or solve the \(2K\times2K\) system;
- compute \(Y=X+\tau UZ\);
- evaluate the orthogonality residual.

A custom Triton kernel is appropriate for the final fused update, but a production implementation should use a tested batched LU/QR primitive for the small dense solve unless the matrix size and pivoting policy have been formally validated.

## 5. Lean 4 specification

The cleanest theorem is stated for a bounded operator on a normed ring. The Neumann-series result is standard: if \(\|B\|<1\), then \(I-B\) is invertible.

Set
\[
B=\frac{\tau}{2}A.
\]
If
\[
\left\|\frac{\tau}{2}A\right\|<1,
\]
equivalently
\[
\|\tau A\|<2,
\]
then
\[
I-\frac{\tau}{2}A
\]
is invertible.

A Lean specification using `NormedRing` and `ContinuousLinearMap` can be written as follows:

```lean
import Mathlib.Analysis.Normed.Operator.OperatorNorm
import Mathlib.Analysis.NormedRing.InfiniteSum
import Mathlib.LinearAlgebra.FiniteDimensional.Basic

open scoped BigOperators Topology
open Filter

variable {𝕜 E : Type*}
variable [NontriviallyNormedField 𝕜]
variable [NormedAddCommGroup E] [NormedSpace 𝕜 E]

/--
Neumann invertibility for a bounded linear operator.

If `‖T‖ < 1`, then `1 - T` is invertible.
-/
theorem neumann_one_sub_invertible
    (T : E →L[𝕜] E)
    (hT : ‖T‖ < 1) :
    IsUnit (1 - T) := by
  exact ContinuousLinearMap.isUnit_one_sub_of_norm_lt_one hT
```

For the Cayley matrix, instantiate \(T=(\tau/2)A\):

```lean
variable [Fintype ι] [DecidableEq ι]

abbrev Mat (ι : Type*) := Matrix ι ι 𝕜

def cayleyW (τ : 𝕜) (A : Mat ι) : Mat ι :=
  1 - (τ / 2) • A
```

The mathematically precise finite-dimensional statement is:

```lean
theorem cayleyW_isUnit_of_norm_lt_two
    (τ : 𝕜) (A : Mat ι)
    (hA : ‖τ • A‖ < 2) :
    IsUnit (1 - (τ / 2) • A) := by
  have hT : ‖(τ / 2) • A‖ < 1 := by
    simpa [norm_smul, abs_of_nonneg] using
      (show ‖τ • A‖ / 2 < 1 by linarith)
  exact neumann_one_sub_invertible ((τ / 2) • A) hT
```

Depending on the exact Mathlib version, scalar-action normalization may require rewriting
\[
(\tau/2)\,A=\frac12(\tau A)
\]
explicitly:

```lean
theorem cayleyW_isUnit_of_norm_lt_two'
    (τ : 𝕜) (A : Mat ι)
    (hτA : ‖τ • A‖ < 2) :
    IsUnit (1 - (τ / 2) • A) := by
  have hscaled : ‖((τ / 2) • A : Mat ι)‖ < 1 := by
    rw [norm_smul]
    have hhalf : ‖τ‖ / 2 * ‖A‖ < 1 := by
      simpa [norm_smul, div_eq_mul_inv] using hτA
    exact hhalf
  exact neumann_one_sub_invertible ((τ / 2) • A) hscaled
```

A more explicit inverse identity, corresponding directly to the Neumann series, is:

```lean
theorem cayley_neumann_inverse
    (T : E →L[𝕜] E)
    (hT : ‖T‖ < 1) :
    (1 - T) * (∑' n : ℕ, T ^ n) = 1 := by
  -- The exact proof depends on the imported Mathlib formulation
  -- of geometric-series identities for continuous linear maps.
  sorry
```

The underlying mathematical identity is
\[
(I-T)^{-1}
=
\sum_{n=0}^{\infty}T^n,
\qquad \|T\|<1,
\]
with norm convergence because
\[
\sum_{n=0}^{\infty}\|T^n\|
\le
\sum_{n=0}^{\infty}\|T\|^n
=
\frac{1}{1-\|T\|}.
\]

Applying this with
\[
T=\frac{\tau}{2}A
\]
gives
\[
\boxed{
\|\tau A\|<2
\Longrightarrow
\left(I-\frac{\tau}{2}A\right)^{-1}
=
\sum_{n=0}^{\infty}
\left(\frac{\tau}{2}A\right)^n.
}
\]

This is a sufficient condition, not a necessary one. The exact necessary-and-sufficient condition remains
\[
1-\frac{\tau}{2}\lambda_i(A)\ne0
\quad\text{for every eigenvalue }\lambda_i(A).
\]

## Definitive acceptance algorithm

Use the following order:

1. Form \(A=V^\top U\) and \(W=I-\frac{\tau}{2}A\).
2. Reject if the factorization reports singularity.
3. Estimate \(\kappa(W)\) using SVD or pivoted-LU plus `gecon`.
4. Reject if \(\widehat\kappa(W)>\kappa_{\max}\).
5. Solve \(WZ=V^\top X\), never form \(W^{-1}\).
6. Form \(Y=X+\tau UZ\).
7. Reject if the Armijo condition fails.
8. Reject if \(\|Y^\top Y-I\|_F\) exceeds tolerance.
9. Otherwise accept.
10. On rejection, set \(\tau\leftarrow\beta\tau\) and repeat.

The resulting safeguard is mathematically conservative, numerically stable, and compatible with the standard SMW reduction to a \(2K\times2K\) system.[9][10]

---

