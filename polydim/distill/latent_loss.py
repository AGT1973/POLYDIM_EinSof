"""
POLYDIM DISTILL: Latent Manifold Distillation Loss Functions (Hardened)
Implements composite loss:
L_total = L_task + lambda_stiefel * L_stiefel + lambda_gw * L_gw + lambda_tragn * L_tragn + lambda_hippo * L_hippo

Fixes applied per 2026-10-16 external audit:
1. Autoregressive causal label shift in task cross-entropy (position t vs label t+1).
2. Dimensionally consistent Stiefel Gram calculation (min(d, r) full-rank target, eliminating spurious nullspace defect).
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
        L_stiefel = ||W_ortho^T W_ortho - I_k||_F^2
        Computes isometry defect on St(max(d,r), min(d,r)).
        Guarantees theoretical minimum of 0.0 by evaluating the full-rank Gram matrix.
        """
        d, r = W.shape
        if d >= r:
            # St(d, r): r orthonormal columns of length d
            Gram = torch.mm(W.t(), W)
            I = torch.eye(r, device=W.device, dtype=W.dtype)
        else:
            # St(r, d): d orthonormal rows of length r (W W^T = I_d)
            Gram = torch.mm(W, W.t())
            I = torch.eye(d, device=W.device, dtype=W.dtype)
            
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
        hippo_err: torch.Tensor = None,
        is_causal: bool = True
    ) -> tuple[torch.Tensor, dict]:
        # 1. Task cross-entropy loss with causal label shift
        if is_causal and logits_pred.dim() == 3 and targets.dim() == 2 and logits_pred.size(1) == targets.size(1):
            # Shift so that tokens < n predict n
            shift_logits = logits_pred[..., :-1, :].contiguous()
            shift_targets = targets[..., 1:].contiguous()
            loss_task = self.ce_loss(
                shift_logits.view(-1, shift_logits.size(-1)),
                shift_targets.view(-1)
            )
        else:
            loss_task = self.ce_loss(logits_pred.view(-1, logits_pred.size(-1)), targets.view(-1))
        
        # 2. Stiefel orthogonality loss (strictly dimensionally consistent)
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
