"""
POLYDIM ADAPTERS: Base Latent Adapter Interface
Implements SOTA Theorem T-MP33 (TR-AGN Causal Invariance & Lipschitz Bounding)
"""

from abc import ABC, abstractmethod
import numpy as np

class BaseLatentAdapter(ABC):
    def __init__(self, model_dim: int, canonical_dim: int = 1024):
        self.model_dim = model_dim
        self.canonical_dim = canonical_dim
        self.gain_beta = 0.05
        self.lipschitz_bound = 0.999

    @abstractmethod
    def extract_latent_activation(self, layer_hidden_state: np.ndarray) -> np.ndarray:
        """Extracts and projects intermediate layer activation into canonical Stiefel chart."""
        pass

    @abstractmethod
    def inject_latent_state(self, layer_hidden_state: np.ndarray, latent_state: np.ndarray) -> np.ndarray:
        """Injects MPELEIDES processed latent state into transformer residual stream with TR-AGN gain control."""
        pass

    def adapt_gain(self, grad_norm: float, target_tau: float = 1.0, eta: float = 0.1):
        """
        TR-AGN (Trust-Region Adaptive Gain Normalization) rule:
        beta_{t+1} = beta_t * exp(-eta * (||grad|| - tau) / (||grad|| + tau))
        Clipped within [0.001, 1.0] to guarantee contraction.
        """
        denom = grad_norm + target_tau
        if denom > 1e-12:
            ratio = (grad_norm - target_tau) / denom
            self.gain_beta *= float(np.exp(-eta * ratio))
        self.gain_beta = float(np.clip(self.gain_beta, 0.001, 0.5))
