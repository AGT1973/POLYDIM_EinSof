"""Hardware-aware QLoRA 2027 SFT training pipeline."""

from .einsof_qlora_2027_trainer import (
    detect_silicon_profile,
    resolve_hf_token,
    format_zero_prompt_sft,
    train_qlora_2027,
)

__all__ = [
    "detect_silicon_profile",
    "resolve_hf_token",
    "format_zero_prompt_sft",
    "train_qlora_2027",
]
