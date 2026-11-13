"""
PMTP: Physical Manifold Transport Protocol & Inter-Process Latent Alignment
"""

from .pmtp_types import PmtpCompactHeader, HEADER_COMPACT_SIZE
from .pmtp_shm_bus import PmtpShmBus
from .pmtp_stiefel import PmtpStiefelAdapter
from .pmtp_procrustes import PmtpOrthogonalProcrustes
from .pmtp_decoder import PmtpHypothesisEncoder, PmtpHypothesisDecoder, PmtpCausalDAGReasoner
from .pmtp_channel import PmtpChannel
from .pmtp_security import (
    SAFE_WEIGHT_EXTENSIONS,
    assert_safe_checkpoint_path,
    build_safe_hf_load_kwargs,
    load_numpy_safe,
)
from .pmtp_aladin import AladinTelepathyClient

# Alias ergonómicos para desarrolladores
StiefelAdapter = PmtpStiefelAdapter
ProcrustesAligner = PmtpOrthogonalProcrustes
PmtpProcrustesAligner = PmtpOrthogonalProcrustes

__version__ = "1.0.0"
__all__ = [
    "PmtpCompactHeader",
    "HEADER_COMPACT_SIZE",
    "PmtpShmBus",
    "PmtpChannel",
    "PmtpStiefelAdapter",
    "StiefelAdapter",
    "PmtpOrthogonalProcrustes",
    "ProcrustesAligner",
    "PmtpProcrustesAligner",
    "PmtpHypothesisEncoder",
    "PmtpHypothesisDecoder",
    "PmtpCausalDAGReasoner",
    "SAFE_WEIGHT_EXTENSIONS",
    "assert_safe_checkpoint_path",
    "build_safe_hf_load_kwargs",
    "load_numpy_safe",
    "AladinTelepathyClient",
]
