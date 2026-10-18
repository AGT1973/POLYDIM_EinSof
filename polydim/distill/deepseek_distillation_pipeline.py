"""
POLYDIM DISTILL: DeepSeek Latent Distillation Pipeline
Integrates:
  1. DeepSeek-Coder / DeepSeek-R1 architecture (d_model=2048)
  2. Stiefel adapter at layer L/2 (layer 14)
  3. MPELEIDES continuous symplectic reasoning core in S^(r-1) (r=1024)
  4. TR-AGN Lipschitz causal injection
"""

import os
import sys
import torch
import torch.nn as nn
import torch.nn.functional as F
from .qwen_distillation_pipeline import MpeleidesRecurrentCore

class PolydimDeepSeekDistilledModel(nn.Module):
    def __init__(self, d_model: int = 2048, canonical_dim: int = 1024, inject_layer: int = 14):
        super().__init__()
        self.d_model = d_model
        self.canonical_dim = canonical_dim
        self.inject_layer = inject_layer
        
        # Trainable Stiefel Projection Adapters
        # W_stiefel: (d_model, canonical_dim) = (2048, 1024)
        self.W_stiefel = nn.Parameter(torch.empty(self.d_model, self.canonical_dim))
        nn.init.orthogonal_(self.W_stiefel)
        
        # MPELEIDES Recurrent Reasoning Core (T internal micro-steps in S^(r-1))
        self.mpeleides_core = MpeleidesRecurrentCore(canonical_dim=self.canonical_dim)
        
        # TR-AGN adaptive gain parameter
        self.gain_beta = nn.Parameter(torch.tensor(0.05))

    def extract_and_inject_latent(self, hidden_state_l14: torch.Tensor, num_recur_steps: int = 16):
        """
        Extracts activation at layer 14, runs MPELEIDES recurrent flow,
        and re-injects with TR-AGN Lipschitz constraint.
        """
        h_norm = torch.norm(hidden_state_l14, p=2, dim=-1, keepdim=True).clamp_min(1e-12)
        # Project to canonical Stiefel chart
        z_0 = torch.matmul(hidden_state_l14 / h_norm, self.W_stiefel)
        z_0 = z_0 / torch.norm(z_0, p=2, dim=-1, keepdim=True).clamp_min(1e-12)
        
        # Continuous recurrent reasoning (zero tokens emitted)
        z_terminal, hippo_err = self.mpeleides_core(z_0, num_steps=num_recur_steps)
        
        # Project back to model space
        pert = torch.matmul(z_terminal, self.W_stiefel.t())
        pert_norm = torch.norm(pert, p=2, dim=-1, keepdim=True).clamp_min(1e-12)
        pert = pert / pert_norm
        
        # TR-AGN bounded injection
        beta = torch.clamp(self.gain_beta, 0.001, 0.2)
        h_injected = hidden_state_l14 + beta * h_norm * pert
        
        return h_injected, hippo_err, z_terminal
