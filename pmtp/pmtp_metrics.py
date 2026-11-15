# ============================================================================
# PMTP METRICS COLLECTOR — Métricas SHM en Tiempo Real
# Proyecto: PMTP (Polydim Memory Tensor Protocol)
# Autor: Ariel García Traba — Independent Research / POLYDIM-EinsofOS
# ============================================================================
"""
PmtpMetricsCollector: subsistema de métricas SHM en tiempo real, thread-safe.
Expuesto como `bus.metrics` (property de PmtpShmBus).
"""

import time
import threading
from collections import deque
from typing import Dict, Deque, Tuple


class PmtpMetricsCollector:
    """
    Colector de métricas de memoria compartida en tiempo real.

    Métricas disponibles:
      - active_leases()           → int   : slabs activos (no liberados)
      - total_bytes_allocated()   → int   : bytes totales en slabs activos
      - lease_age_histogram()     → dict  : distribución de edades de slabs
      - mac_verification_rate()   → float : tasa de MACs exitosos (ventana 60s)
      - throughput_bps()          → float : bytes/seg escritos (ventana 10s)
    """

    def __init__(self, bus: "PmtpShmBus"):  # type: ignore[name-defined]
        self._bus = bus
        self._lock = threading.Lock()

        # Ventana deslizante MAC verifications: (timestamp, success: bool)
        self._mac_events: Deque[Tuple[float, bool]] = deque()
        self._MAC_WINDOW_S = 60.0

        # Ventana deslizante throughput: (timestamp, bytes)
        self._throughput_events: Deque[Tuple[float, int]] = deque()
        self._THROUGHPUT_WINDOW_S = 10.0

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def active_leases(self) -> int:
        """Número de slabs activos (no marcados como released)."""
        with self._lock:
            return sum(
                1 for info in self._bus.slabs.values()
                if not info.get("released", False)
            )

    def total_bytes_allocated(self) -> int:
        """Bytes totales ocupados por slabs activos (payload * 2 slots + header)."""
        from pmtp_types import HEADER_COMPACT_SIZE
        with self._lock:
            total = 0
            for info in self._bus.slabs.values():
                if not info.get("released", False):
                    total += HEADER_COMPACT_SIZE + 2 * info.get("payload_bytes", 0)
            return total

    def lease_age_histogram(self) -> Dict[str, int]:
        """
        Histograma de edades de slabs activos.
        Buckets: '<1s', '1-5s', '5-30s', '>30s'
        """
        now = time.monotonic()
        buckets = {"<1s": 0, "1-5s": 0, "5-30s": 0, ">30s": 0}
        with self._lock:
            for info in self._bus.slabs.values():
                if info.get("released", False):
                    continue
                acquired = info.get("acquired_at", None)
                if acquired is None:
                    # Fallback: usar published_at_ns si no hay acquired_at
                    pub_ns = info.get("published_at_ns", None)
                    if pub_ns is None:
                        continue
                    age = (time.time_ns() - pub_ns) / 1e9
                else:
                    age = now - acquired

                if age < 1.0:
                    buckets["<1s"] += 1
                elif age < 5.0:
                    buckets["1-5s"] += 1
                elif age < 30.0:
                    buckets["5-30s"] += 1
                else:
                    buckets[">30s"] += 1
        return buckets

    def mac_verification_rate(self) -> float:
        """
        Porcentaje de verificaciones MAC exitosas en la última ventana de 60s.
        Retorna 100.0 si no hay eventos registrados (ningún fallo conocido).
        """
        cutoff = time.monotonic() - self._MAC_WINDOW_S
        with self._lock:
            # Limpiar eventos viejos
            while self._mac_events and self._mac_events[0][0] < cutoff:
                self._mac_events.popleft()
            if not self._mac_events:
                return 100.0
            successes = sum(1 for _, ok in self._mac_events if ok)
            return 100.0 * successes / len(self._mac_events)

    def throughput_bps(self) -> float:
        """
        Bytes por segundo escritos en la ventana deslizante de 10s.
        """
        cutoff = time.monotonic() - self._THROUGHPUT_WINDOW_S
        with self._lock:
            while self._throughput_events and self._throughput_events[0][0] < cutoff:
                self._throughput_events.popleft()
            if not self._throughput_events:
                return 0.0
            total_bytes = sum(b for _, b in self._throughput_events)
            # Ventana efectiva entre primer y último evento (mín 1s para evitar ÷0)
            if len(self._throughput_events) == 1:
                window = self._THROUGHPUT_WINDOW_S
            else:
                window = max(
                    self._throughput_events[-1][0] - self._throughput_events[0][0],
                    0.001
                )
            return total_bytes / window

    # ------------------------------------------------------------------
    # Métodos internos para registrar eventos (llamados desde el bus)
    # ------------------------------------------------------------------

    def _record_mac_event(self, success: bool) -> None:
        """Registra resultado de verificación MAC."""
        with self._lock:
            self._mac_events.append((time.monotonic(), success))

    def _record_write(self, num_bytes: int) -> None:
        """Registra escritura de bytes para throughput."""
        with self._lock:
            self._throughput_events.append((time.monotonic(), num_bytes))
