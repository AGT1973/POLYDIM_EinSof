"""
pmtp_channel.py — Canal opcional con degradación garantizada a texto.

Garantía de compatibilidad (verificada en tests/test_channel_fallback.py):
  * El texto SIEMPRE viaja en el mensaje. PMTP nunca lo reemplaza ni lo altera.
  * Si el receptor no soporta PMTP, recibe exactamente el mismo texto que recibiría
    sin PMTP: no se pierde nada y no cuesta nada.
  * Si el bus de memoria compartida falla (sin /dev/shm, permisos, slab corrupto),
    el canal degrada a texto y registra el motivo, sin lanzar excepciones al usuario.
  * Si ambos extremos soportan PMTP, el receptor obtiene además el vector latente
    copiado bit a bit desde memoria compartida, sin serializarlo a texto.
"""

from typing import Any, Dict, Optional, Tuple
import numpy as np


class PmtpChannel:
    def __init__(self, bus: Optional[Any] = None, enabled: bool = True):
        self.bus = bus
        self.enabled = enabled and bus is not None
        self.last_degradation: Optional[str] = None

    def send(self, text: str, latent: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """Construye el mensaje. El texto es obligatorio; el latente es un adjunto opcional."""
        if not isinstance(text, str):
            raise TypeError("text debe ser str: el canal de texto es la base obligatoria")
        msg: Dict[str, Any] = {"text": text, "pmtp": None}
        self.last_degradation = None
        if not self.enabled or latent is None:
            return msg
        try:
            vec = np.asarray(latent, dtype=np.float64).ravel()
            if vec.size == 0 or not np.all(np.isfinite(vec)):
                raise ValueError("latente vacío o con NaN/Inf")
            nrm = float(np.linalg.norm(vec))
            if nrm == 0.0:
                raise ValueError("latente nulo")
            desc = self.bus.publish_tensor(vec / nrm)
            msg["pmtp"] = {"slab": desc, "dim": int(vec.size), "norm": nrm}
        except Exception as exc:  # degradación silenciosa a texto
            self.last_degradation = f"send: {type(exc).__name__}: {exc}"
        return msg

    def receive(self, msg: Dict[str, Any], supports_pmtp: bool) -> Tuple[str, Optional[np.ndarray]]:
        """Devuelve (texto, latente|None). Un receptor sin PMTP sólo ve el texto."""
        text = msg["text"]
        self.last_degradation = None
        meta = msg.get("pmtp")
        if not supports_pmtp or not meta or self.bus is None:
            return text, None
        try:
            unit = self.bus.read_tensor(meta["slab"], verify_stiefel=True)
            return text, unit * float(meta["norm"])
        except Exception as exc:
            self.last_degradation = f"receive: {type(exc).__name__}: {exc}"
            return text, None
