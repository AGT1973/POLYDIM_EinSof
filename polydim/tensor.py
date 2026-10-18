# polydim/tensor.py
import ctypes
from pathlib import Path
import numpy as np

# Rutas nativas
_DLL_PATH = Path(r"E:\POLYDIM_EINSOF\ENTREGA_2026_10_07_V26155\kernel_cpp_v26155.dll")
_cpp_dll = None

def _get_dll():
    global _cpp_dll
    if _cpp_dll is None:
        if not _DLL_PATH.exists():
            raise FileNotFoundError(f"No se encontro la libreria nativa POLYDIM: {_DLL_PATH}")
        _cpp_dll = ctypes.CDLL(str(_DLL_PATH))
        
        # Configurar firmas
        class _ConstView(ctypes.Structure):
            _fields_ = [("ptr", ctypes.POINTER(ctypes.c_double)), ("len", ctypes.c_uint64)]
        class _MutView(ctypes.Structure):
            _fields_ = [("ptr", ctypes.POINTER(ctypes.c_double)), ("len", ctypes.c_uint64)]
            
        _cpp_dll._ConstView = _ConstView
        _cpp_dll._MutView = _MutView
        _cpp_dll.polydim_sphere_project_v26155.argtypes = [_ConstView, _MutView]
        _cpp_dll.polydim_sphere_project_v26155.restype = ctypes.c_int32
    return _cpp_dll

class Tensor:
    """
    Tensor de alta dimension nativo de POLYDIM.
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
        Garantiza preservacion de norma con precision < 1e-12.
        """
        dll = _get_dll()
        flat_in = np.ascontiguousarray(self._data.flatten(), dtype=np.float64)
        n = len(flat_in)
        out = np.zeros(n, dtype=np.float64)
        
        cv = dll._ConstView(flat_in.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), n)
        mv = dll._MutView(out.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), n)
        
        rc = dll.polydim_sphere_project_v26155(cv, mv)
        if rc != 0:
            raise RuntimeError(f"Error nativo en proyeccion esferica (Status code: {rc})")
            
        return Tensor(out.reshape(self._data.shape))

    def __repr__(self):
        return f"polydim.Tensor(shape={self.shape}, dtype=fp64, norm={self.norm():.6f})"
