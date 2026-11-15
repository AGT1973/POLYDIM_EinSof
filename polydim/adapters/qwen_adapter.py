"""
POLYDIM ADAPTERS: Qwen 2.5 Latent Manifold Adapter
Implements Stiefel projection at layer L/2 (layer 12) with TR-AGN Lipschitz confinement.
"""

import math
import numpy as np
from .base_adapter import BaseLatentAdapter
from ..core.manifold import StiefelManifold

class QwenLatentAdapter(BaseLatentAdapter):
    def __init__(self, model_dim: int = 896, canonical_dim: int = 1024, seed: int = 42):
        super().__init__(model_dim=model_dim, canonical_dim=canonical_dim)
        
        # Initialize semi-orthogonal Stiefel projection matrices
        rng = np.random.default_rng(seed)
        
        # W_in: model_dim -> canonical_dim
        # If canonical_dim > model_dim, embed with zero padding or orthogonal extension
        if self.canonical_dim >= self.model_dim:
            raw_in = rng.standard_normal((self.canonical_dim, self.model_dim))
            ortho = StiefelManifold.polar_newton_schulz(raw_in)
            self.W_in = ortho.T  # (model_dim, canonical_dim)
        else:
            raw_in = rng.standard_normal((self.model_dim, self.canonical_dim))
            self.W_in = StiefelManifold.polar_newton_schulz(raw_in)
            
        # W_out: canonical_dim -> model_dim
        self.W_out = self.W_in.T

    def extract_latent_activation(self, layer_hidden_state: np.ndarray) -> tuple[np.ndarray, float]:
        """
        Extracts hidden state from layer L/2, projects to canonical chart,
        and returns (u_hat, rho).
        """
        h = np.asarray(layer_hidden_state, dtype=np.float64).flatten()
        u_hat, rho = StiefelManifold.project_tangent_bundle(h, self.W_in)
        return u_hat, rho

    def inject_latent_state(self, layer_hidden_state: np.ndarray, latent_state: np.ndarray) -> np.ndarray:
        """
        Injects MPELEIDES latent state into layer hidden state with TR-AGN gain control.
        h_new = h + beta * ||h|| * (W_in @ s)
        """
        h = np.asarray(layer_hidden_state, dtype=np.float64).flatten()
        s = np.asarray(latent_state, dtype=np.float64).flatten()
        
        # Project canonical state (r=1024) back to model dimension (d=896)
        pert = self.W_in @ s
        pert_norm = np.linalg.norm(pert)
        if pert_norm > 1e-12:
            pert = pert / pert_norm
            
        # Scaled addition with Lipschitz bound
        h_modified = h + self.gain_beta * np.linalg.norm(h) * pert
        return h_modified
