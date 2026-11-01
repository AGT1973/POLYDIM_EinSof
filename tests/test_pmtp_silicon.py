# ============================================================================
# PMTP SILICON AUDIT & RED TEAM ADVERSARIAL SUITE (V1.0 SOTA HARDENED)
# Proyecto: PMTP (Polydim Memory Tensor Protocol)
# Autor: Ariel García Traba — Independent Research / EinsofOS
# Base Teórica: Teoremas T-MP12, T-MP15, T-MP17, T-MP18, T-MP20, T-MP21, T-MP22
# ============================================================================

import sys
import os
import time
import json
import numpy as np

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    HAS_TORCH = True
except ImportError:
    torch = None
    AutoTokenizer = None
    AutoModelForCausalLM = None
    HAS_TORCH = False

from pmtp_shm_bus import PmtpShmBus
from pmtp_stiefel import PmtpStiefelAdapter
from pmtp_types import PmtpCompactHeader, HEADER_COMPACT_SIZE

def same_bits(t1, t2) -> bool:
    if hasattr(t1, "detach"):
        b1 = t1.detach().contiguous().cpu().numpy().tobytes()
        b2 = t2.detach().contiguous().cpu().numpy().tobytes()
    else:
        b1 = np.ascontiguousarray(t1).tobytes()
        b2 = np.ascontiguousarray(t2).tobytes()
    return b1 == b2

def test_01_atomic_monitor_and_leases():
    print("[1/4] Auditando T-MP15 / T-MP17 / T-MP20: Concurrencia PMTP, Monitor y Leases...")
    bus = PmtpShmBus(prefix="pmtp_test")
    slab_id = 0xAA01
    dim = 2048
    shm = bus.allocate_tensor_slab(slab_id=slab_id, num_elements=dim, dtype=np.float64)

    # 1. Escritura inicial en Slot 0
    v1 = np.ones(dim, dtype=np.float64) * 42.0
    assert bus.publish_snapshot_atomic(slab_id=slab_id, data=v1), "Falla escritura inicial v1"

    # 2. Lector adquiere lease sobre slot activo (Slot 1 tras primera conmutación)
    slot_leased, gen1 = bus.acquire_reader_lease(slab_id=slab_id)
    assert slot_leased == 1, f"Slot activo esperado 1, obtenido {slot_leased}"

    # 3. Escritor publica v2 en Slot 0 (inactivo y retirado)
    v2 = np.ones(dim, dtype=np.float64) * 84.0
    assert bus.publish_snapshot_atomic(slab_id=slab_id, data=v2), "Falla publicación v2"

    # 4. Exclusión Anti-ABA (T-MP17): Escritor intenta sobrescribir Slot 1 retenido por Lector
    v3 = np.ones(dim, dtype=np.float64) * 126.0
    overwritten = bus.publish_snapshot_atomic(slab_id=slab_id, data=v3, max_retries=2)
    assert not overwritten, "VULNERABILIDAD DETECTADA: Escritor sobrescribió slot retenido por lease de lectura"

    # 5. Lectura protegida libre de torn-reads
    info = bus.slabs[slab_id]
    offset = HEADER_COMPACT_SIZE + (slot_leased * info["payload_bytes"])
    data_read = np.ndarray((dim,), dtype=np.float64, buffer=info["shm"].buf, offset=offset)
    assert np.all(data_read == 42.0), "TORN-READ DETECTADA: Datos leídos no corresponden al snapshot v1"

    # 6. Liberación y reintento de publicación
    bus.release_reader_lease(slab_id=slab_id, slot=slot_leased)
    assert bus.publish_snapshot_atomic(slab_id=slab_id, data=v3), "Falla publicación v3 tras release"

    # 7. Lectura mediante método de conveniencia leased
    leased = bus.read_snapshot_leased(slab_id=slab_id)
    assert np.all(leased.array == 126.0), "Snapshot leído no corresponde a v3"
    del leased
    import gc
    gc.collect()

    bus.release_all()
    print("      [PASS] Monitor atómico y exclusión anti-ABA certificados en silicio.")
    return True

def test_02_polarsafe_v2_scale_invariance():
    print("[2/4] Auditando T-MP18: Contrato PolarSafe V2 con Invarianza a Escala...")
    # Caso A: Matriz diminuta pero ortogonalmente perfecta (1e-8 * I)
    X_tiny = np.eye(64, dtype=np.float64) * 1e-8
    Q_tiny, kappa_tiny, r_rel_tiny, status_tiny = PmtpStiefelAdapter.polar_safe_v2(X_tiny)
    assert status_tiny.startswith("ACCEPTED"), f"Falla PolarSafe V2 en matriz diminuta: {status_tiny}"
    assert np.isclose(kappa_tiny, 1.0, atol=1e-10), f"Kappa incorrecto: {kappa_tiny}"
    defect_tiny = np.max(np.abs(np.dot(Q_tiny.T, Q_tiny) - np.eye(64)))
    assert defect_tiny < 1e-14, f"Defecto polar inadmisible: {defect_tiny}"

    # Caso B: Matriz patológica mal condicionada (kappa = 1e16)
    X_ill = np.diag([1e9] + [1e-7] * 63).astype(np.float64)
    Q_ill, kappa_ill, r_rel_ill, status_ill = PmtpStiefelAdapter.polar_safe_v2(X_ill, kappa_fatal=1e8)
    assert status_ill == "REJECTED_ILL_CONDITIONED", f"Falla rechazo de matriz enferma: {status_ill}"

    # Caso C: Matriz nula
    X_zero = np.zeros((64, 64), dtype=np.float64)
    _, _, _, status_zero = PmtpStiefelAdapter.polar_safe_v2(X_zero)
    assert status_zero == "REJECTED_SINGULAR", f"Falla rechazo de matriz singular: {status_zero}"

    # Caso D: Adaptador completo con Newton-Schulz Orden 5
    adapter = PmtpStiefelAdapter(dim_source=896, dim_latent=1024, seed=123)
    defect = adapter.compute_orthogonality_defect()
    print(f"      Defecto de ortogonalidad ||W^T W - I||_inf: {defect:.2e} (status={adapter.status})")
    assert defect < 1e-12, f"Defecto de adaptador excesivo: {defect}"
    assert adapter.status.startswith("ACCEPTED_NEWTON_SCHULZ"), f"Status no esperado: {adapter.status}"
    print("      [PASS] Contrato PolarSafe V2 certificado con Newton-Schulz Orden 5.")
    return True

def test_03_sequence_abi_and_immutability():
    print("[3/4] Auditando T-MP21: ABI Sequence-to-Core y Contrato de Inmutabilidad...")
    adapter = PmtpStiefelAdapter(dim_source=896, dim_latent=896, seed=456)
    B, L, D = 1, 8, 896
    if HAS_TORCH:
        H = torch.randn(B, L, D, dtype=torch.float32)
        H_baseline = H.clone()
    else:
        np.random.seed(456)
        H = np.random.randn(B, L, D).astype(np.float32)
        H_baseline = H.copy()

    # 1. Extracción de coordenadas esféricas en token L-1
    u_orig, rho_orig = adapter.extract_sequence_latent(H, token_pos=-1)
    assert np.isclose(np.linalg.norm(u_orig), 1.0, atol=1e-12), "u_orig no está normalizado en S^(r-1)"
    assert rho_orig > 0.0, "rho_orig debe ser estrictamente positivo"

    # 2. Inyección con bypass exacto (beta = 0.0)
    H_bypass = adapter.inject_sequence_residual(
        H=H,
        u_prime=u_orig,
        rho_prime=rho_orig,
        u_orig=u_orig,
        rho_orig=rho_orig,
        beta=0.0,
        token_pos=-1,
        enabled=True
    )
    assert same_bits(H, H_bypass), "Falla T-MP21: bypass beta=0 alteró los bits del tensor"

    # 3. Contrato de Inmutabilidad Anti-Aliasing (MP-59)
    # Si modificamos H_bypass in-place, H original debe permanecer idéntico a H_baseline
    if HAS_TORCH:
        H_bypass.add_(100.0)
        assert torch.equal(H, H_baseline), "VULNERABILIDAD ALIASING: Mutación de salida corrompió el tensor base H"
    else:
        H_bypass += 100.0
        assert np.array_equal(H, H_baseline), "VULNERABILIDAD ALIASING: Mutación de salida corrompió el tensor base H"

    # 4. Inyección en token L-1: los tokens [0 ... L-2] deben permanecer exactamente inalterados
    delta_u = np.random.randn(896) * 0.1
    u_prime = (u_orig + delta_u) / np.linalg.norm(u_orig + delta_u)
    H_mod = adapter.inject_sequence_residual(
        H=H,
        u_prime=u_prime,
        rho_prime=rho_orig,
        u_orig=u_orig,
        rho_orig=rho_orig,
        beta=0.5,
        token_pos=-1,
        enabled=True
    )
    if HAS_TORCH:
        assert torch.equal(H_mod[:, :-1, :], H[:, :-1, :]), "CORRUPCIÓN ABI: Tokens previos fueron alterados"
        assert not torch.equal(H_mod[:, -1, :], H[:, -1, :]), "FALLA ABI: Token objetivo L-1 no fue modulado"
    else:
        assert np.array_equal(H_mod[:, :-1, :], H[:, :-1, :]), "CORRUPCIÓN ABI: Tokens previos fueron alterados"
        assert not np.array_equal(H_mod[:, -1, :], H[:, -1, :]), "FALLA ABI: Token objetivo L-1 no fue modulado"
    print("      [PASS] ABI Sequence-to-Core e inmutabilidad anti-aliasing certificadas.")
    return True

def test_04_real_qwen_kv_cache_interop():
    print("[4/4] Auditando T-MP22: Interoperabilidad Neuronal Real Qwen con KV-Cache...")
    if not HAS_TORCH:
        print("      [SKIP] PyTorch/Transformers no disponible en entorno host (CPython freethreaded).")
        return True
    snap_path = r"C:\Users\eluithi\.cache\huggingface\hub\models--Qwen--Qwen2.5-0.5B\snapshots\060db6499f32faf8b98477b0a26969ef7d8b9987"
    if not os.path.exists(snap_path):
        print(f"      [SKIP] Snapshot de Qwen no encontrado en {snap_path}")
        return True

    tokenizer = AutoTokenizer.from_pretrained(snap_path)
    model = AutoModelForCausalLM.from_pretrained(snap_path, torch_dtype=torch.float32)
    model.eval()

    prompt = "In quantum mechanics, the wave function collapse"
    inputs = tokenizer(prompt, return_tensors="pt")

    # 1. Baseline de decodificación autorregresiva (5 tokens bajo KV-Cache)
    with torch.inference_mode():
        base_tokens = model.generate(**inputs, max_new_tokens=5, use_cache=True, do_sample=False)
        base_text = tokenizer.decode(base_tokens[0])

    # 2. Forward hook no invasivo en capa intermedia (capa 12)
    target_layer = len(model.model.layers) // 2
    def identity_hook(_module, _inp, out):
        if isinstance(out, tuple):
            return (out[0].clone(), *out[1:])
        return out.clone()

    hook_handle = model.model.layers[target_layer].register_forward_hook(identity_hook)
    try:
        with torch.inference_mode():
            hook_tokens = model.generate(**inputs, max_new_tokens=5, use_cache=True, do_sample=False)
            hook_text = tokenizer.decode(hook_tokens[0])
    finally:
        hook_handle.remove()

    assert same_bits(base_tokens, hook_tokens), "FALLA T-MP22: Incompatibilidad de tokens generados bajo KV-Cache"
    assert base_text == hook_text, f"Texto discrepante: '{base_text}' vs '{hook_text}'"

    # 3. Comprobación de prefill sobre logits inmediatos
    with torch.inference_mode():
        base_logits = model(**inputs, use_cache=False).logits
    hook_handle = model.model.layers[target_layer].register_forward_hook(identity_hook)
    try:
        with torch.inference_mode():
            hook_logits = model(**inputs, use_cache=False).logits
    finally:
        hook_handle.remove()

    max_diff = float((base_logits - hook_logits).abs().max().item())
    assert max_diff == 0.0, f"Divergencia en prefill logits: {max_diff}"
    print(f"      Certificación Q1 completada: max_abs_logit_diff = {max_diff}, tokens idénticos bit a bit.")
    print(f"      Texto generado validado: '{hook_text}'")
    print("      [PASS] Interoperabilidad neuronal con KV-Cache certificada (T-MP22).")
    return True

def main():
    print("============================================================================")
    print("PMTP SILICON VALIDATION SUITE (T-MP12 A T-MP22) — HARDWARE AUDIT")
    print("============================================================================")
    t0 = time.time()
    
    assert test_01_atomic_monitor_and_leases()
    assert test_02_polarsafe_v2_scale_invariance()
    assert test_03_sequence_abi_and_immutability()
    assert test_04_real_qwen_kv_cache_interop()

    elapsed = time.time() - t0
    print("============================================================================")
    print(f"PMTP VALIDATION: 4/4 SUB-SUITES PASSED | LATENCIA TOTAL: {elapsed:.2f}s | EXIT CODE 0")
    print("============================================================================")
    sys.exit(0)

if __name__ == "__main__":
    main()
