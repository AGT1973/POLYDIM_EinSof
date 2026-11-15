# polydim/tensor.py
import ctypes
from pathlib import Path
import numpy as np
import os as _os

# Ruta nativa — configurable via env var POLYDIM_LIBRARY.
# Por defecto busca kernel_cpp_v26500.dll junto a este paquete o en 02_KERNELS_Y_SILICIO.
_DEFAULT_LOCATIONS = [
    Path(_os.environ.get("POLYDIM_LIBRARY", "")),
    Path(__file__).resolve().parent.parent / "kernel_cpp_v26500.dll",
    Path(r"E:\POLYDIM_EINSOF\ENTREGA_2026_10_16_V26404\02_KERNELS_Y_SILICIO\kernel_cpp_v26500.dll"),
]

_DLL_PATH = None
for loc in _DEFAULT_LOCATIONS:
    if loc and loc.exists():
        _DLL_PATH = loc
        break
if _DLL_PATH is None:
    _DLL_PATH = _DEFAULT_LOCATIONS[2]

_cpp_dll = None
_project_fn = None

def _get_dll():
    global _cpp_dll, _project_fn
    if _cpp_dll is None:
        if not _DLL_PATH.exists():
            raise FileNotFoundError(
                f"Librería nativa POLYDIM no encontrada: {_DLL_PATH}\n"
                f"Establece la variable de entorno POLYDIM_LIBRARY con la ruta correcta."
            )
        _cpp_dll = ctypes.CDLL(str(_DLL_PATH))

        class _ConstView(ctypes.Structure):
            _fields_ = [("ptr", ctypes.POINTER(ctypes.c_double)), ("len", ctypes.c_uint64)]
        class _MutView(ctypes.Structure):
            _fields_ = [("ptr", ctypes.POINTER(ctypes.c_double)), ("len", ctypes.c_uint64)]

        _cpp_dll._ConstView = _ConstView
        _cpp_dll._MutView = _MutView

        # Enlazar símbolo de proyección esférica con fallback por versión
        for sym in ["polydim_sphere_project_v26500", "polydim_sphere_project_v26403", "polydim_sphere_project_v26402"]:
            if hasattr(_cpp_dll, sym):
                _project_fn = getattr(_cpp_dll, sym)
                _project_fn.argtypes = [_ConstView, _MutView]
                _project_fn.restype = ctypes.c_int32
                break

        if _project_fn is None:
            raise AttributeError(f"No se encontró símbolo de proyección esférica v26500 en {_DLL_PATH}")

    return _cpp_dll

class Tensor:
    """
    Tensor de alta dimensión nativo de POLYDIM.
    Opera directamente sobre memoria contigua FP64 en la variedad Stiefel St(D, K) y S^(D-1).
    """
    def __init__(self, data: np.ndarray):
        if not isinstance(data, np.ndarray):
            data = np.asarray(data, dtype=np.float64)
        if data.dtype != np.float64:
            data = data.astype(np.float64)
        if not data.flags['C_CONTIGUOUS']:
            data = np.ascontiguousarray(data)
        self._data = data

    @classmethod
    def from_numpy(cls, arr: np.ndarray) -> "Tensor":
        return cls(arr)

    @classmethod
    def ones(cls, d: int, k: int = 1) -> "Tensor":
        shape = (d,) if k == 1 else (d, k)
        return cls(np.ones(shape, dtype=np.float64))

    @classmethod
    def zeros(cls, d: int, k: int = 1) -> "Tensor":
        shape = (d,) if k == 1 else (d, k)
        return cls(np.zeros(shape, dtype=np.float64))

    @classmethod
    def randn(cls, d: int, k: int = 1, seed: int = None) -> "Tensor":
        if seed is not None:
            np.random.seed(seed)
        shape = (d,) if k == 1 else (d, k)
        return cls(np.random.randn(*shape).astype(np.float64))

    @property
    def shape(self):
        return self._data.shape

    @property
    def d(self) -> int:
        return self._data.shape[0]

    @property
    def k(self) -> int:
        return 1 if self._data.ndim == 1 else self._data.shape[1]

    @property
    def nbytes(self) -> int:
        return self._data.nbytes

    def numpy(self) -> np.ndarray:
        return self._data

    def norm(self) -> float:
        return float(np.linalg.norm(self._data))

    def is_unit_norm(self, tol: float = 1e-10) -> bool:
        return abs(self.norm() - 1.0) <= tol

    def project_sphere(self) -> "Tensor":
        """
        Proyecta el vector sobre la hiperesfera unitaria S^(D-1) usando el kernel nativo C++20.
        Garantiza preservación de norma con precisión < 1e-12.
        """
        dll = _get_dll()
        flat_in = np.ascontiguousarray(self._data.flatten(), dtype=np.float64)
        n = len(flat_in)
        out = np.zeros(n, dtype=np.float64)
        
        cv = dll._ConstView(flat_in.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), n)
        mv = dll._MutView(out.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), n)
        
        rc = _project_fn(cv, mv)
        if rc != 0:
            raise RuntimeError(f"Error nativo en proyección esférica (Status code: {rc})")
            
        return Tensor(out.reshape(self._data.shape))

    def __repr__(self):
        return f"polydim.Tensor(shape={self.shape}, dtype=fp64, norm={self.norm():.6f})"
