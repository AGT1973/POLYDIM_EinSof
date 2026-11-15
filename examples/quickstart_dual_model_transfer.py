"""
POLYDIM SUITE — Quickstart Mínimo de Transferencia Tensorial Dual
Demuestra cómo el Modelo A transfiere activaciones latentes al Modelo B
a través de memoria compartida sin serializar a texto plano (Zero-Copy).
"""

import sys
import os
import time
import math
import numpy as np

# Permitir ejecución directa sin requerir 'pip install -e .'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pmtp import PmtpShmBus, PmtpStiefelAdapter

def main():
    print("=" * 68)
    print("POLYDIM SUITE — QUICKSTART DUAL-MODEL TRANSFER (ZERO-COPY)")
    print("=" * 68)

    dim = 2048
    rank = 64

    # 1. Simular activación latente de Modelo A normalizada a S^{D-1}
    rng = np.random.default_rng(2026)
    latent_A = rng.standard_normal(dim).astype(np.float64)
    norm_A = math.sqrt(math.fsum(latent_A * latent_A))
    latent_A /= norm_A

    print(f"[*] Modelo A generó activación latente: D={dim}, ||v||={np.linalg.norm(latent_A):.6f}")

    # 2. Inicializar bus de memoria compartida y adaptador Stiefel
    bus = PmtpShmBus(prefix="quickstart_pmtp", max_slabs=8, max_dim=dim)
    adapter = PmtpStiefelAdapter(dim_source=dim, dim_latent=rank, seed=42)

    # 3. Modelo A publica tensor directamente en memoria compartida (Host RAM / VRAM)
    t0 = time.perf_counter_ns()
    descriptor = bus.publish_tensor(latent_A)
    write_us = (time.perf_counter_ns() - t0) / 1000.0

    print(f"[+] Modelo A publicó en Shared Memory: descriptor={descriptor} ({write_us:.2f} µs)")

    # 4. Modelo B lee directamente de la memoria compartida (sin tokens, sin de-tokenizador)
    t1 = time.perf_counter_ns()
    received_tensor = bus.read_tensor(descriptor, verify_stiefel=True)
    read_us = (time.perf_counter_ns() - t1) / 1000.0

    print(f"[+] Modelo B leyó vector continuo: {len(received_tensor)} floats ({read_us:.2f} µs)")

    # 5. Proyectar sobre la variedad de Stiefel St(D, rank)
    t2 = time.perf_counter_ns()
    u, rho = adapter.project_to_spherical(received_tensor)
    proj_us = (time.perf_counter_ns() - t2) / 1000.0

    # 6. Verificación de integridad matemática y defecto
    mse = float(np.mean((latent_A - received_tensor) ** 2))
    defect = float(np.max(np.abs(adapter.W.T @ adapter.W - np.eye(rank))))

    print(f"[+] Proyección esférica Stiefel (u, rho): {proj_us:.2f} µs")
    print(f"[*] Error Cuadrático Medio: {mse:.2e} (Copia Exacta Bit a Bit)")
    print(f"[*] Defecto de Ortogonalidad Stiefel: ||W^T W - I|| = {defect:.2e}")
    print("-" * 68)
    print(f">>> LATENCIA TOTAL TRANSFERENCIA: {write_us + read_us:.2f} µs (Costo: 0 Tokens) <<<")
    print("=" * 68)

    # Limpieza determinista de descriptores
    bus.release_slab(descriptor)
    bus.cleanup()
    return 0

if __name__ == "__main__":
    sys.exit(main())
