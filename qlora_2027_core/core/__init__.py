"""Core mathematical, quantization, splice, KV-cache, CAG, and Helena primitives."""

from .stiefel_riemannian import (
    neumaier_sum,
    neumaier_sum_sq,
    neumaier_norm,
    horner_polar_order4,
    project_stiefel_polar_order4,
    retract_peft_lora_stiefel,
    project_to_stiefel_tangent,
    riemannian_weight_decay_gradient,
    condition_number_stiefel,
    riemannian_armijo_step,
    stream_cache_sharded_dot,
)
from .procrustes_splice import (
    PmtpOrthogonalProcrustes,
    apply_rope_phase_compensator,
    StiefelImpedanceProjector,
    ResidualStreamSpliceHook,
    AttentionSummaryPooling,
    forward_vector_first,
)
from .kv_cache_bridge import PmtpSharedKVCacheBridge
from .nf4_engine import NF4Linear, quantize_peft_base_to_nf4
from .cag_activation_hook import (
    SOVEREIGN_SPECIAL_TOKENS,
    ADDED_TOKENS_MAP,
    BANNED_VERISIMILITUDE_PHRASES,
    CAGClosedWorldLogitsProcessor,
    patch_chat_template_preserve_native,
    attach_cag_on_activation,
)
from .helena_carrier_bridge import (
    encode_png_carrier,
    decode_png_carrier,
    encode_4bit_quant_carrier,
    encode_1bit_spinor_carrier,
    build_sandbox_verification_script,
)

__all__ = [
    "neumaier_sum",
    "neumaier_sum_sq",
    "neumaier_norm",
    "horner_polar_order4",
    "project_stiefel_polar_order4",
    "retract_peft_lora_stiefel",
    "project_to_stiefel_tangent",
    "riemannian_weight_decay_gradient",
    "condition_number_stiefel",
    "riemannian_armijo_step",
    "stream_cache_sharded_dot",
    "PmtpOrthogonalProcrustes",
    "apply_rope_phase_compensator",
    "StiefelImpedanceProjector",
    "ResidualStreamSpliceHook",
    "AttentionSummaryPooling",
    "forward_vector_first",
    "PmtpSharedKVCacheBridge",
    "NF4Linear",
    "quantize_peft_base_to_nf4",
    "SOVEREIGN_SPECIAL_TOKENS",
    "ADDED_TOKENS_MAP",
    "BANNED_VERISIMILITUDE_PHRASES",
    "CAGClosedWorldLogitsProcessor",
    "patch_chat_template_preserve_native",
    "attach_cag_on_activation",
    "encode_png_carrier",
    "decode_png_carrier",
    "encode_4bit_quant_carrier",
    "encode_1bit_spinor_carrier",
    "build_sandbox_verification_script",
]
