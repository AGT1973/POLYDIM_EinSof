The measurements are internally plausible, but they do **not** establish a race-free or cleanly terminated protocol. The critical distinction is that CUDA IPC exports a mapping capability—not ownership, synchronization, or lifetime protection.

## 1. TOCTOU and 16 concurrent reader streams

`cudaIpcGetMemHandle()` is not a snapshot of the allocation’s contents. It produces a process-transferable handle for an existing allocation; the importing process obtains its own valid device pointer through `cudaIpcOpenMemHandle()`.[1]

There is no intrinsic TOCTOU race between one `cudaIpcGetMemHandle()` call and multiple `cudaIpcOpenMemHandle()` calls if all of the following remain true:

- The exporting allocation remains allocated.
- The exporter does not reuse, resize, or free the allocation.
- The handle is transferred intact.
- The importer opens it in a compatible CUDA context.
- The producer and consumers synchronize access to the data.

Sixteen reader **streams** are not sixteen IPC mappings. CUDA streams are execution-ordering entities; they do not independently open the handle. A single importer process/context can open the handle once, then issue work on 16 streams. CUDA’s runtime restrictions state that an IPC memory handle from a device may be opened by only one context per device per importing process; repeated opens in that context increase the handle reference count and return the existing pointer.[6]

The actual races are these:

- **Free-after-export:** the producer calls `cudaFree()` while any importer may still dereference the mapping. This is undefined behavior; the exporter must not free the allocation until all importers have closed their mappings.[8]
- **Reuse-after-free:** the producer frees the allocation and allocates another object at the same address. An importer can then access memory whose logical ownership and contents have changed.
- **Publication race:** the consumer begins reading before the producer’s writes are visible. IPC handle creation does not publish completed writes.
- **Completion race:** the producer reuses or overwrites the buffer before all 16 reader streams finish.
- **Close race:** `cudaIpcCloseMemHandle()` occurs before all queued work in the importing context that uses the pointer has completed.
- **Descriptor race:** a consumer reads a wire descriptor before the descriptor and allocation metadata are fully committed.

A sound protocol requires explicit state transitions, for example:

1. Producer allocates and initializes the buffer.
2. Producer records a completion event after the final write.
3. Consumer receives the descriptor and opens the handle.
4. Consumer waits for producer completion before issuing reads.
5. Consumer records completion after all 16 streams finish.
6. Producer waits for every consumer completion acknowledgment.
7. Consumers synchronize their relevant streams, then call `cudaIpcCloseMemHandle()`.
8. Producer destroys the event, frees the allocation, and exits.

For cross-process CUDA event synchronization, use an interprocess-capable event exported with `cudaIpcGetEventHandle()` rather than assuming host-message ordering implies device-memory visibility. Host acknowledgments should be treated as protocol messages, not as substitutes for CUDA stream/event ordering.

Also distinguish **one importing process with 16 streams** from **16 importing processes**. The latter requires separate lifecycle accounting and is more error-prone. Every importer must close its mapping, and the producer must retain the allocation until all consumers have acknowledged closure.

## 2. Meaning of the `CudaIPCTypes.cpp:16` warning

The warning means that the producer process exited while PyTorch still believed that one or more CUDA tensors exported through its CUDA-sharing machinery were alive in consumer processes. It is a lifetime violation, not evidence that the data was corrupted:

> “Producer process has been terminated before all shared CUDA tensors released.”[3]

PyTorch’s CUDA IPC design requires the sending process to remain alive while the receiving process retains the shared CUDA tensor. The consumer must release its reference before the producer exits.[5] `torch.cuda.ipc_collect()` can force cleanup of released IPC allocations, but it cannot make live consumer references safe after producer termination.[4]

A clean teardown protocol is:

**Producer**

- Stop publishing new descriptors.
- Send an explicit end-of-stream or shutdown message.
- Continue servicing acknowledgments.
- Wait until every consumer reports that it has:
  - synchronized all streams using the mapping,
  - destroyed tensor views,
  - released references,
  - closed the imported mapping.
- Optionally invoke `torch.cuda.ipc_collect()` after consumers have released their references.
- Synchronize the producer’s relevant streams.
- Destroy IPC events and free the original allocation.
- Only then terminate.

**Consumer**

- Stop accepting new work after shutdown.
- Synchronize every stream that touched the imported pointer.
- Destroy all tensor aliases and views, including hidden references held by queues, futures, callbacks, caches, and framework objects.
- Call `cudaIpcCloseMemHandle()` exactly once per corresponding open/reference.
- Send an acknowledgment only after those operations complete.
- Remain alive until the producer confirms teardown, unless the protocol explicitly supports abnormal consumer death.

Do not rely on Python garbage collection timing. Use explicit ownership objects and deterministic shutdown. In PyTorch, avoid creating CUDA tensors inside ordinary `DataLoader` workers; worker termination while those tensors remain referenced is a common trigger for this warning.[3][7]

A particularly important audit point is whether the protocol combines **raw CUDA IPC mappings** with **PyTorch CUDA tensor sharing**. Those are separate lifetime systems. A raw `cudaIpcCloseMemHandle()` does not necessarily release PyTorch’s tensor-level IPC reference, and destroying a Python tensor does not necessarily close a separately managed raw CUDA mapping. The protocol must document which layer owns each reference.

## 3. Is 9.03 GB/s plausible on PCIe Gen3 x16 with `can_device_access_peer == False`?

Yes. It is plausible, but the result should not be described as native GPU-to-GPU P2P bandwidth.

`cudaDeviceCanAccessPeer == false` means CUDA cannot establish direct peer virtual-address access between those devices in the relevant topology/context. Consequently, the transfer path is generally staged through host-visible memory or uses a CUDA-supported fallback path rather than direct peer memory access. The exact implementation depends on the driver, runtime, topology, allocation type, and transfer API.

PCIe Gen3 x16 has a theoretical signaling rate of about 15.75 GB/s after 128b/130b encoding, before protocol overhead, transaction inefficiency, software overhead, and any staging copies. A measured 9.03 GB/s is therefore compatible with:

- PCIe protocol overhead;
- host staging;
- pageable or insufficiently optimized host-memory behavior;
- NUMA/root-complex placement;
- synchronization and launch overhead;
- smaller transfers or non-pipelined batches;
- an additional device-to-host or host-to-device leg;
- measurement methodology that includes setup or latency.

The reported 0.825 ms latency is also consistent with a path involving synchronization and staging, but it cannot be interpreted without transfer size, direction, warm-up policy, stream usage, and timing method.

The result should be reported as:

> “Measured inter-device transfer throughput under the tested non-P2P PCIe topology: 9.03 GB/s.”

It should **not** be reported as:

> “T4 VRAM-to-VRAM bandwidth” or “PCIe Gen3 x16 saturation.”

To audit the claim, measure separately:

- device 0 → pinned host;
- pinned host → device 1;
- device 0 → device 1 through the chosen API;
- reverse direction;
- multiple concurrent transfers;
- pageable versus pinned host memory;
- synchronous versus asynchronous copies;
- transfer sizes large enough to amortize setup;
- topology and NUMA affinity using `nvidia-smi topo -m`.

Also verify that the benchmark does not include producer-side synchronization, IPC opening, descriptor transmission, or consumer-side synchronization in the bandwidth numerator.

## 4. Why FP64 `tl.atomic_add` reaches 139.78 GB/s instead of 320 GB/s

The 320 GB/s figure is the nominal external GDDR6 memory bandwidth of the Tesla T4, not an unconditional application-level throughput ceiling. It assumes sufficiently parallel, coalesced, mostly streaming accesses with limited serialization and favorable instruction mix.

An FP64 atomic add is a read-modify-write operation with substantially different behavior:

- Each atomic update requires a memory-side read-modify-write transaction.
- Updates to the same address or cache line serialize.
- Atomic throughput is limited by the relevant atomic pipelines, memory partitions, cache behavior, and contention—not merely by DRAM pin bandwidth.
- FP64 atomic support on the target architecture is much less favorable than ordinary FP32/FP64 loads and stores.
- The operation performs arithmetic and synchronization in addition to data movement.
- A naïve bandwidth calculation may count only 8 bytes written, whereas the hardware transaction involves reading and updating a line and may incur writeback/coherence traffic.
- Kernel launch, synchronization, and timing methodology can depress the reported effective rate.
- If the reduction accumulates into a small number of locations, contention dominates and the kernel is fundamentally serialization-bound.

Thus \(139.78/320 \approx 43.7\%\) of nominal peak is not surprising for a contended FP64 atomic reduction. It does not indicate that the T4’s GDDR6 is defective or that the kernel is “using SRAM bandwidth.” “SRAM reduction” is potentially misleading: registers, shared memory, L2, and global-memory atomic paths have distinct bandwidth and serialization characteristics. `tl.atomic_add` ultimately targets the address space selected by the pointer; it does not automatically convert a global-memory reduction into a shared-memory reduction.

The timing also needs scrutiny. For \(D=10^7\) FP64 values, the input alone is 80 MB. At 320 GB/s, the idealized one-pass load lower bound is about 250 µs, excluding reduction stores, atomics, synchronization, and execution overhead. A measured 572.32 µs corresponds to roughly 140 GB/s for one 80 MB stream, which is credible for an atomic reduction but does not isolate the atomic operation’s cost.

For a defensible roofline analysis, report at least:

- achieved DRAM read and write bytes using a stated accounting convention;
- number and distribution of atomic destinations;
- contention factor;
- occupancy and register/shared-memory usage;
- achieved memory throughput from hardware counters;
- comparison against a non-atomic copy or reduction;
- comparison against hierarchical reduction: per-thread registers → warp reduction → shared memory → one global atomic;
- whether accumulation is one global scalar, one value per block, or many independent bins.

The strongest optimization is normally hierarchical reduction: eliminate most global FP64 atomics, reduce within warps and blocks, and perform only a small number of final global atomic operations. The 139.78 GB/s result is therefore best characterized as an **effective throughput for this particular atomic reduction kernel**, not a measurement of T4 memory-bandwidth utilization or an SRAM roofline.

## Bottom-line audit verdict

- **Bitwise equality** validates the tested result, not synchronization correctness under adversarial scheduling.
- **9.03 GB/s** is plausible for a non-P2P PCIe fallback, but requires a precise path and timing definition.
- **The warning is a real teardown defect** unless it was deliberately produced by forced process termination after all useful work; clean protocols must keep the producer alive until every consumer releases its references.
- **Sixteen streams do not remove the need for lifetime and data-ordering protocol state.**
- **139.78 GB/s** is plausible for a contended FP64 atomic reduction and should not be compared directly with nominal 320 GB/s as though both measured the same operation.
- CUDA explicitly requires imported mappings to be closed and prohibits freeing the exported allocation while imports remain active.[6][8]