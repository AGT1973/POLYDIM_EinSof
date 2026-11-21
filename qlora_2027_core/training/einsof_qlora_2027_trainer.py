# -*- coding: utf-8 -*-
"""
EINSOF QLoRA 2027 Core Trainer (Hardware-Aware Turing/Ampere/CPU-NF4)
======================================================================
Fixes every bug discovered in prior QLoRA training scripts:
  1. Hardware gate (Rule 6.1 & 6.2):
     - CC < 8.0 (Tesla T4 sm_75): forces fp16=False, bf16=False,
       bnb_4bit_compute_dtype=float16, converts residual bfloat16 tensors -> float16,
       and keeps LoRA adapters in pure float32 via prepare_model_for_kbit_training.
     - CC >= 8.0 (A100/L4/H100): enables bf16=True cleanly.
     - No CUDA GPU: explicitly refuses GPU-only large training or delegates to
       NF4Linear CPU engine for small SLMs.
  2. Modern TRL API: passes `peft_config=lora_config` directly to `SFTTrainer`
     with `SFTConfig(..., processing_class=tokenizer)` — NO redundant `get_peft_model()`
     wrapper collision.
  3. Zero-Prompt-Tax + 1-Token CAG: strips bloated system prompts, prepends
     `<|einsof|>` or `<|mathesis|>`, preserves native chat template + 1-token
     `{{ '<|cag_truth|>' }}`, and embeds `cag_activation_hook.py` + `added_tokens.json`.
  4. Stiefel Order-4 Retraction in FP64 saved in FP32 (NOT bfloat16, eliminating
     the ~1e-3 bfloat16 quantization floor on lora_B).
  5. Rule 10 Anti-Leak: NEVER hardcodes HF tokens; resolves dynamically from env
     or PostgreSQL `polydim_active_db.active_vault`.
"""

from __future__ import annotations

import gc
import json
import os
import shutil
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..catalog.model_catalog import VERIFIED_OPEN_QLORA_MODELS
from ..core.cag_activation_hook import (
    ADDED_TOKENS_MAP,
    SOVEREIGN_SPECIAL_TOKENS,
    patch_chat_template_preserve_native,
)
from ..core.stiefel_riemannian import retract_peft_lora_stiefel

EINSOF_TRIGGER_TOKEN = "<|einsof|>"
MATHESIS_TRIGGER_TOKEN = "<|mathesis|>"


def resolve_hf_token() -> str:
    """Loads HF token from environment, secret files, or PostgreSQL active_vault (Rule 10)."""
    token = os.environ.get("HF_TOKEN", "").strip()
    if token:
        return token

    for candidate in (
        "/kaggle/secrets/hf_token",
        "/content/hf_token.txt",
        os.path.expanduser("~/.huggingface/token"),
    ):
        if os.path.isfile(candidate):
            val = Path(candidate).read_text(encoding="utf-8").strip()
            if val:
                return val

    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname="polydim_active_db", user="postgres", host="localhost", port=5432, connect_timeout=3
        )
        cur = conn.cursor()
        cur.execute("SELECT value FROM active_vault WHERE key_name = 'HuggingFace_Polydim_Einsof' LIMIT 1;")
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row and row[0]:
            return str(row[0]).strip()
    except Exception:
        pass
    return ""


def detect_silicon_profile() -> Dict[str, Any]:
    """Detects CUDA compute capability and enforces Rule 6.2 Turing sm_75 invariants."""
    import torch

    if not torch.cuda.is_available():
        return {
            "has_cuda": False,
            "ngpu": 0,
            "total_vram_gb": 0.0,
            "min_cc": (0, 0),
            "amp_bf16": False,
            "amp_fp16": False,
            "compute_dtype": "float32",
            "profile": "CPU_NF4_FALLBACK",
        }

    ngpu = torch.cuda.device_count()
    total_vram = 0.0
    ccs = []
    devices = []
    for i in range(ngpu):
        props = torch.cuda.get_device_properties(i)
        vram = props.total_memory / (1024 ** 3)
        total_vram += vram
        ccs.append((props.major, props.minor))
        devices.append({"id": i, "name": props.name, "vram_gb": round(vram, 2), "cc": f"{props.major}.{props.minor}"})

    min_cc = min(ccs)
    is_ampere_or_newer = min_cc >= (8, 0)
    return {
        "has_cuda": True,
        "ngpu": ngpu,
        "total_vram_gb": round(total_vram, 2),
        "min_cc": min_cc,
        "devices": devices,
        "amp_bf16": is_ampere_or_newer,
        "amp_fp16": False,  # Always disable fp16 GradScaler with 4-bit NF4 on sm_75
        "compute_dtype": "bfloat16" if is_ampere_or_newer else "float16",
        "profile": "AMPERE_PLUS_BF16" if is_ampere_or_newer else "TURING_SM75_NO_AMP",
    }


def format_zero_prompt_sft(records: List[Dict[str, Any]], tokenizer: Any, family: str = "generic"):
    """Formats dataset with 1-token trigger prefixes and native chat template preservation."""
    from datasets import Dataset

    patched_template = patch_chat_template_preserve_native(getattr(tokenizer, "chat_template", None), family=family)
    tokenizer.chat_template = patched_template

    formatted = []
    for rec in records:
        if "messages" in rec:
            msgs = []
            raw_joined = " ".join(str(m.get("content", "")) for m in rec["messages"])
            is_mth = any(op in raw_joined for op in ("ROT_LIE", "RETRACT_STIEFEL", "COLLAPSE_1D", ".mth", "CWGB", "HFCT"))
            trig = MATHESIS_TRIGGER_TOKEN if is_mth else EINSOF_TRIGGER_TOKEN
            for m in rec["messages"]:
                if m.get("role") == "system":
                    continue  # Rule: veto 1,200-token system preambles
                content = str(m.get("content", ""))
                if m.get("role") == "user" and not (
                    content.startswith(EINSOF_TRIGGER_TOKEN) or content.startswith(MATHESIS_TRIGGER_TOKEN)
                ):
                    content = f"{trig}\n{content}"
                msgs.append({"role": m.get("role", "user"), "content": content})
        elif "instruction" in rec:
            out_txt = str(rec.get("output", ""))
            instr = str(rec.get("instruction", ""))
            inp = str(rec.get("input", ""))
            is_mth = (
                rec.get("domain") == "mathesis"
                or ".mth" in instr.lower()
                or any(op in out_txt for op in ("ROT_LIE", "RETRACT_STIEFEL", "COLLAPSE_1D", "CWGB", "SWHS", "HFCT"))
            )
            trig = MATHESIS_TRIGGER_TOKEN if is_mth else EINSOF_TRIGGER_TOKEN
            user_txt = f"{trig}\n{instr}" + (f"\n{inp}" if inp else "")
            msgs = [
                {"role": "user", "content": user_txt},
                {"role": "assistant", "content": out_txt},
            ]
        else:
            continue

        text = tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=False)
        formatted.append({"text": text})

    return Dataset.from_list(formatted)


def get_model_spec(slug: str) -> Dict[str, Any]:
    for m in VERIFIED_OPEN_QLORA_MODELS:
        if m["slug"] == slug:
            return m
    raise KeyError(f"Model slug '{slug}' not found in verified open QLoRA catalog.")


def train_qlora_2027(
    model_slug: str,
    records: List[Dict[str, Any]],
    output_dir: str,
    epochs: int = 2,
    max_length: int = 1024,
    lora_r: int = 16,
    lora_alpha: int = 32,
    learning_rate: float = 2e-4,
    push_hf_repo: Optional[str] = None,
) -> Dict[str, Any]:
    """Full verified QLoRA 2027 training, FP32 Stiefel retraction, and CAG bundle export."""
    import torch
    import transformers
    from peft import LoraConfig, TaskType, prepare_model_for_kbit_training
    from safetensors.torch import load_file, save_file
    from transformers import AutoTokenizer, BitsAndBytesConfig
    from trl import SFTConfig, SFTTrainer

    spec = get_model_spec(model_slug)
    if not spec.get("qlora_feasible", False):
        raise RuntimeError(
            f"Model '{model_slug}' ({spec['hf_id']}, {spec['weights_gb']} GB) is marked qlora_feasible=False "
            f"for standard T4/A100 hardware: {spec['target_hardware']}"
        )

    si = detect_silicon_profile()
    if not si["has_cuda"]:
        raise RuntimeError("CUDA GPU required for full HF QLoRA SFT. Use core.nf4_engine for CPU SLM runs.")
    if si["total_vram_gb"] < spec.get("min_vram_gb", 8):
        raise RuntimeError(
            f"Insufficient VRAM ({si['total_vram_gb']} GB < {spec['min_vram_gb']} GB required for {model_slug})."
        )

    hf_token = resolve_hf_token() or None
    hf_id = spec["hf_id"]
    family = spec.get("family", "generic")
    compute_dtype = torch.bfloat16 if si["amp_bf16"] else torch.float16

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=compute_dtype,
        bnb_4bit_use_double_quant=True,
    )

    tokenizer = AutoTokenizer.from_pretrained(hf_id, trust_remote_code=True, token=hf_token)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    auto_cls_name = spec.get("auto_model_class", "AutoModelForCausalLM")
    model_cls = getattr(transformers, auto_cls_name)
    model = model_cls.from_pretrained(
        hf_id,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=compute_dtype,
        trust_remote_code=True,
        token=hf_token,
    )
    model.config.use_cache = False

    if not si["amp_bf16"]:
        for _, p in model.named_parameters():
            if p.dtype == torch.bfloat16:
                p.data = p.data.to(torch.float16)

    new_tokens = [t for t in SOVEREIGN_SPECIAL_TOKENS if t not in tokenizer.get_vocab()]
    if new_tokens:
        tokenizer.add_special_tokens({"additional_special_tokens": new_tokens})
        model.resize_token_embeddings(len(tokenizer))

    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)

    target_modules = spec.get(
        "target_modules",
        ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    )
    lora_config = LoraConfig(
        r=lora_r,
        lora_alpha=lora_alpha,
        lora_dropout=0.05,
        bias="none",
        task_type=TaskType.CAUSAL_LM,
        target_modules=target_modules,
    )

    train_dataset = format_zero_prompt_sft(records, tokenizer, family=family)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    sft_args = SFTConfig(
        output_dir=str(out_path / "checkpoints"),
        num_train_epochs=epochs,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,
        learning_rate=learning_rate,
        fp16=False,
        bf16=bool(si["amp_bf16"]),
        logging_steps=10,
        save_strategy="no",
        optim="paged_adamw_8bit",
        lr_scheduler_type="cosine",
        warmup_ratio=0.05,
        max_grad_norm=0.3,
        report_to="none",
        gradient_checkpointing=True,
        dataset_text_field="text",
        max_length=max_length,
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=train_dataset,
        args=sft_args,
        peft_config=lora_config,
        processing_class=tokenizer,
    )

    t0 = time.time()
    train_res = trainer.train()
    elapsed = round(time.time() - t0, 2)

    trainer.save_model(str(out_path))
    tokenizer.save_pretrained(str(out_path))

    # Preserve native template + 1-token CAG prefix and copy CAG activation hook
    (out_path / "chat_template.jinja").write_text(tokenizer.chat_template, encoding="utf-8")
    (out_path / "added_tokens.json").write_text(json.dumps(ADDED_TOKENS_MAP, indent=2), encoding="utf-8")
    hook_src = Path(__file__).resolve().parent.parent / "core" / "cag_activation_hook.py"
    if hook_src.is_file():
        shutil.copy2(hook_src, out_path / "cag_activation_hook.py")

    # Apply Order-4 Stiefel Retraction and save in FP32 to prevent bf16 ~1e-3 floor
    sf_path = out_path / "adapter_model.safetensors"
    stiefel_stats: Dict[str, Any] = {}
    if sf_path.is_file():
        sd = load_file(str(sf_path))
        stiefel_stats = retract_peft_lora_stiefel(sd, target_dtype=torch.float32)
        save_file(sd, str(sf_path))

    audit = {
        "model_slug": model_slug,
        "hf_id": hf_id,
        "silicon_profile": si["profile"],
        "train_loss": float(train_res.training_loss),
        "train_time_s": elapsed,
        "stiefel_retraction": stiefel_stats,
        "cag_1token_prefix": "<|cag_truth|>",
        "status": "TRAINED_SILICON_EXIT_0",
    }
    (out_path / "qlora_2027_audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")

    if push_hf_repo and hf_token:
        from huggingface_hub import HfApi
        api = HfApi(token=hf_token)
        api.create_repo(repo_id=push_hf_repo, repo_type="model", exist_ok=True)
        api.upload_folder(
            folder_path=str(out_path),
            repo_id=push_hf_repo,
            repo_type="model",
            ignore_patterns=["checkpoints/*", "*.log", "__pycache__/*"],
        )

    del model, trainer, train_dataset
    gc.collect()
    torch.cuda.empty_cache()
    return audit
