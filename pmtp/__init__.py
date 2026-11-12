"""
PMTP: Physical Manifold Transport Protocol & Inter-Process Latent Alignment
"""

from .pmtp_types import PmtpCompactHeader, HEADER_COMPACT_SIZE
from .pmtp_shm_bus import PmtpShmBus
from .pmtp_stiefel import PmtpStiefelAdapter
from .pmtp_procrustes import PmtpOrthogonalProcrustes
from .pmtp_decoder import PmtpHypothesisEncoder, PmtpHypothesisDecoder, PmtpCausalDAGReasoner

# Alias ergonómicos para desarrolladores
StiefelAdapter = PmtpStiefelAdapter
ProcrustesAligner = PmtpOrthogonalProcrustes
PmtpProcrustesAligner = PmtpOrthogonalProcrustes

__version__ = "1.0.0"
__all__ = [
    "PmtpCompactHeader",
    "HEADER_COMPACT_SIZE",
    "PmtpShmBus",
    "PmtpStiefelAdapter",
    "StiefelAdapter",
    "PmtpOrthogonalProcrustes",
    "ProcrustesAligner",
    "PmtpProcrustesAligner",
    "PmtpHypothesisEncoder",
    "PmtpHypothesisDecoder",
    "PmtpCausalDAGReasoner"
]
