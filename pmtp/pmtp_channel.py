"""
pmtp_channel.py — Canal opcional con degradación observable garantizada a texto UTF-8.

Garantía de compatibilidad (verificada en tests/test_channel_fallback.py):
  * El texto SIEMPRE viaja en el mensaje. PMTP nunca lo reemplaza ni lo altera.
  * Si el receptor no soporta PMTP, recibe exactamente el mismo texto que recibiría
    sin PMTP: no se pierde nada y no cuesta nada.
  * Si el bus de memoria compartida falla (sin /dev/shm, permisos, slab corrupto, fallo MAC),
    el canal degrada a texto UTF-8 sin lanzar excepciones no capturadas, emite log estructurado
    WARN en stderr/JSON, activa la bandera PMTP_FLAG_FALLBACK_ACTIVE e incrementa métricas.
  * Auto-rearme: cuando una operación posterior vía SHM tiene éxito, PMTP_FLAG_FALLBACK_ACTIVE se limpia a False.
"""

import json
import sys
from typing import Any, Dict, Optional, Tuple
import numpy as np


class PmtpChannel:
    def __init__(self, bus: Optional[Any] = None, enabled: bool = True, emit_warn_logs: bool = True):
        self.bus = bus
        self.enabled = enabled and bus is not None
        self.emit_warn_logs = emit_warn_logs
        self.last_degradation: Optional[str] = None
        self.fallback_active: bool = False
        self.fallback_count: int = 0

    def _record_degradation(self, phase: str, exc: Exception) -> None:
        reason = f"{phase}: {type(exc).__name__}: {exc}"
        self.last_degradation = reason
        self.fallback_active = True
        self.fallback_count += 1
        if self.emit_warn_logs:
            event = {
                "level": "WARN",
                "flag": "PMTP_FLAG_FALLBACK_ACTIVE",
                "phase": phase,
                "error_type": type(exc).__name__,
                "detail": str(exc),
                "fallback_count": self.fallback_count,
            }
            print(json.dumps(event, ensure_ascii=False), file=sys.stderr)

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
            self.fallback_active = False  # Auto-rearme tras éxito en SHM
        except Exception as exc:  # Degradación observable garantizada a UTF-8
            self._record_degradation("send", exc)
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
            self.fallback_active = False  # Auto-rearme tras lectura autenticada exitosa
            return text, unit * float(meta["norm"])
        except Exception as exc:
            self._record_degradation("receive", exc)
            return text, None
