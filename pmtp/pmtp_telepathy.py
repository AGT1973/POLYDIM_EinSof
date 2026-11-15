# ============================================================================
# PMTP TELEPATHY COMPATIBILITY SHIM -> pmtp_aladin
# ============================================================================
from .pmtp_aladin import (
    ALADIN_MAGIC,
    ALADIN_VERSION,
    GHOST_FORBIDDEN_KEYS,
    AladinTelepathyClient,
    _blake2s_mac,
    _decode_message,
    _encode_message,
)

__all__ = [
    "ALADIN_MAGIC",
    "ALADIN_VERSION",
    "GHOST_FORBIDDEN_KEYS",
    "AladinTelepathyClient",
    "_blake2s_mac",
    "_decode_message",
    "_encode_message",
]
