"""Live-verified 2026-2027 model catalog and feasibility matrix for QLoRA."""

from .model_catalog import (
    REAL_TRAINED_ADAPTERS_ON_DISK,
    VERIFIED_OPEN_QLORA_MODELS,
    CLOSED_COMMERCIAL_SATELLITES,
    ALADIN_OLLAMA_2026_TARGETS,
    POLYDIM_HF_32_REPOS,
    get_all_catalog_entries,
)

__all__ = [
    "REAL_TRAINED_ADAPTERS_ON_DISK",
    "VERIFIED_OPEN_QLORA_MODELS",
    "CLOSED_COMMERCIAL_SATELLITES",
    "ALADIN_OLLAMA_2026_TARGETS",
    "POLYDIM_HF_32_REPOS",
    "get_all_catalog_entries",
]
