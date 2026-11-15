# ============================================================================
# PMTP FAIL-CLOSED SERIALIZATION & WEIGHT LOADING POLICY
# Proyecto: PMTP / POLYDIM-EINSOF
# Requisito SOTA: Prohibición estricta de deserialización pickle (.bin/.pt/.pth)
# ============================================================================

import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
import numpy as np

SAFE_WEIGHT_EXTENSIONS = (".safetensors",)
BLOCKED_PICKLE_EXTENSIONS = (".bin", ".pt", ".pth", ".ckpt", ".pkl", ".pickle", ".marshal")


def assert_safe_checkpoint_path(path: Union[str, os.PathLike]) -> Path:
    """
    Valida en modo fail-closed que un checkpoint local utilice exclusivamente `.safetensors`.
    Rechaza formatos basados en pickle (.bin, .pt, .pth, .ckpt, .pkl, .pickle).
    """
    resolved = Path(path)
    suffix = resolved.suffix.lower()
    if suffix in BLOCKED_PICKLE_EXTENSIONS:
        raise PermissionError(
            f"Fail-closed security policy: blocked pickle-backed artifact '{resolved.name}'. "
            "Use '.safetensors' only."
        )
    if suffix not in SAFE_WEIGHT_EXTENSIONS:
        raise PermissionError(
            f"Fail-closed security policy: unsupported checkpoint extension '{suffix or '<none>'}' "
            f"for '{resolved.name}'. Allowed: {SAFE_WEIGHT_EXTENSIONS}."
        )
    return resolved


def build_safe_hf_load_kwargs(extra_kwargs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Construye argumentos fail-closed para `AutoModel*.from_pretrained(...)`,
    forzando `use_safetensors=True` y `trust_remote_code=False`.
    """
    cfg: Dict[str, Any] = dict(extra_kwargs or {})
    if cfg.get("use_safetensors") is False:
        raise PermissionError("Fail-closed policy violation: 'use_safetensors=False' is forbidden.")
    if cfg.get("trust_remote_code") is True:
        raise PermissionError("Fail-closed policy violation: 'trust_remote_code=True' is forbidden by default.")
    cfg["use_safetensors"] = True
    cfg["trust_remote_code"] = False
    return cfg


def load_numpy_safe(path: Union[str, os.PathLike]) -> Any:
    """Carga arreglos NumPy con `allow_pickle=False` estricto (inmune a object-array RCE)."""
    return np.load(path, allow_pickle=False)
