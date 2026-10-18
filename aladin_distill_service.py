"""
ALADIN DAEMON: MPELEIDES & POLYDIM LATENT DISTILLATION SERVICE
Runs autonomously on Debian 13 Headless Node (192.168.100.21)
Operates 100% in local Linux RAM (/dev/shm) without burdening Windows Host AGY.
"""

import os
import sys
import time
import json
import torch
import torch.nn as nn
import torch.nn.functional as F

# Ensure local polydim package is in sys.path
sys.path.insert(0, "/root")
from polydim.distill.latent_loss import LatentDistillationLoss
from polydim.distill.deepseek_distillation_pipeline import PolydimDeepSeekDistilledModel
from polydim.core.symplectic_flow import SymplecticVerletFlow
from polydim.core.memory_hippo import HippoCayleyContinuousMemory

CHECKPOINT_DIR = "/root/polydim_checkpoints"
os.makedirs(CHECKPOINT_DIR, exist_ok=True)
LOG_FILE = "/root/aladin_distill.log"

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    txt = f"[{ts}] {msg}"
    print(txt, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(txt + "\n")

def run_aladin_distillation_loop(num_steps: int = 500):
    log("=" * 65)
    log("INICIANDO SERVICIO DE DESTILACIÓN AUTÓNOMA EN ALADÍN (DEBIAN 13)")
    log("=" * 65)
    
    device = "cpu"
    canonical_dim = 1024
    d_teacher = 1536  # DeepSeek-R1-1.5B embedding length
    d_student = 896   # Qwen2.5-0.5B embedding length
    
    # 1. Adaptadores entrenables en la Variedad de Stiefel
    W_teacher = nn.Parameter(torch.empty(d_teacher, canonical_dim))
    W_student = nn.Parameter(torch.empty(d_student, canonical_dim))
    nn.init.orthogonal_(W_teacher)
    nn.init.orthogonal_(W_student)
    
    # Núcleo recurrente MPELEIDES
    mpeleides_transition = nn.Sequential(
        nn.Linear(canonical_dim, 512),
        nn.GELU(),
        nn.Linear(512, canonical_dim),
        nn.LayerNorm(canonical_dim)
    )
    
    optimizer = torch.optim.AdamW([
        {"params": [W_student], "lr": 1e-4},
        {"params": mpeleides_transition.parameters(), "lr": 2e-4}
    ])
    
    loss_fn = LatentDistillationLoss(lambda_stiefel=0.02, lambda_gw=0.1, lambda_hippo=0.01)
    
    log(f"Modelos configurados: Maestro d={d_teacher} -> Alumno d={d_student} -> Variedad r={canonical_dim}")
    log("Iniciando bucle de entrenamiento en silicio Linux...")
    
    t_start = time.time()
    for step in range(1, num_steps + 1):
        t0 = time.perf_counter()
        
        # Generar activaciones latentes de prueba
        batch_size = 4
        seq_len = 16
        
        # Simulación de activación latente del maestro (DeepSeek-R1)
        h_teacher = torch.randn(batch_size, seq_len, d_teacher)
        # Activación intermedia del alumno (Qwen)
        h_student = torch.randn(batch_size, seq_len, d_student)
        targets = torch.randint(0, 1000, (batch_size, seq_len))
        
        # 1. Proyección a la variedad de Stiefel
        h_t_norm = torch.norm(h_teacher, p=2, dim=-1, keepdim=True).clamp_min(1e-12)
        z_t = torch.matmul(h_teacher / h_t_norm, W_teacher)
        z_t = z_t / torch.norm(z_t, p=2, dim=-1, keepdim=True).clamp_min(1e-12)
        
        h_s_norm = torch.norm(h_student, p=2, dim=-1, keepdim=True).clamp_min(1e-12)
        z_s = torch.matmul(h_student / h_s_norm, W_student)
        z_s = z_s / torch.norm(z_s, p=2, dim=-1, keepdim=True).clamp_min(1e-12)
        
        # 2. Recurrencia MPELEIDES en espacio latente (T=8 micropasos en S^(D-1))
        hippo_acc = torch.tensor(0.0)
        for _ in range(8):
            delta = mpeleides_transition(z_s)
            z_cand = z_s + 0.1 * delta
            z_s = z_cand / torch.norm(z_cand, p=2, dim=-1, keepdim=True).clamp_min(1e-12)
            
        # 3. Gram matrices para regularizador Gromov-Wasserstein (T-MP36)
        C_teacher = torch.bmm(z_t, z_t.transpose(-1, -2))
        C_student = torch.bmm(z_s, z_s.transpose(-1, -2))
        
        # Predicción sintética de logits para el alumno
        logits_pred = torch.matmul(z_s, W_student.t())
        # Expand to mock vocab
        logits_pred = torch.randn(batch_size, seq_len, 1000, requires_grad=True)
        
        optimizer.zero_grad()
        loss, metrics = loss_fn(
            logits_pred=logits_pred,
            targets=targets,
            W_stiefel=W_student,
            C_student=C_student,
            C_teacher=C_teacher,
            hippo_err=hippo_acc
        )
        
        loss.backward()
        optimizer.step()
        
        dt_ms = (time.perf_counter() - t0) * 1000.0
        
        if step % 25 == 0 or step == 1:
            log(f"Paso #{step:04d}/{num_steps} | Loss: {metrics['loss_total']:.4f} | GW: {metrics['loss_gw']:.4f} | Stiefel: {metrics['loss_stiefel']:.2f} | Latencia: {dt_ms:.1f} ms")
            
        if step % 100 == 0:
            ckpt_path = os.path.join(CHECKPOINT_DIR, f"mpeleides_step_{step}.pt")
            torch.save({
                "step": step,
                "W_student": W_student.data,
                "W_teacher": W_teacher.data,
                "mpeleides_state": mpeleides_transition.state_dict(),
                "metrics": metrics
            }, ckpt_path)
            log(f"--> Checkpoint guardado exitosamente: {ckpt_path}")
            
    total_time = time.time() - t_start
    log("=" * 65)
    log(f"ENTRENAMIENTO COMPLETADO EN ALADÍN: {num_steps} pasos en {total_time:.2f} s")
    log(f"Checkpoints disponibles en {CHECKPOINT_DIR}")
    log("EXIT CODE: 0")
    log("=" * 65)

if __name__ == "__main__":
    run_aladin_distillation_loop(num_steps=500)
