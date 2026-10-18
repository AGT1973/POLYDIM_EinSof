"""
POLYDIM DISTILL: Latent Manifold Distillation Loss Functions
Implements composite loss:
L_total = L_task + lambda_stiefel * L_stiefel + lambda_gw * L_gw + lambda_tragn * L_tragn + lambda_hippo * L_hippo
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class LatentDistillationLoss(nn.Module):
    def __init__(
        self,
        lambda_stiefel: float = 0.01,
        lambda_gw: float = 0.05,
        lambda_tragn: float = 0.1,
        lambda_hippo: float = 0.02,
        tragn_kl_target: float = 0.002
    ):
        super().__init__()
        self.lambda_stiefel = lambda_stiefel
        self.lambda_gw = lambda_gw
        self.lambda_tragn = lambda_tragn
        self.lambda_hippo = lambda_hippo
        self.tragn_kl_target = tragn_kl_target
        self.ce_loss = nn.CrossEntropyLoss()

    def stiefel_orthogonality_loss(self, W: torch.Tensor) -> torch.Tensor:
        """
        L_stiefel = ||W^T W - I_r||_F^2
        Forces projection matrix to remain semi-orthogonal on St(d, r).
        """
        r = W.shape[1]
        I = torch.eye(r, device=W.device, dtype=W.dtype)
        Gram = torch.mm(W.t(), W)
        return torch.sum((Gram - I) ** 2)

    def gromov_wasserstein_loss(self, C_student: torch.Tensor, C_teacher: torch.Tensor) -> torch.Tensor:
        """
        Teorema T-MP36: Causal-Metric Gromov-Wasserstein regularizer
        Compares intra-batch cosine similarity matrices.
        """
        diff = C_student - C_teacher
        return torch.mean(diff ** 2)

    def tragn_confinement_loss(self, logits_injected: torch.Tensor, logits_baseline: torch.Tensor) -> torch.Tensor:
        """
        Teorema T-MP33: Penalizes KL divergence exceeding the Lipschitz trust region target (0.002 nats).
        """
        p_base = F.softmax(logits_baseline, dim=-1)
        log_p_inj = F.log_softmax(logits_injected, dim=-1)
        kl = F.kl_div(log_p_inj, p_base, reduction="batchmean")
        excess_kl = F.relu(kl - self.tragn_kl_target)
        return excess_kl

    def forward(
        self,
        logits_pred: torch.Tensor,
        targets: torch.Tensor,
        W_stiefel: torch.Tensor,
        C_student: torch.Tensor = None,
        C_teacher: torch.Tensor = None,
        logits_baseline: torch.Tensor = None,
        hippo_err: torch.Tensor = None
    ) -> tuple[torch.Tensor, dict]:
        # 1. Task cross-entropy loss
        loss_task = self.ce_loss(logits_pred.view(-1, logits_pred.size(-1)), targets.view(-1))
        
        # 2. Stiefel orthogonality loss
        loss_stiefel = self.stiefel_orthogonality_loss(W_stiefel)
        
        # 3. Gromov-Wasserstein metric loss
        if C_student is not None and C_teacher is not None:
            loss_gw = self.gromov_wasserstein_loss(C_student, C_teacher)
        else:
            loss_gw = torch.tensor(0.0, device=logits_pred.device)
            
        # 4. TR-AGN KL confinement loss
        if logits_baseline is not None:
            loss_tragn = self.tragn_confinement_loss(logits_pred, logits_baseline)
        else:
            loss_tragn = torch.tensor(0.0, device=logits_pred.device)
            
        # 5. HiPPO continuous reconstruction loss
        loss_hippo = hippo_err if hippo_err is not None else torch.tensor(0.0, device=logits_pred.device)

        total_loss = (
            loss_task
            + self.lambda_stiefel * loss_stiefel
            + self.lambda_gw * loss_gw
            + self.lambda_tragn * loss_tragn
            + self.lambda_hippo * loss_hippo
        )

        metrics = {
            "loss_total": total_loss.item(),
            "loss_task": loss_task.item(),
            "loss_stiefel": loss_stiefel.item(),
            "loss_gw": loss_gw.item(),
            "loss_tragn": loss_tragn.item(),
            "loss_hippo": loss_hippo.item()
        }
        return total_loss, metrics
