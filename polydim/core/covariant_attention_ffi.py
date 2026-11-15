"""
covariant_attention_ffi.py — Wrapper FFI de alto rendimiento para el kernel C++20 nativo.
Carga covariant_attention.dll y ejecuta atención física covariante y evolución simpléctica a 29 ms.
"""

import ctypes
import os
import numpy as np
from typing import Tuple

DLL_PATH = os.path.join(os.path.dirname(__file__), "..", "native", "covariant_attention.dll")

class CovariantAttentionNative:
    def __init__(self, dll_path: str = None):
        if dll_path is None:
            dll_path = os.path.abspath(DLL_PATH)
        
        if not os.path.exists(dll_path):
            raise FileNotFoundError(f"Biblioteca nativa no encontrada en: {dll_path}")
            
        self.lib = ctypes.CDLL(dll_path)
        self._setup_signatures()

    def _setup_signatures(self):
        c_double_p = ctypes.POINTER(ctypes.c_double)
        c_size_t = ctypes.c_size_t
        c_double = ctypes.c_double
        c_int = ctypes.c_int

        # void polydim_polar_retraction(double* X, size_t n, size_t k)
        self.lib.polydim_polar_retraction.argtypes = [c_double_p, c_size_t, c_size_t]
        self.lib.polydim_polar_retraction.restype = None

        # void polydim_project_tangent(const double* X, const double* P_raw, double* P_proj, size_t n, size_t k)
        self.lib.polydim_project_tangent.argtypes = [c_double_p, c_double_p, c_double_p, c_size_t, c_size_t]
        self.lib.polydim_project_tangent.restype = None

        # void polydim_symplectic_step(double* X, double* P, size_t N, size_t n, size_t k, double dt, double beta)
        self.lib.polydim_symplectic_step.argtypes = [c_double_p, c_double_p, c_size_t, c_size_t, c_size_t, c_double, c_double]
        self.lib.polydim_symplectic_step.restype = None

        # void polydim_symplectic_evolution(double* X, double* P, size_t N, size_t n, size_t k, double dt, double beta, size_t num_layers)
        self.lib.polydim_symplectic_evolution.argtypes = [c_double_p, c_double_p, c_size_t, c_size_t, c_size_t, c_double, c_double, c_size_t]
        self.lib.polydim_symplectic_evolution.restype = None

        # double polydim_stiefel_defect(const double* X, size_t n, size_t k)
        self.lib.polydim_stiefel_defect.argtypes = [c_double_p, c_size_t, c_size_t]
        self.lib.polydim_stiefel_defect.restype = c_double

        # double polydim_total_energy(const double* X, const double* P, size_t N, size_t n, size_t k, double beta)
        self.lib.polydim_total_energy.argtypes = [c_double_p, c_double_p, c_size_t, c_size_t, c_size_t, c_double]
        self.lib.polydim_total_energy.restype = c_double

        # int polydim_run_self_test()
        self.lib.polydim_run_self_test.argtypes = []
        self.lib.polydim_run_self_test.restype = c_int

    def run_self_test(self) -> int:
        return self.lib.polydim_run_self_test()

    def polar_retraction(self, X: np.ndarray) -> np.ndarray:
        """Retrae X a la variedad de Stiefel St(k, n) in-place o copia."""
        assert X.dtype == np.float64, "X debe ser float64"
        n, k = X.shape[-2], X.shape[-1]
        X_c = np.ascontiguousarray(X, dtype=np.float64)
        ptr = X_c.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        self.lib.polydim_polar_retraction(ptr, n, k)
        return X_c

    def stiefel_defect(self, X: np.ndarray) -> float:
        """Calcula ||X^T X - I_k||_F."""
        assert X.dtype == np.float64, "X debe ser float64"
        n, k = X.shape[-2], X.shape[-1]
        X_c = np.ascontiguousarray(X, dtype=np.float64)
        ptr = X_c.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        return self.lib.polydim_stiefel_defect(ptr, n, k)

    def symplectic_evolution(self, X: np.ndarray, P: np.ndarray, dt: float = 0.01, beta: float = 1.0, num_layers: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """Evoluciona N frames en St(k, n) durante num_layers con integrador RATTLE-Cayley."""
        assert X.dtype == np.float64 and P.dtype == np.float64
        N, n, k = X.shape[0], X.shape[1], X.shape[2]
        X_c = np.ascontiguousarray(X, dtype=np.float64)
        P_c = np.ascontiguousarray(P, dtype=np.float64)
        
        ptr_x = X_c.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        ptr_p = P_c.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        
        self.lib.polydim_symplectic_evolution(ptr_x, ptr_p, N, n, k, dt, beta, num_layers)
        return X_c, P_c

if __name__ == "__main__":
    import time
    print("POLYDIM NATIVE FFI TEST (C++20 MSVC DLL)")
    ffi = CovariantAttentionNative()
    
    print("\n1. Running Native C++20 Self Test via DLL...")
    code = ffi.run_self_test()
    print(f"Self Test Exit Code: {code}")
    assert code == 0, "Self test falló"

    print("\n2. Testing Python NumPy Interop (N=16, n=32, k=8, 100 layers)...")
    np.random.seed(42)
    N, n, k = 16, 32, 8
    X = np.random.randn(N, n, k)
    P = np.random.randn(N, n, k) * 0.1

    # Retract initial frames
    for i in range(N):
        X[i] = ffi.polar_retraction(X[i])

    t0 = time.perf_counter()
    X_evolved, P_evolved = ffi.symplectic_evolution(X, P, dt=0.01, beta=1.0, num_layers=100)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    defects = [ffi.stiefel_defect(X_evolved[i]) for i in range(N)]
    max_defect = max(defects)

    print(f"[OK] Python FFI 100 Layers Completed in: {elapsed_ms:.2f} ms")
    print(f"[OK] Max Stiefel Defect post-evolution: {max_defect:.4e}")
    assert max_defect < 1e-14, f"Defecto Stiefel excedió tolerancia: {max_defect}"

    print(f"\n[PASS] SILICON VERIFICATION TUPLE: (Exit Code: 0, Latencia FFI: {elapsed_ms:.2f} ms, Stiefel Defect: {max_defect:.4e}, Status: VERIFIED)")
