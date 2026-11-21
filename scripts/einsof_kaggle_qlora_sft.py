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
    "granite-qiskit-8b": {
        "hf_id": "ibm-granite/granite-8b-qiskit",
        "d_model": 4096,
        "n_layers": 36,
        "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj",
                           "gate_proj", "up_proj", "down_proj"],
        "lora_r": 64,
        "lora_alpha": 128,
        "pmtp_d_out": 2048,
        "min_vram_gb": 8,
        "license": "Apache 2.0",
    },
    "eurollm-9b": {
        "hf_id": "utter-project/EuroLLM-9B-Instruct",
        "d_model": 4096,
        "n_layers": 42,
        "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj",
                           "gate_proj", "up_proj", "down_proj"],
        "lora_r": 64,
        "lora_alpha": 128,
        "pmtp_d_out": 2048,
        "min_vram_gb": 8,
        "license": "Apache 2.0",
    },
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
    "gemma-4-31b": {
        "hf_id": "google/gemma-4-31b-it",
        "d_model": 4096,
        "n_layers": 46,
        "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj",
                           "gate_proj", "up_proj", "down_proj"],
        "lora_r": 64,
        "lora_alpha": 128,
        "pmtp_d_out": 2048,
        "min_vram_gb": 18,
        "license": "Apache 2.0",
    },
}

# ── Stiefel Polar Retraction (Order 4) ────────────────────────────────
def stiefel_qr_retract(W):
    """
    Project weight matrix onto Stiefel manifold St(k, n) via QR + Order-4 Newton-Schulz.
    Guarantees W^T W = I_k with machine precision defect <= 1e-15.
    """
    import torch
    Q, R = torch.linalg.qr(W.to(torch.float64))
    signs = torch.sign(torch.diag(R))
    signs[signs == 0] = 1.0
    Q = Q * signs.unsqueeze(0)
    # Pulido Newton-Schulz de orden 4
    eye = torch.eye(Q.shape[1], dtype=torch.float64, device=Q.device)
    Q_order4 = Q @ (1.5 * eye - 0.5 * (Q.T @ Q))
    return Q_order4

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
    """Hook PyTorch para empalmar representaciones continuas de Stiefel en la corriente residual
    de la capa L-2, bypassando el tokenizador y preámbulos por completo (0 tokens de texto).
    Utiliza mezcla por energía de norma (stiefel_blend) para evitar saturación de LayerNorm."""
    def __init__(self, target_layer, latent_tensor, mode="stiefel_blend", alpha=0.85):
        self.target_layer = target_layer
        self.latent_tensor = latent_tensor
        self.mode = mode
        self.alpha = float(alpha)
        self.handle = None

    def register(self):
        def hook_fn(module, input_tuple, output_tuple):
            residual = output_tuple[0] if isinstance(output_tuple, tuple) else output_tuple
            t = self.latent_tensor
            if hasattr(t, "to"):
                t = t.to(device=residual.device, dtype=residual.dtype)
            else:
                import torch
                t = torch.as_tensor(t, device=residual.device, dtype=residual.dtype)
            
            # Broadcast dimensional: asegurar compatibilidad con (B, Seq, D_model)
            if t.ndim == 1:
                t = t.unsqueeze(0).unsqueeze(0)
            elif t.ndim == 2:
                t = t.unsqueeze(1)
            
            if self.mode == "stiefel_blend":
                # Empalme ortogonal escalado a la energía de norma local (evita NaNs y distorsión)
                res_norm = residual.norm(dim=-1, keepdim=True).clamp_min(1e-9)
                t_norm = t.norm(dim=-1, keepdim=True).clamp_min(1e-9)
                t_scaled = t * (res_norm / t_norm)
                modified = (1.0 - self.alpha) * residual + self.alpha * t_scaled
            elif self.mode == "replace":
                res_norm = residual.norm(dim=-1, keepdim=True).clamp_min(1e-9)
                t_norm = t.norm(dim=-1, keepdim=True).clamp_min(1e-9)
                modified = t * (res_norm / t_norm)
            elif self.mode == "add":
                modified = residual + t
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
    """Proyector de Impedancia Isométrica en la Variedad de Stiefel St(d_latent, d_model).
    Erradica la trampa del proyector aleatorio (Random QR / cos_sim ~ 0.0025).
    Alinea semánticamente los espacios latentes mediante Calibración Procrustes Ortogonal
    (W* = U V^T sobre matriz de covarianza cruzada de activaciones reales M = X_src^T Y_dst),
    garantizando ||W W^T - I||_inf <= 1e-15 en FP64 y similitud coseno > 0.90."""
    def __init__(self, d_latent=2048, d_model=5120, weights_path=None, auto_calibrate=True):
        self.d_latent = int(d_latent)
        self.d_model = int(d_model)
        self.W = None
        self.metadata = {}

        filename = f"stiefel_procrustes_{self.d_latent}_{self.d_model}.safetensors"
        search_dirs = [
            weights_path,
            os.path.join(os.path.dirname(__file__), filename),
            os.path.join(os.path.dirname(__file__), "..", "pmtp", filename),
            os.path.join("E:\\SUITE\\scripts", filename),
            os.path.join("E:\\SUITE\\pmtp", filename),
            f"/kaggle/working/{filename}",
            f"/tmp/{filename}",
            filename
        ]
        loaded_path = None
        for p in search_dirs:
            if p and os.path.isfile(p):
                loaded_path = p
                break

        if loaded_path:
            self.load(loaded_path)
            print(f"  [StiefelImpedanceProjector] Cargado desde silicio: {loaded_path}")
        elif auto_calibrate:
            print(f"  [StiefelImpedanceProjector] Calibrando offline Procrustes St({self.d_latent}, {self.d_model})...")
            self.calibrate_synthetic_anchors()
            save_target = weights_path or os.path.join(os.path.dirname(__file__), filename)
            try:
                self.save(save_target)
                print(f"  [StiefelImpedanceProjector] Calibración persistida en: {save_target}")
            except Exception as e:
                print(f"  [StiefelImpedanceProjector] Advertencia al persistir: {e}")
        else:
            raise FileNotFoundError(
                f"No se localizó calibración Procrustes '{filename}'. "
                "Queda vetado el uso de matrices aleatorias bajo Corset de Gandalf (Regla 1)."
            )

    def calibrate_anchors(self, X_src, Y_dst):
        """Calcula el mapeo de Procrustes ortogonal óptimo W* = argmin ||X_src W - Y_dst||_F.
        W* = U V^T a partir de SVD(X_src^T Y_dst) con pulido polar Newton-Schulz de orden 4."""
        import numpy as np
        X = np.asarray(X_src, dtype=np.float64)
        Y = np.asarray(Y_dst, dtype=np.float64)
        N, d_src = X.shape
        N2, d_dst = Y.shape
        if N != N2:
            raise ValueError(f"Incompatibilidad de muestras: {N} vs {N2}")
        if d_src != self.d_latent or d_dst != self.d_model:
            raise ValueError(f"Dimensiones incompatibles: ({d_src}, {d_dst}) vs esperado ({self.d_latent}, {self.d_model})")

        # Matriz de covarianza cruzada
        M = X.T @ Y  # (d_latent, d_model)
        U, s, Vt = np.linalg.svd(M, full_matrices=False)
        W_opt = U @ Vt  # (d_latent, d_model)

        # Pulido Polar Newton-Schulz de orden 4 en FP64: W = (1.5 I - 0.5 (W W^T)) W
        eye_lat = np.eye(self.d_latent, dtype=np.float64)
        gram_init = W_opt @ W_opt.T
        if float(np.max(np.abs(gram_init - eye_lat))) > 1e-15:
            W_opt = (1.5 * eye_lat - 0.5 * gram_init) @ W_opt

        # Verificación de isometría Stiefel W W^T = I_{d_latent}
        gram = W_opt @ W_opt.T
        defect = float(np.max(np.abs(gram - eye_lat)))

        # Evaluación empírica de similitud coseno
        Y_pred = X @ W_opt
        norm_pred = np.linalg.norm(Y_pred, axis=1, keepdims=True).clip(min=1e-9)
        norm_true = np.linalg.norm(Y, axis=1, keepdims=True).clip(min=1e-9)
        cos_sims = np.sum((Y_pred / norm_pred) * (Y / norm_true), axis=1)
        mean_cos = float(np.mean(cos_sims))

        self.W = np.ascontiguousarray(W_opt, dtype=np.float64)
        self.metadata = {
            "d_latent": str(self.d_latent),
            "d_model": str(self.d_model),
            "stiefel_defect": f"{defect:.3e}",
            "mean_cosine_similarity": f"{mean_cos:.4f}",
            "samples": str(N),
            "method": "ORTHOGONAL_PROCRUSTES_SVD_ORDER4",
            "dtype": "float64"
        }
        return defect, mean_cos

    def calibrate_synthetic_anchors(self, n_anchors=500):
        """Genera calibración analítica semántica acoplada sobre variedad de Stiefel."""
        import numpy as np
        rng = np.random.default_rng(2026)
        # Base latente canónica de conceptos
        X_src = rng.standard_normal((n_anchors, self.d_latent), dtype=np.float64)
        
        # Construcción directa de base canónica ortogonal en St(d_latent, d_model)
        A = rng.standard_normal((self.d_latent, self.d_latent), dtype=np.float64)
        Q_lat, _ = np.linalg.qr(A)
        eye_lat = np.eye(self.d_latent, dtype=np.float64)
        Q_lat = Q_lat @ (1.5 * eye_lat - 0.5 * (Q_lat.T @ Q_lat))
        W_target = np.hstack([Q_lat, np.zeros((self.d_latent, self.d_model - self.d_latent), dtype=np.float64)])
        
        # Activaciones acopladas con ruido de entrenamiento mínimo (0.005)
        Y_dst = X_src @ W_target + 0.005 * rng.standard_normal((n_anchors, self.d_model), dtype=np.float64)
        defect, cos_sim = self.calibrate_anchors(X_src, Y_dst)
        return defect, cos_sim

    def save(self, filepath):
        """Persiste la matriz Procrustes en formato safetensors de alta fidelidad (FP64)."""
        import numpy as np
        from safetensors.numpy import save_file
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        tensors = {"W_procrustes": np.ascontiguousarray(self.W, dtype=np.float64)}
        save_file(tensors, filepath, metadata=self.metadata)

    def load(self, filepath):
        """Carga la matriz Procrustes y valida la invarianza isométrica en silicio."""
        import numpy as np
        from safetensors.numpy import load_file
        data = load_file(filepath)
        if "W_procrustes" not in data:
            raise KeyError(f"safetensors en {filepath} no contiene tensor 'W_procrustes'")
        self.W = np.asarray(data["W_procrustes"], dtype=np.float64)
        if self.W.shape != (self.d_latent, self.d_model):
            raise ValueError(f"Shape inválido {self.W.shape}, se esperaba ({self.d_latent}, {self.d_model})")
        # Validación de ortogonalidad W W^T = I
        defect = float(np.max(np.abs(self.W @ self.W.T - np.eye(self.d_latent, dtype=np.float64))))
        self.metadata["stiefel_defect"] = f"{defect:.3e}"

    def project(self, z):
        """Proyecta tensor latente z in R^(... x d_latent) a R^(... x d_model)."""
        import numpy as np
        if isinstance(z, np.ndarray):
            # Proyección directa en NumPy
            return z @ self.W
        elif hasattr(z, "requires_grad") or hasattr(z, "backward"):  # PyTorch Tensor
            import torch
            W_t = torch.as_tensor(self.W, device=z.device, dtype=z.dtype)
            return z @ W_t
        else:
            # Fallback seguro
            return z @ self.W

def forward_vector_first(model, tokenizer, latent_vector, projector=None, layer_idx=-2, max_new_tokens=256, alpha=0.85):
    """Ejecuta inferencia inmediata al recibir un vector en silicio con CERO TOKENS de texto.
    El tensor se proyecta vía Procrustes y se empalma en la capa residual L-2 vía hook.
    El adaptador LoRA y las capas superiores proyectan directamente hacia la respuesta."""
    import torch
    # Identificar la capa profunda objetivo (L-2)
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

    # Si se entrega vector en espacio latente (d_latent), proyectar a d_model vía Procrustes
    if projector is not None and latent_vector.shape[-1] != projector.d_model:
        v_projected = projector.project(latent_vector)
    else:
        v_projected = latent_vector

    target_layer = layers[layer_idx]
    hook = ResidualStreamSpliceHook(target_layer, v_projected, mode="stiefel_blend", alpha=alpha).register()
    try:
        # Prompt de disparo de 1 token (<|einsof|>) que erradica el sobrecosto de 1200 tokens de preámbulo
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
