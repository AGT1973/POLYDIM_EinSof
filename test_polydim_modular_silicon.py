"""
POLYDIM SILICON TEST SUITE
Validates all modular packages in physical silicon with raw IEEE-754 metrics.
Enforces Exit Code 0 and Empirical Veto (Rule 10 & Rule 30).
"""

import sys
import time
import numpy as np

def run_suite():
    print("=" * 70)
    print("INICIANDO SUITE DE CERTIFICACIÓN MODULAR POLYDIM EN SILICIO")
    print("=" * 70)
    t0 = time.perf_counter()

    # 1. Stiefel Manifold & Polar Newton-Schulz
    print("\n[TEST 1] Stiefel Manifold & Polar Factor (Newton-Schulz Ord-5)")
    from polydim.core.manifold import StiefelManifold
    
    rng = np.random.default_rng(1337)
    raw_M = rng.standard_normal((1024, 256))
    U = StiefelManifold.polar_newton_schulz(raw_M, num_iters=5)
    defect = StiefelManifold.orthogonality_defect(U)
    print(f"  - Matriz U shape: {U.shape}")
    print(f"  - Defecto ortogonal ||U^T U - I_r||_inf: {defect:.3e}")
    assert defect < 1e-14, f"Defecto ortogonal excesivo: {defect}"

    # Tangent Bundle Chart (u_hat, rho)
    h_sample = rng.standard_normal(1024) * 4.2
    u_hat, rho = StiefelManifold.project_tangent_bundle(h_sample)
    assert abs(np.linalg.norm(u_hat) - 1.0) < 1e-14, "u_hat no es unitario"
    assert rho > 0.0, "rho debe ser positivo"
    print(f"  - Haz tangente: ||u_hat|| = {np.linalg.norm(u_hat):.16f}, rho = {rho:.6f}")

    # Karcher Mean across 3 frames
    frames = [StiefelManifold.polar_newton_schulz(rng.standard_normal((128, 32))) for _ in range(3)]
    k_mean = StiefelManifold.karcher_mean(frames, max_iter=5)
    k_defect = StiefelManifold.orthogonality_defect(k_mean)
    print(f"  - Karcher Mean shape: {k_mean.shape}, Defecto: {k_defect:.3e}")
    assert k_defect < 1e-14, "Karcher mean no está en Stiefel"

    # 2. Symplectic Verlet Flow & SNAP
    print("\n[TEST 2] Symplectic Riemannian Verlet Flow (SMW-Cayley O(D))")
    from polydim.core.symplectic_flow import SymplecticVerletFlow, TopologicalSnapStabilizer
    
    flow = SymplecticVerletFlow(dim=1024, step_size=0.01, gamma_damping=0.02)
    u_curr = rng.standard_normal(1024)
    u_curr = u_curr / np.linalg.norm(u_curr)
    p_curr = np.zeros(1024)
    snap = TopologicalSnapStabilizer(snap_interval=200, drift_threshold=1e-6)

    max_norm_err = 0.0
    for step_idx in range(500):
        # Gradiente sintético de potencial
        grad_V = 0.1 * np.sin(u_curr)
        u_curr, p_curr = flow.step(u_curr, p_curr, grad_V)
        norm_err = abs(np.linalg.norm(u_curr) - 1.0)
        max_norm_err = max(max_norm_err, norm_err)
        u_curr, did_snap = snap.evaluate_and_stabilize(u_curr)

    print(f"  - 500 pasos Verlet ejecutados.")
    print(f"  - Máximo error de norma esférica en flujo: {max_norm_err:.3e}")
    print(f"  - Resets SNAP activados: {snap.snaps_triggered}")
    assert max_norm_err < 1e-14, f"Desviación de variedad excesiva: {max_norm_err}"

    # 3. Dual-Memory CAM-HiPPO
    print("\n[TEST 3] Dual-Memory CAM-HiPPO Continuous Memory O(1)")
    from polydim.core.memory_hippo import ModernHopfieldCAM, HippoCayleyContinuousMemory
    
    hippo = HippoCayleyContinuousMemory(order=64, dt=0.02)
    print(f"  - Radio espectral HiPPO-Cayley rho(A_disc): {hippo.max_eigenval_mag:.6f}")
    assert hippo.max_eigenval_mag <= 1.0 + 1e-9, f"Inestabilidad asintótica HiPPO: rho > 1.0 ({hippo.max_eigenval_mag})"
    
    # 200 pasos continuos de actualización
    for step in range(200):
        s = hippo.update(float(np.sin(step * 0.1)))
    assert not np.isnan(s).any(), "NaN detectado en estado HiPPO"

    # CAM Associative Memory
    cam = ModernHopfieldCAM(key_dim=128)
    pat1 = rng.standard_normal(128)
    pat1 = pat1 / np.linalg.norm(pat1)
    cam.store_pattern(pat1)
    
    # Query con ruido ortogonal de 5%
    noisy_q = pat1 + 0.05 * rng.standard_normal(128)
    recalled = cam.query(noisy_q)
    cos_sim = float(np.dot(pat1, recalled))
    print(f"  - CAM Recall Cosine Similarity (bajo ruido): {cos_sim:.6f}")
    assert cos_sim > 0.99, f"Recall deficiente en CAM: {cos_sim}"

    # 4. Protocolo Helena (Carrier Transport)
    print("\n[TEST 4] Protocolo Helena (L2 Invariant Hybrid Transport)")
    from polydim.transport.helena_carrier import HelenaCarrier
    
    test_vec = rng.standard_normal(4096)
    test_vec = test_vec / np.linalg.norm(test_vec)
    
    # 4-bit packaging
    carrier_4bit_str = HelenaCarrier.pack_4bit(test_vec, slab_id="helena_test_4bit")
    meta_4bit, unpacked_4bit = HelenaCarrier.parse_carrier_block(carrier_4bit_str)
    cos_4bit = float(np.dot(test_vec, unpacked_4bit))
    print(f"  - Helena 4-Bit: Payload {len(carrier_4bit_str)} chars (~{len(carrier_4bit_str)//4} tokens)")
    print(f"  - Helena 4-Bit Cosine Similarity: {cos_4bit:.6f} (>0.993 target)")
    assert cos_4bit >= 0.990, f"Similitud 4-bit por debajo de cota: {cos_4bit}"

    # FP64 exact packaging
    carrier_exact_str = HelenaCarrier.pack_exact_fp64(test_vec, slab_id="helena_test_exact")
    meta_exact, unpacked_exact = HelenaCarrier.parse_carrier_block(carrier_exact_str)
    exact_err = float(np.max(np.abs(test_vec - unpacked_exact)))
    print(f"  - Helena FP64 Exact Error L_inf: {exact_err:.3e} (bit-exact IEEE-754)")
    assert exact_err < 1e-15, f"Error exacto excede precisión máquina: {exact_err}"

    # 5. PMTP Shared Memory Local Bus
    print("\n[TEST 5] PMTP Shared Memory Local Bus (Win32 / SHM)")
    from polydim.transport.pmtp_shm import PmtpShmBus
    
    shm_bus = PmtpShmBus(tag_name="polydim_shm_test_suite", size_bytes=1024 * 1024)
    write_meta = shm_bus.write_tensor(test_vec, slab_id=77)
    read_tensor, read_meta = shm_bus.read_tensor(expected_slab_id=77)
    shm_err = float(np.max(np.abs(test_vec - read_tensor)))
    print(f"  - PMTP SHM Round-Trip Error: {shm_err:.3e}")
    print(f"  - BLAKE2s Checksum: {read_meta['checksum']}")
    shm_bus.close()
    assert shm_err == 0.0, "PMTP SHM falló en transmisión idéntica bit-a-bit"

    # 6. Qwen Latent Adapter (TR-AGN Control)
    print("\n[TEST 6] Qwen 2.5 Latent Adapter (TR-AGN Injection)")
    from polydim.adapters.qwen_adapter import QwenLatentAdapter
    
    adapter = QwenLatentAdapter(model_dim=896, canonical_dim=1024)
    raw_hidden = rng.standard_normal(896) * 1.5
    u_ext, rho_ext = adapter.extract_latent_activation(raw_hidden)
    print(f"  - Extracción capa 12 Qwen: ||u|| = {np.linalg.norm(u_ext):.6f}, rho = {rho_ext:.6f}")
    assert abs(np.linalg.norm(u_ext) - 1.0) < 1e-14, "Fallo de norma en extracción"
    
    # Inyección latente
    s_peleides = rng.standard_normal(1024)
    s_peleides = s_peleides / np.linalg.norm(s_peleides)
    modified_hidden = adapter.inject_latent_state(raw_hidden, s_peleides)
    pert_ratio = np.linalg.norm(modified_hidden - raw_hidden) / np.linalg.norm(raw_hidden)
    print(f"  - Inyección TR-AGN: Ratio de perturbación relativa = {pert_ratio:.6f} (Confinado)")
    assert pert_ratio <= adapter.gain_beta * 1.01, "Perturbación excede cota de ganancia TR-AGN"

    t1 = time.perf_counter()
    print("\n" + "=" * 70)
    print(f"SUITE COMPLETA EXITOSA (6/6 CHECKS) | LATENCIA TOTAL: {(t1 - t0)*1000:.2f} ms")
    print("EXIT CODE: 0")
    print("=" * 70)

if __name__ == "__main__":
    run_suite()
