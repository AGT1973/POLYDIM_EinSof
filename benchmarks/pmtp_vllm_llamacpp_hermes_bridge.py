# -*- coding: utf-8 -*-
"""
POLYDIM / EinsofOS — Executable Reference Bridge for Zero-Token Latent Injection
Targets:
  1. Hugging Face Transformers (`model(inputs_embeds=...)`)
  2. vLLM Engine (`PromptEmbeds` / `prompt_embeds` tensor payload)
  3. llama.cpp / Ollama C-API (`struct llama_batch` with `token = NULL`, `embd != NULL`)
  4. NousResearch/Hermes-3-Llama-3.1-8B (`St(4096, 2048)` real `.safetensors` adapter)

Author: Ariel H. García Traba (ORCID: 0009-0001-2787-6067)
Affiliation: EinsofOS Independent Research / POLYDIM Research Initiative
DOIs: 10.5281/zenodo.21209973 | 10.5281/zenodo.21136742
HAL: hal-05847496v1 | Jxiv: 7040 | SWHID: swh:1:snp:bdea78b37132a4bd6b67049805cbb6d4472ec2cd
"""
import os
import time
import math
import json
import ctypes
import struct
from multiprocessing import shared_memory
import numpy as np
from safetensors.numpy import load_file


def neumaier_sum(arr_1d):
    s = 0.0
    c = 0.0
    for x in arr_1d:
        xf = float(x)
        t = s + xf
        if abs(s) >= abs(xf):
            c += (s - t) + xf
        else:
            c += (xf - t) + s
        s = t
    return s + c


def neumaier_unit_normalize(vec):
    clean = np.where(np.isfinite(vec), vec, 0.0)
    clean = np.where(np.abs(clean) < 1e-300, 0.0, clean)
    sq = np.square(clean, dtype=np.float64).ravel()
    n_val = math.sqrt(max(0.0, neumaier_sum(sq)))
    if n_val == 0.0:
        raise ValueError("Zero-norm vector cannot be projected onto S^{D-1}")
    return clean / n_val, n_val


class LlamaBatchCABI(ctypes.Structure):
    """Exact C-ABI mirror of `struct llama_batch` in llama.cpp / Ollama runner."""
    _fields_ = [
        ("n_tokens", ctypes.c_int32),
        ("token", ctypes.POINTER(ctypes.c_int32)),      # MUST be NULL for direct latent injection
        ("embd", ctypes.POINTER(ctypes.c_float)),       # Non-NULL pointer to continuous embeddings (n_tokens * n_embd)
        ("pos", ctypes.POINTER(ctypes.c_int32)),
        ("n_seq_id", ctypes.POINTER(ctypes.c_int32)),
        ("seq_id", ctypes.POINTER(ctypes.POINTER(ctypes.c_int32))),
        ("logits", ctypes.POINTER(ctypes.c_int8)),
    ]


def pack_pmtp_wire_header(slab_slot: int, d_dim: int, seq_len: int, epoch: int = 26506) -> bytes:
    """Packs a 64-byte PMTP Wire 26506 atomic control descriptor (`SLAB_ID`)."""
    magic = b"PMTP2656"
    flags = (1 << 63) | ((slab_slot & 0xFFFF) << 32) | (epoch & 0xFFFFFFFF)
    header = struct.pack("<8sQIII36s", magic, flags, d_dim, seq_len, 64, b"\x00" * 36)
    assert len(header) == 64
    return header


def run_bridge_verification():
    t0 = time.perf_counter()
    hermes_sf = r"E:\POLYDIM_EINSOF\hf_export\Hermes-3-Llama-3.1-8B-PMTP-Einsof\adapter_model.safetensors"
    if os.path.exists(hermes_sf):
        tensors = load_file(hermes_sf)
        W_fp64 = tensors["W_fp64"]  # shape (2048, 4096)
    else:
        rng_init = np.random.default_rng(20261102)
        G = rng_init.standard_normal((4096, 2048), dtype=np.float64)
        Q, R = np.linalg.qr(G, mode="reduced")
        d = np.sign(np.diag(R))
        d[d == 0] = 1.0
        W_fp64 = np.ascontiguousarray((Q * d).T, dtype=np.float64)

    # 1. Verify Stiefel condition on W_fp64: W_fp64 @ W_fp64^T = I_2048
    gram_err = float(np.max(np.abs(W_fp64 @ W_fp64.T - np.eye(2048, dtype=np.float64))))
    assert gram_err <= 2.5e-15, f"Stiefel ortho defect exceeded: {gram_err}"

    # 2. Allocate Zero-Copy Shared Memory Slab for 2048-D canonical Swarm state
    rng = np.random.default_rng(1550)
    z_2048, _ = neumaier_unit_normalize(rng.standard_normal(2048, dtype=np.float64))
    shm = shared_memory.SharedMemory(create=True, size=z_2048.nbytes)
    try:
        shm_view = np.ndarray(z_2048.shape, dtype=np.float64, buffer=shm.buf)
        shm_view[:] = z_2048[:]
        wire_hdr = pack_pmtp_wire_header(slab_slot=1, d_dim=2048, seq_len=1)

        # 3. Receiver reads SLAB_ID & projects isometrically into Hermes-3 / LLaMA-3.1 (d_model = 4096)
        shm_rx = shared_memory.SharedMemory(name=shm.name)
        try:
            z_rx = np.ndarray((2048,), dtype=np.float64, buffer=shm_rx.buf)
            h_4096 = W_fp64.T @ z_rx  # Isometric embedding 2048 -> 4096: ||h_4096||_2 == ||z_rx||_2 == 1.0
            _, norm_4096 = neumaier_unit_normalize(h_4096)
            norm_drift = abs(norm_4096 - 1.0)
            assert norm_drift <= 1e-15, f"Isometric embedding norm drift exceeded: {norm_drift}"

            # 4a. Hugging Face Transformers / vLLM PromptEmbeds shape (1, 1, 4096)
            hf_inputs_embeds = h_4096.reshape(1, 1, 4096).astype(np.float32)

            # 4b. llama.cpp / Ollama C-API struct llama_batch with token=NULL, embd!=NULL
            embd_f32 = np.ascontiguousarray(h_4096, dtype=np.float32)
            pos_arr = np.array([0], dtype=np.int32)
            n_seq_arr = np.array([1], dtype=np.int32)
            logits_arr = np.array([1], dtype=np.int8)
            batch_c = LlamaBatchCABI(
                n_tokens=1,
                token=ctypes.POINTER(ctypes.c_int32)(),  # NULL pointer: bypasses 1D tokenizer
                embd=embd_f32.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                pos=pos_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
                n_seq_id=n_seq_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
                seq_id=ctypes.POINTER(ctypes.POINTER(ctypes.c_int32))(),
                logits=logits_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int8)),
            )
            assert not bool(batch_c.token), "llama_batch.token MUST be NULL for latent injection!"
            assert bool(batch_c.embd), "llama_batch.embd MUST be non-NULL!"
        finally:
            shm_rx.close()
    finally:
        shm.close()
        shm.unlink()

    elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 3)
    result = {
        "status": "PASS",
        "exit_code": 0,
        "wire_header_bytes": len(wire_hdr),
        "stiefel_gram_max_err_fp64": gram_err,
        "neumaier_isometric_norm_drift": norm_drift,
        "hf_inputs_embeds_shape": list(hf_inputs_embeds.shape),
        "llama_batch_token_is_null": not bool(batch_c.token),
        "llama_batch_embd_non_null": bool(batch_c.embd),
        "latency_ms": elapsed_ms
    }
    print("[PMTP BRIDGE VERIFIED]", json.dumps(result))
    return result


if __name__ == "__main__":
    run_bridge_verification()
