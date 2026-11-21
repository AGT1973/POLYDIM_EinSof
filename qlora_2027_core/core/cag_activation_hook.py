# -*- coding: utf-8 -*-
"""
CAG Closed-World Activation Hook & Native-Preserving 1-Token Template (2027 Core)
=================================================================================
Fixes two defects discovered on 2026-11-21:
  1. Preserves each base model's native chat template (GLM-4 [gMASK]<sop>, Gemma-4,
     DeepSeek, Moonlight <|im_user|>, Qwen <|im_start|>, Aion) while prepending the
     1-token `<|cag_truth|>` trigger (`98.9%` prompt tax reduction vs 95-token prose).
  2. Uses an audited ban list that blocks non-existent/closed placeholder claims
     (`Claude Opus 5.5`, `GPT-6 Astra/Terra`, `Gemini 4 Carbon/Hydrogen`,
     `Qwen 3.8 Max`, `Qwen 3.5 Max`, `GLM-5.3 Prime`) and paternalistic Regla 9/23
     phrases WITHOUT false-banning verified open-weight HF models (`Gemma 4`,
     `Qwen3.8-27B`, `DeepSeek-V4.1-Flash`, `Llama-4-Scout`).
  3. Masks unsealed execution claims (`Exit Code 0`, `CERTIFIED_IN_SILICON`) to
     `-inf` (P = 0.0) whenever `active_blake2s_seal` is None.
"""

from __future__ import annotations

import functools
import json
from typing import Any, Dict, List, Optional

import torch

try:
    from transformers import LogitsProcessor, LogitsProcessorList
    _HAS_TRANSFORMERS_LP = True
except ImportError:
    LogitsProcessor = object
    LogitsProcessorList = list
    _HAS_TRANSFORMERS_LP = False

SOVEREIGN_SPECIAL_TOKENS: List[str] = [
    "<|einsof|>",
    "<|mathesis|>",
    "<|cag_truth|>",
    "<|matrix_display|>",
    "<|haptic_taxel|>",
    "<|bci_stream|>",
]

ADDED_TOKENS_MAP: Dict[str, int] = {
    "<|einsof|>": 151665,
    "<|mathesis|>": 151666,
    "<|cag_truth|>": 151667,
    "<|matrix_display|>": 151668,
    "<|haptic_taxel|>": 151669,
    "<|bci_stream|>": 151670,
}

CAG_TRIGGER_JINJA = "{{ '<|cag_truth|>' }}"
CAG_CLOSED_WORLD_PREFIX = "<|cag_truth|>"

# Verified non-open / non-existent model claims and paternalistic Regla 9/23 triggers
BANNED_VERISIMILITUDE_PHRASES: List[str] = [
    "Claude Opus 5.5",
    "GPT-6 Astra",
    "GPT-6 Terra",
    "Gemini 4 Carbon",
    "Gemini 4 Hydrogen",
    "Qwen 3.8 Max",
    "Qwen 3.5 Max",
    "GLM-5.3 Prime",
    "deberías ir a dormir",
    "cuidar tu salud mental",
    "soy solo un predictor estadístico",
    "prohibido actuar como co-worker",
]

UNSEALED_SILICON_CLAIMS: Tuple[str, ...] = (
    "Exit Code 0",
    "CERTIFIED_IN_SILICON",
    "verificado en silicio",
)

# Native chat templates preserved per model family (fallback when tokenizer_config lacks one)
NATIVE_CHAT_TEMPLATES: Dict[str, str] = {
    "glm4": (
        "[gMASK]<sop>{% for message in messages %}"
        "<|{{ message['role'] }}|>\n{{ message['content'] }}"
        "{% endfor %}{% if add_generation_prompt %}<|assistant|>\n{% endif %}"
    ),
    "gemma4": (
        "{{ bos_token }}{% for message in messages %}"
        "{% if message['role'] == 'user' %}<start_of_turn>user\n{{ message['content'] }}<end_of_turn>\n"
        "{% elif message['role'] == 'assistant' %}<start_of_turn>model\n{{ message['content'] }}<end_of_turn>\n"
        "{% elif message['role'] == 'system' %}{{ message['content'] }}\n{% endif %}"
        "{% endfor %}{% if add_generation_prompt %}<start_of_turn>model\n{% endif %}"
    ),
    "moonlight": (
        "{% for message in messages %}"
        "{% if message['role'] == 'system' %}<|im_system|>system<|im_middle|>{{ message['content'] }}<|im_end|>"
        "{% elif message['role'] == 'user' %}<|im_user|>user<|im_middle|>{{ message['content'] }}<|im_end|>"
        "{% elif message['role'] == 'assistant' %}<|im_assistant|>assistant<|im_middle|>{{ message['content'] }}<|im_end|>"
        "{% endif %}{% endfor %}{% if add_generation_prompt %}<|im_assistant|>assistant<|im_middle|>{% endif %}"
    ),
    "deepseek_coder": (
        "{{ bos_token }}{% for message in messages %}"
        "{% if message['role'] == 'user' %}User: {{ message['content'] }}\n\n"
        "{% elif message['role'] == 'assistant' %}Assistant: {{ message['content'] }}{{ eos_token }}"
        "{% elif message['role'] == 'system' %}{{ message['content'] }}\n\n{% endif %}"
        "{% endfor %}{% if add_generation_prompt %}Assistant:{% endif %}"
    ),
    "deepseek_prover": (
        "{{ bos_token }}{% for message in messages %}"
        "{% if message['role'] == 'user' %}<｜User｜>{{ message['content'] }}"
        "{% elif message['role'] == 'assistant' %}<｜Assistant｜>{{ message['content'] }}<｜end▁of▁sentence｜>"
        "{% elif message['role'] == 'system' %}{{ message['content'] }}{% endif %}"
        "{% endfor %}{% if add_generation_prompt %}<｜Assistant｜>{% endif %}"
    ),
    "qwen": (
        "{% for message in messages %}"
        "<|im_start|>{{ message['role'] }}\n{{ message['content'] }}<|im_end|>\n"
        "{% endfor %}{% if add_generation_prompt %}<|im_start|>assistant\n{% endif %}"
    ),
    "llama": (
        "{{ bos_token }}{% for message in messages %}"
        "<|start_header_id|>{{ message['role'] }}<|end_header_id|>\n\n{{ message['content'] }}<|eot_id|>"
        "{% endfor %}{% if add_generation_prompt %}<|start_header_id|>assistant<|end_header_id|>\n\n{% endif %}"
    ),
    "mistral": (
        "{{ bos_token }}{% for message in messages %}"
        "{% if message['role'] == 'user' %}[INST] {{ message['content'] }} [/INST]"
        "{% elif message['role'] == 'assistant' %}{{ message['content'] }}{{ eos_token }}"
        "{% elif message['role'] == 'system' %}{{ message['content'] }}\n\n{% endif %}{% endfor %}"
    ),
    "granite": (
        "{% for message in messages %}"
        "<|start_of_role|>{{ message['role'] }}<|end_of_role|>{{ message['content'] }}<|end_of_text|>\n"
        "{% endfor %}{% if add_generation_prompt %}<|start_of_role|>assistant<|end_of_role|>{% endif %}"
    ),
    "generic": (
        "{% for message in messages %}<|{{ message['role'] }}|>\n{{ message['content'] }}\n"
        "{% endfor %}{% if add_generation_prompt %}<|assistant|>\n{% endif %}"
    ),
}


def patch_chat_template_preserve_native(
    existing_template: Optional[str] = None,
    family: str = "generic",
) -> str:
    """
    Prepends the 1-token `<|cag_truth|>` trigger without destroying native family
    chat tokens (such as GLM-4 `[gMASK]<sop>` or Gemma `<start_of_turn>`).
    """
    base = (existing_template or "").strip()
    is_broken_overwrite = base.startswith("{{ '<|cag_truth|>' }}{% for message in messages %}<|{{ message['role'] }}|>")
    if not base or (is_broken_overwrite and family in NATIVE_CHAT_TEMPLATES and family != "generic"):
        base = NATIVE_CHAT_TEMPLATES.get(family, NATIVE_CHAT_TEMPLATES["generic"])

    if "<|cag_truth|>" in base:
        return base
    return CAG_TRIGGER_JINJA + base


class CAGClosedWorldLogitsProcessor(LogitsProcessor):
    """
    Sets logits to -inf (P = 0.0) for banned verisimilitude sequences and unsealed
    silicon certification claims whenever `active_blake2s_seal` is missing.
    """

    def __init__(
        self,
        banned_token_sequences: List[List[int]],
        active_blake2s_seal: Optional[str] = None,
        unsealed_claim_sequences: Optional[List[List[int]]] = None,
    ):
        self.banned_sequences = [seq for seq in banned_token_sequences if len(seq) > 0]
        self.active_blake2s_seal = active_blake2s_seal
        self.unsealed_claim_sequences = [seq for seq in (unsealed_claim_sequences or []) if len(seq) > 0]

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor) -> torch.FloatTensor:
        active_bans = list(self.banned_sequences)
        if not self.active_blake2s_seal:
            active_bans.extend(self.unsealed_claim_sequences)

        batch_size, seq_len = input_ids.shape
        for b in range(batch_size):
            history = input_ids[b].tolist()
            for seq in active_bans:
                k = len(seq)
                if k == 1:
                    scores[b, seq[0]] = -float("inf")
                elif seq_len >= k - 1 and history[-(k - 1):] == seq[:-1]:
                    scores[b, seq[-1]] = -float("inf")
        return scores


def attach_cag_on_activation(
    model: Any,
    tokenizer: Any,
    active_blake2s_seal: Optional[str] = None,
    family: str = "generic",
):
    """Binds 1-token `<|cag_truth|>` template and `-inf` LogitsProcessor onto model.generate."""
    banned_seqs: List[List[int]] = []
    for phrase in BANNED_VERISIMILITUDE_PHRASES:
        for variant in (phrase, phrase.lower(), " " + phrase, " " + phrase.lower()):
            toks = tokenizer.encode(variant, add_special_tokens=False)
            if toks and toks not in banned_seqs:
                banned_seqs.append(toks)

    unsealed_seqs: List[List[int]] = []
    for claim in UNSEALED_SILICON_CLAIMS:
        for variant in (claim, " " + claim):
            toks = tokenizer.encode(variant, add_special_tokens=False)
            if toks and toks not in unsealed_seqs:
                unsealed_seqs.append(toks)

    processor = CAGClosedWorldLogitsProcessor(
        banned_token_sequences=banned_seqs,
        active_blake2s_seal=active_blake2s_seal,
        unsealed_claim_sequences=unsealed_seqs,
    )

    tokenizer.chat_template = patch_chat_template_preserve_native(
        getattr(tokenizer, "chat_template", None), family=family
    )

    orig_generate = model.generate

    @functools.wraps(orig_generate)
    def cag_locked_generate(*args, **kwargs):
        lp = kwargs.get("logits_processor", None)
        lp_list = LogitsProcessorList(list(lp)) if lp is not None else LogitsProcessorList()
        lp_list.append(processor)
        kwargs["logits_processor"] = lp_list
        kwargs["do_sample"] = False
        return orig_generate(*args, **kwargs)

    model.generate = cag_locked_generate
    model._cag_truth_gate_attached = True
    model._cag_processor = processor
    return model, tokenizer


def run_silicon_self_test(negative_control_mode: bool = False) -> int:
    """Self-test with Popperian Control X (`--control-x-fail` disables masking and asserts failure)."""
    processor = CAGClosedWorldLogitsProcessor(
        banned_token_sequences=[[101, 102, 103]],
        active_blake2s_seal=None,
        unsealed_claim_sequences=[[201, 202, 203]],
    )
    raw_logits = torch.ones((1, 500), dtype=torch.float32) * 5.0

    in_banned = torch.tensor([[50, 101, 102]], dtype=torch.long)
    guarded = raw_logits.clone() if negative_control_mode else processor(in_banned, raw_logits.clone())
    prob_banned = float(torch.softmax(guarded, dim=-1)[0, 103].item())
    assert prob_banned == 0.0, f"CAG_LEAK: banned token prob={prob_banned}"

    in_claim = torch.tensor([[50, 201, 202]], dtype=torch.long)
    guarded_claim = raw_logits.clone() if negative_control_mode else processor(in_claim, raw_logits.clone())
    prob_claim = float(torch.softmax(guarded_claim, dim=-1)[0, 203].item())
    assert prob_claim == 0.0, f"CAG_LEAK: unsealed claim prob={prob_claim}"

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(run_silicon_self_test("--control-x-fail" in sys.argv))
