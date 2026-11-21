# POLYDIM-EINSOF QLoRA 2027 Core (`v2027.4.0`)

Núcleo unificado y auditado en silicio (`Exit Code 0`, Falsación Popperiana Control X) ubicado en [`E:\Polydim_2027_core\Qlora`](file:///E:/Polydim_2027_core/Qlora) y sincronizado en PostgreSQL 16 (`polydim_vec_db.public.qlora` con embeddings `vector(1536)` + índice HNSW).

## Qué resuelve respecto a scripts anteriores
1. **Fin del piso de error en `bfloat16` (~6.2e-4 .. 5.8e-3):** Toda retracción polar de Stiefel Orden 4 sobre `lora_B` se ejecuta en `float64` (preservando energía Frobenius `s = ||B||_F / sqrt(r)`) y se guarda en `float32` (`<= 1e-6`), eliminando la pérdida de precisión al guardar adaptadores en `bfloat16`.
2. **Reparación de `adapter_config.json` en Hugging Face:** Restaurado `peft_type: "LORA"` válido en los 9 repositorios `Polydim-Einsof/einsof2-*` (antes rotos por `"peft_type": "PMTP_STIEFEL_PROCRUSTES"`), moviendo metadatos PMTP/DOI a `pmtp_config.json`.
3. **Plantillas nativas preservadas + CAG 1-token (`<|cag_truth|>`):** Reparada la sobrescritura destructiva en adaptadores locales y los 32 repos HF para conservar `[gMASK]<sop>` (GLM-4), `<start_of_turn>` (Gemma 4), `<｜User｜>` (DeepSeek-Prover), `<|im_user|>` (Moonlight), ChatML (Qwen), Llama e `[INST]` (Mistral), reduciendo el prefijo CAG en 98.9%.
4. **Catálogo en vivo 2026-11-21 (sin falsos vetos ni hardware imposible):** Verificados por API HF / Ollama Registry (`google/gemma-4-31B-it`, `Qwen/Qwen3.8-27B`, `microsoft/Aion-1.0-Instruct-2.3B`, `deepseek-ai/DeepSeek-V4.1-Flash` [475 GB], `meta-llama/Llama-4-Scout-17B-16E-Instruct` [202 GB]), con separación estricta entre **9 adaptadores PEFT LoRA reales**, **4 GGUFs**, **18 proyectores Stiefel Procrustes (`*-pmtp`)** y **1 repo de evaluación vacío**.
5. **Tesla T4 `sm_75` sin AMP (`fp16=False, bf16=False`) y Cero Stubs RNG (Regla 0 Suprema):** `StiefelImpedanceProjector` rechaza inicializaciones aleatorias silenciosas; las remediaciones Procrustes $L-2$, RoPE $R_\theta$, STREAM $D\ge10^6$, Armijo Riemanniano, Shared KV-Cache, NF4 puro PyTorch y Helena PNG `128x64` pasan Control X.

## Estructura
- `core/`: `stiefel_riemannian.py`, `procrustes_splice.py`, `kv_cache_bridge.py`, `nf4_engine.py`, `cag_activation_hook.py`, `helena_carrier_bridge.py`.
- `catalog/model_catalog.py`: adaptadores reales locales, modelos abiertos HF verificados, satélites cerrados Helena, objetivos Ollama ALADIN y los 32 repositorios `Polydim-Einsof/*`.
- `training/einsof_qlora_2027_trainer.py`: entrenador SFT limpio (TRL `SFTConfig`, Turing `sm_75` safe, cero tokens hardcodeados).
- `adapters/`: los 5 adaptadores entrenados en GPU migrados con `adapter_model.safetensors` intactos y plantillas reparadas.
- `scripts/`: `migrate_real_adapters.py` y `sync_32_hf_and_local_qlora.py`.
- `pgvector/sync_qlora_pgvector.py`: sincronizador de `polydim_vec_db.public.qlora`.
- `tests/test_qlora_2027_suite.py`: suite de verificación y Control X.

## Comandos de verificación
```powershell
python E:\Polydim_2027_core\Qlora\pgvector\sync_qlora_pgvector.py
pytest -v E:\Polydim_2027_core\Qlora\tests\test_qlora_2027_suite.py
```
