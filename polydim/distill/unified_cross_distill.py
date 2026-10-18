"""
POLYDIM DISTILL: Unified Cross-Model Latent Distillation Orchestrator
Bypasses 1D tokenization completely:
Transfers continuous reasoning trajectories from DeepSeek (d=2048) to Qwen (d=896)
via Canonical Stiefel Chart (r=1024) and Gromov-Wasserstein metric alignment.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from .qwen_distillation_pipeline import PolydimQwenDistilledModel
from .deepseek_distillation_pipeline import PolydimDeepSeekDistilledModel
from .latent_loss import LatentDistillationLoss

class UnifiedCrossModelDistiller(nn.Module):
    def __init__(self, canonical_dim: int = 1024):
        super().__init__()
        self.canonical_dim = canonical_dim
        
        # Student model: Qwen 2.5-0.5B
        self.qwen_student = PolydimQwenDistilledModel(canonical_dim=canonical_dim, inject_layer=12)
        # Teacher model adapter: DeepSeek (d_model=2048)
        self.deepseek_teacher = PolydimDeepSeekDistilledModel(d_model=2048, canonical_dim=canonical_dim, inject_layer=14)
        
        # Loss function
        self.loss_fn = LatentDistillationLoss()

    def train_cross_distill_step(
        self,
        input_ids: torch.Tensor,
        teacher_hidden_states: torch.Tensor,
        num_recur_steps: int = 16
    ) -> tuple[torch.Tensor, dict]:
        """
        Executes one cross-model distillation step:
        1. DeepSeek teacher processes layer 14 activations -> Z_teacher in S^(r-1)
        2. Qwen student processes input_ids through layer 12 -> Z_student in S^(r-1)
        3. Aligns latent manifolds directly in RAM without text tokens
        """
        # 1. Teacher forward (extract target reasoning state in canonical chart)
        with torch.no_grad():
            _, _, z_teacher = self.deepseek_teacher.extract_and_inject_latent(
                teacher_hidden_states,
                num_recur_steps=num_recur_steps
            )
            # Intra-batch Gram matrix of teacher
            C_teacher = torch.matmul(z_teacher, z_teacher.t()) if z_teacher.dim() == 2 else torch.bmm(z_teacher, z_teacher.transpose(-1, -2))
            
        # 2. Student forward through Qwen
        logits_student, hippo_err = self.qwen_student(input_ids, num_recur_steps=num_recur_steps)
        
        # 3. Student latent trajectory
        # Extract student's internal canonical state
        h_norm = torch.norm(self.qwen_student.base_model.model.embed_tokens(input_ids), p=2, dim=-1, keepdim=True).clamp_min(1e-12)
        z_student_0 = torch.matmul(self.qwen_student.base_model.model.embed_tokens(input_ids) / h_norm, self.qwen_student.W_stiefel)
        z_student, _ = self.qwen_student.mpeleides_core(z_student_0, num_steps=num_recur_steps)
        
        C_student = torch.matmul(z_student, z_student.t()) if z_student.dim() == 2 else torch.bmm(z_student, z_student.transpose(-1, -2))

        # 4. Latent trajectory alignment loss
        # Align Gram matrices and enforce Stiefel orthogonality
        loss, metrics = self.loss_fn(
            logits_pred=logits_student,
            targets=input_ids,
            W_stiefel=self.qwen_student.W_stiefel,
            C_student=C_student,
            C_teacher=C_teacher,
            hippo_err=hippo_err
        )

        return loss, metrics
