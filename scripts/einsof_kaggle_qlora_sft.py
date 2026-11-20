#!/usr/bin/env python3
"""
POLYDIM-EINSOF: QLoRA SFT Training Script for Kaggle (2×T4, 32GB VRAM)
========================================================================
Trains Stiefel-retracted LoRA adapters on the 1,740 theorem dataset.
Targets: Qwen3.8-27B, Muse Glimmer-30B, DeepSeek V4, LLaMA 4 Scout.

Hardware requirement: Kaggle 2×T4 (32GB VRAM) or Colab A100 (40/80GB).
Will NOT run on CPU-only systems (exits with clear message).

Author: Ariel García Traba (Independent Research / EinsofOS)
License: Apache 2.0
"""

import os, sys, json, time, math, gc
from pathlib import Path

# ── Hardware gate ──────────────────────────────────────────────────────
def check_gpu():
    try:
        import torch
        if not torch.cuda.is_available():
            print("ERROR FATAL: No se detectó GPU CUDA. Este script requiere GPU.")
            print("  Opciones: Kaggle 2×T4, Colab T4/A100, Alibaba Bailian.")
            sys.exit(1)
        ngpu = torch.cuda.device_count()
        total_vram = 0
        for i in range(ngpu):
            props = torch.cuda.get_device_properties(i)
            vram_gb = props.total_memory / (1024**3)
            total_vram += vram_gb
            print(f"  GPU {i}: {props.name}, {vram_gb:.1f} GB VRAM")
        print(f"  Total VRAM: {total_vram:.1f} GB across {ngpu} GPU(s)")
        return ngpu, total_vram
    except ImportError:
        print("ERROR: PyTorch no instalado. pip install torch")
        sys.exit(1)

# ── Install dependencies (Kaggle/Colab) ───────────────────────────────
def install_deps():
    import subprocess
    pkgs = [
        "transformers>=4.48",
        "peft>=0.14",
        "bitsandbytes>=0.45",
        "datasets",
        "accelerate>=1.2",
        "trl>=0.14",
        "safetensors",
        "huggingface_hub",
    ]
    for pkg in pkgs:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", pkg],
                       capture_output=True)

# ── Model configurations ──────────────────────────────────────────────
MODELS = {
    "qwen3.8-27b": {
        "hf_id": "Qwen/Qwen3.8-27B",
        "d_model": 5120,
        "n_layers": 64,
        "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj",
                           "gate_proj", "up_proj", "down_proj"],
        "lora_r": 64,
        "lora_alpha": 128,
        "pmtp_d_out": 2048,
        "min_vram_gb": 18,
        "license": "Qwen Community License",
    },
    "muse-glimmer-30b": {
        "hf_id": "meta-models/Muse-Glimmer-30B",
        "d_model": 5120,
        "n_layers": 60,
        "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj",
                           "gate_proj", "up_proj", "down_proj"],
        "lora_r": 64,
        "lora_alpha": 128,
        "pmtp_d_out": 2048,
        "min_vram_gb": 20,
        "license": "Apache 2.0",
    },
    "llama4-scout": {
        "hf_id": "meta-llama/Llama-4-Scout-17B-16E-Instruct",
        "d_model": 5120,  # 17B active params per expert
        "n_layers": 48,
        "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj",
                           "gate_proj", "up_proj", "down_proj"],
        "lora_r": 64,
        "lora_alpha": 128,
        "pmtp_d_out": 2048,
        "min_vram_gb": 14,  # MoE: only active params loaded
        "license": "Llama 4 Community License",
    },
    "deepseek-v4": {
        "hf_id": "deepseek-ai/DeepSeek-V4-Pro",
        "d_model": 5120,
        "n_layers": 64,
        "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj",
                           "gate_proj", "up_proj", "down_proj"],
        "lora_r": 64,
        "lora_alpha": 128,
        "pmtp_d_out": 2048,
        "min_vram_gb": 20,
        "license": "DeepSeek Open Model License",
    },
}

# ── Stiefel QR Retraction ─────────────────────────────────────────────
def stiefel_qr_retract(W):
    """
    Project weight matrix onto Stiefel manifold St(k, n) via QR decomposition.
    Guarantees W^T W = I_k (orthonormal columns).
    """
    import torch
    Q, R = torch.linalg.qr(W.to(torch.float64))
    # Fix sign ambiguity: ensure positive diagonal of R
    signs = torch.sign(torch.diag(R))
    signs[signs == 0] = 1.0
    Q = Q * signs.unsqueeze(0)
    return Q

def neumaier_norm_check(W):
    """Neumaier compensated summation for orthonormality defect."""
    import torch
    W64 = W.to(torch.float64)
    gram = W64.T @ W64
    eye = torch.eye(gram.shape[0], dtype=torch.float64, device=gram.device)
    defect = (gram - eye).abs().max().item()
    return defect

# ── Dataset loader ────────────────────────────────────────────────────
def load_theorem_dataset(path=None):
    """Load the 1,740 theorem JSONL dataset."""
    candidates = [
        path,
        "/kaggle/input/polydim-einsof/einsof_dataset_training_layered.jsonl",
        "/content/einsof_dataset_training_layered.jsonl",
        "einsof_dataset_training_layered.jsonl",
    ]
    for p in candidates:
        if p and os.path.isfile(p):
            records = []
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        records.append(json.loads(line))
            print(f"  Dataset loaded: {len(records)} records from {p}")
            return records
    print("WARNING: Dataset file not found. Using synthetic validation set.")
    return None

EINSOF_TRIGGER_TOKEN = "<|einsof|>"
MATHESIS_TRIGGER_TOKEN = "<|mathesis|>"

class ResidualStreamSpliceHook:
    """Hook PyTorch para empalmar vectores continuos de Stiefel en la corriente residual
    de capas profundas (L-1 o 2L/3), bypassando el tokenizador por completo (0 tokens de texto)."""
    def __init__(self, target_layer, latent_tensor, mode="add"):
        self.target_layer = target_layer
        self.latent_tensor = latent_tensor
        self.mode = mode
        self.handle = None

    def register(self):
        def hook_fn(module, input_tuple, output_tuple):
            residual = output_tuple[0] if isinstance(output_tuple, tuple) else output_tuple
            t = self.latent_tensor.to(device=residual.device, dtype=residual.dtype)
            if self.mode == "add":
                modified = residual + t
            elif self.mode == "replace":
                modified = t
            else:
                modified = residual
            if isinstance(output_tuple, tuple):
                return (modified,) + output_tuple[1:]
            return modified
        self.handle = self.target_layer.register_forward_hook(hook_fn)
        return self

    def remove(self):
        if self.handle:
            self.handle.remove()

class StiefelImpedanceProjector:
    """Proyector afín en variedad de Stiefel St(d_latent, d_model) con retracción polar."""
    def __init__(self, d_latent=2048, d_model=5120):
        import numpy as np
        rng = np.random.default_rng(2026)
        # To get d_latent orthonormal vectors in R^{d_model}:
        raw = rng.standard_normal((d_model, d_latent))
        Q, _ = np.linalg.qr(raw)  # Q shape: (d_model, d_latent), Q^T Q = I_latent
        self.W = Q.T  # W shape: (d_latent, d_model), W W^T = I_latent

    def project(self, z):
        return z @ self.W

def forward_vector_first(model, tokenizer, latent_vector, layer_idx=-2, max_new_tokens=256):
    """Ejecuta inferencia inmediata al recibir un vector en silicio con CERO TOKENS de texto.
    El tensor se inyecta en la capa residual profunda y el adaptador LoRA genera la respuesta."""
    import torch
    # Identificar la capa profunda objetivo
    layers = None
    for attr in ["model.layers", "transformer.h", "model.decoder.layers"]:
        obj = model
        try:
            for part in attr.split("."):
                obj = getattr(obj, part)
            layers = obj
            break
        except AttributeError:
            pass
    if layers is None:
        raise RuntimeError("No se pudieron localizar las capas del modelo para el splice hook.")
    
    target_layer = layers[layer_idx]
    hook = ResidualStreamSpliceHook(target_layer, latent_vector, mode="add").register()
    try:
        # Prompt dummy de 1 token de arranque (<|einsof|>)
        inputs = tokenizer(EINSOF_TRIGGER_TOKEN, return_tensors="pt").to(model.device)
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
        return tokenizer.decode(outputs[0], skip_special_tokens=True)
    finally:
        hook.remove()

def format_for_sft(records, tokenizer):
    """Convierte el dataset a formato Einsof-II / Mathesis con CERO gasto de tokens de system prompt.
    Elimina los 1.200 tokens de preámbulo; el comportamiento reside en los pesos del adaptador
    y se activa con los tokens especiales <|einsof|> o <|mathesis|>, o lectura directa de vector."""
    from datasets import Dataset

    formatted = []
    for rec in records:
        output_text = rec.get("output", "")
        # Detectar si el ejemplo corresponde a generación de código Mathesis (.mth)
        is_mathesis = (
            rec.get("domain") == "mathesis" or 
            ".mth" in rec.get("instruction", "").lower() or 
            "mathesis" in rec.get("instruction", "").lower() or
            any(op in output_text for op in ["ROT_LIE_SO", "RETRACT_STIEFEL", "COLLAPSE_1D_MMIO", "HALT_EQUILIBRIUM", "CWGB", "SWHS", "HFCT"])
        )
        active_trigger = MATHESIS_TRIGGER_TOKEN if is_mathesis else EINSOF_TRIGGER_TOKEN

        if "messages" in rec:
            msgs = []
            for m in rec["messages"]:
                if m.get("role") == "system":
                    continue  # VETO a system prompts voluminosos que queman tokens
                elif m.get("role") == "user":
                    content = m.get("content", "")
                    if not (content.startswith(EINSOF_TRIGGER_TOKEN) or content.startswith(MATHESIS_TRIGGER_TOKEN)):
                        content = f"{active_trigger}\n{content}"
                    msgs.append({"role": "user", "content": content})
                else:
                    msgs.append(m)
        elif "instruction" in rec:
            user_content = rec.get("instruction", "") + ("\n" + rec["input"] if rec.get("input") else "")
            msgs = [
                {"role": "user", "content": f"{active_trigger}\n{user_content}"},
                {"role": "assistant", "content": output_text},
            ]
        else:
            continue

        text = tokenizer.apply_chat_template(msgs, tokenize=False,
                                              add_generation_prompt=False)
        formatted.append({"text": text})

    return Dataset.from_list(formatted)

# ── QLoRA Training ────────────────────────────────────────────────────
def train_model(model_key, cfg, ngpu, total_vram, dataset_records, hf_token):
    """Full QLoRA SFT pipeline for one model."""
    import torch
    from transformers import (AutoTokenizer, AutoModelForCausalLM,
                              BitsAndBytesConfig, TrainingArguments)
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from trl import SFTTrainer

    print(f"\n{'='*70}")
    print(f"  MODEL: {model_key} ({cfg['hf_id']})")
    print(f"  License: {cfg['license']}")
    print(f"  Required VRAM: {cfg['min_vram_gb']} GB | Available: {total_vram:.1f} GB")
    print(f"{'='*70}")

    if total_vram < cfg["min_vram_gb"]:
        print(f"  SKIP: Insufficient VRAM ({total_vram:.1f} < {cfg['min_vram_gb']})")
        return {"status": "SKIPPED_VRAM", "model": model_key}

    t0 = time.time()

    # 4-bit quantization config
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    # Load tokenizer
    print("  Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(
        cfg["hf_id"],
        trust_remote_code=True,
        token=hf_token,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Load model in 4-bit
    print("  Loading model in 4-bit NF4...")
    model = AutoModelForCausalLM.from_pretrained(
        cfg["hf_id"],
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        token=hf_token,
        torch_dtype=torch.bfloat16,
    )
    
    # Register special trigger tokens for 0-token system prompt overhead
    special_tokens = [EINSOF_TRIGGER_TOKEN, MATHESIS_TRIGGER_TOKEN]
    new_tokens = [t for t in special_tokens if t not in tokenizer.get_vocab()]
    if new_tokens:
        tokenizer.add_special_tokens({"additional_special_tokens": new_tokens})
        model.resize_token_embeddings(len(tokenizer))
        print(f"  [+] Registered zero-overhead trigger tokens: {new_tokens}")
    model = prepare_model_for_kbit_training(model)

    # LoRA config
    lora_config = LoraConfig(
        r=cfg["lora_r"],
        lora_alpha=cfg["lora_alpha"],
        target_modules=cfg["target_modules"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)

    trainable, total = model.get_nb_trainable_parameters()
    print(f"  Trainable: {trainable:,} / {total:,} ({100*trainable/total:.2f}%)")

    # Format dataset
    if dataset_records:
        train_dataset = format_for_sft(dataset_records, tokenizer)
        print(f"  Training samples: {len(train_dataset)}")
    else:
        print("  ERROR: No dataset available. Aborting training.")
        return {"status": "NO_DATASET", "model": model_key}

    # Output directory
    output_dir = f"/tmp/polydim_sft_{model_key}"
    os.makedirs(output_dir, exist_ok=True)

    # Training arguments (conservative for free GPU quota)
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=3,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=16,
        learning_rate=2e-4,
        lr_scheduler_type="cosine",
        warmup_ratio=0.05,
        fp16=False,
        bf16=True,
        logging_steps=10,
        save_strategy="epoch",
        save_total_limit=2,
        report_to="none",
        max_grad_norm=0.3,
        optim="paged_adamw_8bit",
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
    )

    # SFT Trainer
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        tokenizer=tokenizer,
        max_seq_length=2048,
    )

    # Train
    print("  Starting SFT training...")
    train_result = trainer.train()
    train_time = time.time() - t0

    # Save adapter
    adapter_dir = f"/tmp/polydim_adapter_{model_key}"
    trainer.save_model(adapter_dir)
    tokenizer.save_pretrained(adapter_dir)

    # Stiefel retraction on LoRA weights
    print("  Applying Stiefel QR retraction to LoRA adapter weights...")
    from safetensors.torch import load_file, save_file

    adapter_path = os.path.join(adapter_dir, "adapter_model.safetensors")
    if os.path.isfile(adapter_path):
        state_dict = load_file(adapter_path)
        retracted = {}
        max_defect = 0.0
        retraction_count = 0

        for key, tensor in state_dict.items():
            if "lora_A" in key or "lora_B" in key:
                if tensor.ndim == 2 and min(tensor.shape) >= 2:
                    W_retracted = stiefel_qr_retract(tensor).to(tensor.dtype)
                    defect = neumaier_norm_check(W_retracted)
                    max_defect = max(max_defect, defect)
                    retracted[key] = W_retracted
                    retraction_count += 1
                else:
                    retracted[key] = tensor
            else:
                retracted[key] = tensor

        save_file(retracted, adapter_path)
        print(f"  Retracted {retraction_count} LoRA matrices. Max Stiefel defect: {max_defect:.2e}")
    else:
        max_defect = -1.0
        print(f"  WARNING: adapter_model.safetensors not found at {adapter_path}")

    # Upload to Hugging Face
    hf_repo = f"Polydim-Einsof/{model_key}-pmtp-sft"
    print(f"  Uploading to HuggingFace: {hf_repo}")
    from huggingface_hub import HfApi
    api = HfApi(token=hf_token)
    try:
        api.create_repo(hf_repo, exist_ok=True, private=False)
        api.upload_folder(
            folder_path=adapter_dir,
            repo_id=hf_repo,
            commit_message=f"POLYDIM SFT adapter: {model_key} | 1740 theorems | Stiefel QR retraction | max_defect={max_defect:.2e}",
        )
        upload_status = "UPLOADED"
    except Exception as e:
        upload_status = f"UPLOAD_FAILED: {e}"
        print(f"  Upload error: {e}")

    result = {
        "status": "TRAINED",
        "model": model_key,
        "hf_id": cfg["hf_id"],
        "hf_repo_sft": hf_repo,
        "trainable_params": trainable,
        "total_params": total,
        "train_loss": train_result.training_loss,
        "train_time_s": round(train_time, 1),
        "epochs": 3,
        "lora_r": cfg["lora_r"],
        "stiefel_max_defect": max_defect,
        "upload_status": upload_status,
        "license": cfg["license"],
    }
    print(f"  RESULT: {json.dumps(result, indent=2)}")

    # Free memory
    del model, trainer, train_dataset
    gc.collect()
    torch.cuda.empty_cache()

    return result

# ── Main ──────────────────────────────────────────────────────────────
def main():
    print("=" * 70)
    print("  POLYDIM-EINSOF: QLoRA SFT on Stiefel Manifolds")
    print("  Author: Ariel García Traba (Independent Research / EinsofOS)")
    print("  Dataset: 1,740 formal theorems (polydim_vec_db)")
    print("=" * 70)

    # Check GPU
    ngpu, total_vram = check_gpu()

    # Install deps
    print("\nInstalling dependencies...")
    install_deps()

    # HF token

    hf_token = os.environ.get("HF_TOKEN", "")

    if not hf_token:
        # Try reading from file (Kaggle secrets or local)
        for p in ["/kaggle/secrets/hf_token", "/content/hf_token.txt",
                  os.path.expanduser("~/.huggingface/token")]:
            if os.path.isfile(p):
                hf_token = open(p).read().strip()
                break
    if not hf_token:
        print("WARNING: No HF_TOKEN found. Uploads will fail.")
        print("  Set HF_TOKEN env var or place token in ~/.huggingface/token")

    # Load dataset
    print("\nLoading theorem dataset...")
    dataset_records = load_theorem_dataset()

    # Determine which models fit in available VRAM
    # Sort by min_vram ascending (train smallest first to maximize throughput)
    sorted_models = sorted(MODELS.items(), key=lambda x: x[1]["min_vram_gb"])

    results = []
    for model_key, cfg in sorted_models:
        try:
            result = train_model(model_key, cfg, ngpu, total_vram,
                                 dataset_records, hf_token)
            results.append(result)
        except Exception as e:
            print(f"  ERROR training {model_key}: {e}")
            import traceback
            traceback.print_exc()
            results.append({"status": "ERROR", "model": model_key, "error": str(e)})

    # Summary
    print("\n" + "=" * 70)
    print("  FINAL SUMMARY")
    print("=" * 70)
    for r in results:
        status = r.get("status", "UNKNOWN")
        model = r.get("model", "?")
        if status == "TRAINED":
            print(f"  ✓ {model}: loss={r['train_loss']:.4f}, "
                  f"time={r['train_time_s']}s, "
                  f"defect={r['stiefel_max_defect']:.2e}, "
                  f"upload={r['upload_status']}")
        else:
            print(f"  ✗ {model}: {status}")

    # Save results
    results_path = "/tmp/polydim_sft_results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {results_path}")

    return 0 if all(r.get("status") == "TRAINED" for r in results) else 1

if __name__ == "__main__":
    sys.exit(main())
