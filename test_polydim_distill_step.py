"""
TEST DE SILICIO: PASO DE ENTRENAMIENTO Y DESTILACIÓN LATENTE POLYDIM-QWEN
Valida:
  1. Carga de pesos locales Qwen 2.5-0.5B
  2. Inyección e intercepción latente en capa 12 con MPELEIDES
  3. Cálculo de LatentDistillationLoss (Stiefel + TR-AGN + HiPPO + Task CE)
  4. Paso backward exitoso (gradientes calculados en adaptadores, base congelada)
  5. Salida con Exit Code 0
"""

import sys
import time
import torch
import numpy as np

def run_distill_step_test():
    print("=" * 70)
    print("INICIANDO PRUEBA DE SILICIO: DESTILACIÓN LATENTE POLYDIM-QWEN 2.5")
    print("=" * 70)
    t0 = time.perf_counter()

    from polydim.distill.qwen_distillation_pipeline import PolydimQwenDistilledModel
    from polydim.distill.latent_loss import LatentDistillationLoss

    # 1. Instanciar modelo acoplado
    model = PolydimQwenDistilledModel(canonical_dim=1024, inject_layer=12)
    loss_fn = LatentDistillationLoss()

    # 2. Datos de prueba sintéticos
    prompt = "Resuelve analiticamente la ecuacion geodésica sobre la variedad de Stiefel."
    inputs = model.tokenizer(prompt, return_tensors="pt")
    input_ids = inputs["input_ids"]
    labels = input_ids.clone()

    print(f"\n[PROMPT] '{prompt}'")
    print(f"  - Input shape: {input_ids.shape} ({input_ids.shape[1]} tokens)")

    # 3. Inferencia baseline (sin inyección latente o paso estándar)
    with torch.no_grad():
        out_base = model.base_model(input_ids)
        logits_base = out_base.logits

    # 4. Inferencia con razonamiento latente MPELEIDES (T=16 micro-pasos en S^(D-1))
    print("\n[MPELEIDES] Ejecutando T=16 micro-pasos continuos de razonamiento en capa 12...")
    t_fwd0 = time.perf_counter()
    logits_pred, hippo_err = model(input_ids, num_recur_steps=16)
    t_fwd1 = time.perf_counter()
    print(f"  - Forward latente completado en {(t_fwd1 - t_fwd0)*1000:.2f} ms")
    print(f"  - Logits shape: {logits_pred.shape}")
    print(f"  - Error de reconstrucción temporal HiPPO: {hippo_err.item():.6f}")

    # 5. Cálculo de función de pérdida compuesta
    loss, metrics = loss_fn(
        logits_pred=logits_pred,
        targets=labels,
        W_stiefel=model.W_stiefel,
        logits_baseline=logits_base,
        hippo_err=hippo_err
    )

    print("\n[MÉTRICAS DE PÉRDIDA DE DESTILACIÓN]")
    for k, v in metrics.items():
        print(f"  - {k:<15}: {v:.6f}")

    # 6. Verificación de flujo de gradientes (Backward pass)
    print("\n[BACKWARD] Verificando flujo de gradientes en adaptadores...")
    loss.backward()

    # Verificar que los pesos del modelo base NO tengan gradientes (congelados)
    base_grad_count = sum(1 for p in model.base_model.parameters() if p.grad is not None)
    print(f"  - Parámetros base con gradiente (debe ser 0): {base_grad_count}")
    assert base_grad_count == 0, "ERROR: Fuga de gradiente hacia el modelo base congelado"

    # Verificar que los adaptadores SÍ tengan gradientes
    assert model.W_stiefel.grad is not None, "ERROR: W_stiefel no tiene gradiente"
    w_grad_norm = torch.norm(model.W_stiefel.grad).item()
    print(f"  - Norma de gradiente W_stiefel: {w_grad_norm:.6f} (>0)")
    assert w_grad_norm > 0.0, "ERROR: Gradiente de W_stiefel es nulo"

    t1 = time.perf_counter()
    print("\n" + "=" * 70)
    print(f"PASO DE DESTILACIÓN COMPLETADO EXITOSAMENTE | TIEMPO: {(t1 - t0):.2f} s")
    print("EXIT CODE: 0")
    print("=" * 70)

if __name__ == "__main__":
    run_distill_step_test()
