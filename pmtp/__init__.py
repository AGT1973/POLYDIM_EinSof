"""
PMTP: Physical Manifold Transport Protocol & Inter-Process Latent Alignment
"""

from .pmtp_types import PmtpCompactHeader, HEADER_COMPACT_SIZE
from .pmtp_shm_bus import PmtpShmBus
from .pmtp_stiefel import PmtpStiefelAdapter
from .pmtp_procrustes import PmtpProcrustesAligner
from .pmtp_decoder import PmtpDecoder

__version__ = "1.0.0"
__all__ = [
    "PmtpCompactHeader",
    "HEADER_COMPACT_SIZE",
    "PmtpShmBus",
    "PmtpStiefelAdapter",
    "PmtpProcrustesAligner",
    "PmtpDecoder"
]
