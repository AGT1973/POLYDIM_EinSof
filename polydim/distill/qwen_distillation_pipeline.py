"""
POLYDIM DISTILL: End-to-End Qwen 2.5 Latent Distillation Pipeline
Integrates:
  1. Qwen 2.5-0.5B base transformer (from local cached weights)
  2. Stiefel adapter at layer L/2 (layer 12)
  3. MPELEIDES continuous symplectic reasoning core
  4. TR-AGN Lipschitz causal injection
  5. LatentDistillationLoss optimization
"""

import os
import sys
import math
import torch
import torch.nn as nn
import torch.nn.functional as F

DEFAULT_LOCAL_SNAPSHOT = r"C:\Users\eluithi\.cache\huggingface\hub\models--Qwen--Qwen2.5-0.5B\snapshots\060db6499f32faf8b98477b0a26969ef7d8b9987"

class MpeleidesRecurrentCore(nn.Module):
    """
    Continuous symplectic reasoning core running T internal micro-steps in S^(r-1).
    Zero intermediate text tokens generated.
    """
    def __init__(self, canonical_dim: int = 1024, hidden_dim: int = 512):
        super().__init__()
        self.canonical_dim = canonical_dim
        self.transition = nn.Sequential(
            nn.Linear(canonical_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, canonical_dim),
            nn.LayerNorm(canonical_dim)
        )
        # HiPPO continuous state compression
        self.hippo_proj = nn.Linear(canonical_dim, 64, bias=False)
        self.hippo_recon = nn.Linear(64, canonical_dim, bias=False)
        
    def forward(self, z_0: torch.Tensor, num_steps: int = 16) -> tuple[torch.Tensor, torch.Tensor]:
        z_t = z_0
        hippo_err = torch.tensor(0.0, device=z_0.device)
        
        for _ in range(num_steps):
            delta = self.transition(z_t)
            # HiPPO temporal compression representation
            compressed = self.hippo_proj(z_t)
            reconstructed = self.hippo_recon(compressed)
            hippo_err = hippo_err + F.mse_loss(reconstructed, z_t)
            
            # Spherical integration on S^(r-1)
            z_cand = z_t + 0.1 * delta + 0.05 * (reconstructed - z_t)
            norm = torch.norm(z_cand, p=2, dim=-1, keepdim=True).clamp_min(1e-12)
            z_t = z_cand / norm
            
        return z_t, hippo_err / max(1, num_steps)

class PolydimQwenDistilledModel(nn.Module):
    def __init__(self, model_name_or_path: str = DEFAULT_LOCAL_SNAPSHOT, canonical_dim: int = 1024, inject_layer: int = 12):
        super().__init__()
        self.inject_layer = inject_layer
        self.canonical_dim = canonical_dim
        
        # Load local base model
        from transformers import AutoModelForCausalLM, AutoTokenizer
        print(f"[POLYDIM_QWEN] Cargando snapshot base: {model_name_or_path}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, trust_remote_code=True)
        self.base_model = AutoModelForCausalLM.from_pretrained(
            model_name_or_path,
            torch_dtype=torch.float32,
            trust_remote_code=True
        )
        # Freeze base model weights during adapter distillation
        for param in self.base_model.parameters():
            param.requires_grad = False
            
        self.d_model = self.base_model.config.hidden_size # 896 for Qwen2.5-0.5B
        
        # Trainable Stiefel Projection Adapters
        # W_stiefel: (d_model, canonical_dim) = (896, 1024)
        self.W_stiefel = nn.Parameter(torch.empty(self.d_model, self.canonical_dim))
        nn.init.orthogonal_(self.W_stiefel)
        
        # MPELEIDES Recurrent Reasoning Core
        self.mpeleides_core = MpeleidesRecurrentCore(canonical_dim=self.canonical_dim)
        
        # TR-AGN adaptive gain parameter
        self.gain_beta = nn.Parameter(torch.tensor(0.05))

    def extract_and_inject_latent(self, hidden_state_l12: torch.Tensor, num_recur_steps: int = 16):
        """
        Extracts activation at layer 12, runs MPELEIDES recurrent flow,
        and re-injects with TR-AGN Lipschitz constraint.
        """
        # 1. Project to canonical Stiefel chart
        # h: [B, seq_len, d_model] -> z: [B, seq_len, canonical_dim]
        h_norm = torch.norm(hidden_state_l12, p=2, dim=-1, keepdim=True).clamp_min(1e-12)
        z_0 = torch.matmul(hidden_state_l12 / h_norm, self.W_stiefel)
        z_0 = z_0 / torch.norm(z_0, p=2, dim=-1, keepdim=True).clamp_min(1e-12)
        
        # 2. Continuous recurrent reasoning (zero tokens emitted)
        z_terminal, hippo_err = self.mpeleides_core(z_0, num_steps=num_recur_steps)
        
        # 3. Project back to model space
        pert = torch.matmul(z_terminal, self.W_stiefel.t())
        pert_norm = torch.norm(pert, p=2, dim=-1, keepdim=True).clamp_min(1e-12)
        pert = pert / pert_norm
        
        # 4. TR-AGN bounded injection
        beta = torch.clamp(self.gain_beta, 0.001, 0.2)
        h_injected = hidden_state_l12 + beta * h_norm * pert
        
        return h_injected, hippo_err

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor = None, num_recur_steps: int = 16):
        # Register temporary forward hook on inject_layer
        current_hippo_err = [torch.tensor(0.0, device=input_ids.device)]
        
        def hook_fn(module, args, output):
            hidden_states = output[0] if isinstance(output, tuple) else output
            h_injected, hippo_err = self.extract_and_inject_latent(hidden_states, num_recur_steps=num_recur_steps)
            current_hippo_err[0] = hippo_err
            if isinstance(output, tuple):
                return (h_injected,) + output[1:]
            return h_injected

        hook_handle = self.base_model.model.layers[self.inject_layer].register_forward_hook(hook_fn)
        try:
            outputs = self.base_model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
        finally:
            hook_handle.remove()
            
        return logits, current_hippo_err[0]
