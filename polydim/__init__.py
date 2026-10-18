"""
POLYDIM & MPELEIDES STANDARD COGNITIVE FABRIC
Package entrypoint exposing geometry, recurrent flow, dual memory, transport, and adapters.
"""

from .core.manifold import StiefelManifold
from .core.symplectic_flow import SymplecticVerletFlow, TopologicalSnapStabilizer
from .core.memory_hippo import ModernHopfieldCAM, HippoCayleyContinuousMemory
from .transport.helena_carrier import HelenaCarrier
from .transport.pmtp_shm import PmtpShmBus
from .adapters.base_adapter import BaseLatentAdapter
from .adapters.qwen_adapter import QwenLatentAdapter

__version__ = "1.0.0-sota-20261012"
__all__ = [
    "StiefelManifold",
    "SymplecticVerletFlow",
    "TopologicalSnapStabilizer",
    "ModernHopfieldCAM",
    "HippoCayleyContinuousMemory",
    "HelenaCarrier",
    "PmtpShmBus",
    "BaseLatentAdapter",
    "QwenLatentAdapter",
]
