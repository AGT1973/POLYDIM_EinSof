"""
POLYDIM CORE: Dual-Memory CAM-HiPPO & Bilinear Cayley-Tustin Memory
Implements SOTA Theorems T-MP28, T-MP35
Maintains O(1) continuous temporal memory and associative pattern recall.
"""

import math
import numpy as np

class ModernHopfieldCAM:
    """
    Continuous Associative Memory (CAM / Modern Hopfield)
    Retrieval: CAM(q) = softmax(K q / sqrt(r)) V
    """
    def __init__(self, key_dim: int, temp: float = 1.0):
        self.r = key_dim
        self.temp = temp
        self.keys = []
        self.values = []

    def store_pattern(self, key: np.ndarray, val: np.ndarray = None):
        k = np.asarray(key, dtype=np.float64).flatten()
        norm_k = np.linalg.norm(k)
        if norm_k > 1e-12:
            k = k / norm_k
        self.keys.append(k)
        if val is None:
            self.values.append(k)
        else:
            v = np.asarray(val, dtype=np.float64).flatten()
            self.values.append(v)

    def query(self, q: np.ndarray) -> np.ndarray:
        if not self.keys:
            return np.zeros(self.r, dtype=np.float64)
            
        q = np.asarray(q, dtype=np.float64).flatten()
        norm_q = np.linalg.norm(q)
        if norm_q > 1e-12:
            q = q / norm_q
            
        K = np.array(self.keys)
        V = np.array(self.values)
        
        # Logits: K q / (sqrt(r) * temp)
        logits = (K @ q) / (math.sqrt(self.r) * self.temp)
        # Stable softmax
        logits_max = np.max(logits)
        exp_logits = np.exp(logits - logits_max)
        weights = exp_logits / np.sum(exp_logits)
        
        recalled = weights @ V
        norm_rec = np.linalg.norm(recalled)
        if norm_rec > 1e-12:
            return recalled / norm_rec
        return recalled

class HippoCayleyContinuousMemory:
    """
    Teorema T-MP28 / T-MP35: HiPPO-Cayley Bilineal en Espacio Canónico O(1).
    Continuous-time state-space memory using Legendre polynomials.
    Discretized via bilinear Tustin transform: A_cayley = (I - 0.5 * dt * A)^(-1) (I + 0.5 * dt * A)
    Strictly stable: spectral radius rho(A_cayley) <= 1.0 (marginal stability, no explosion).
    """
    def __init__(self, order: int = 64, dt: float = 0.02):
        self.N = order
        self.dt = dt
        self.state = np.zeros(self.N, dtype=np.float64)
        
        # Build HiPPO-LegS continuous transition matrix A
        A_cont = np.zeros((self.N, self.N), dtype=np.float64)
        for i in range(self.N):
            for j in range(self.N):
                if i > j:
                    A_cont[i, j] = (2 * i + 1) ** 0.5 * (2 * j + 1) ** 0.5
                elif i == j:
                    A_cont[i, j] = i + 1
        A_cont = -A_cont
        
        # Build B matrix
        B_cont = np.array([(2 * i + 1) ** 0.5 for i in range(self.N)], dtype=np.float64)
        
        # Bilinear Tustin discretization: Cayley transform
        I = np.eye(self.N, dtype=np.float64)
        M_inv = np.linalg.inv(I - 0.5 * self.dt * A_cont)
        self.A_disc = M_inv @ (I + 0.5 * self.dt * A_cont)
        self.B_disc = M_inv @ (self.dt * B_cont)
        
        # Verify spectral radius
        eigenvals = np.linalg.eigvals(self.A_disc)
        self.max_eigenval_mag = float(np.max(np.abs(eigenvals)))

    def update(self, u_scalar: float) -> np.ndarray:
        """
        Step update of continuous state memory with scalar/projection input.
        c_{t+1} = A_disc c_t + B_disc u_scalar
        """
        self.state = self.A_disc @ self.state + self.B_disc * float(u_scalar)
        return self.state

    def reset(self):
        self.state = np.zeros(self.N, dtype=np.float64)
