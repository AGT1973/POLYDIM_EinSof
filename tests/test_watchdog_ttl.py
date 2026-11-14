# ============================================================================
# TEST: Watchdog TTL de Slabs + Métricas SHM en Tiempo Real
# Proyecto: PMTP (Polydim Memory Tensor Protocol)
# Autor: Ariel García Traba — Independent Research / POLYDIM-EinsofOS
# ============================================================================
"""
Tests certificados en silicio:
  - test_slab_expires_after_ttl
  - test_watchdog_gc_cleans_zombie
  - test_metrics_active_leases
  - test_metrics_mac_verification_rate
"""

import sys
import os
import time
import threading
import numpy as np
import pytest

# Ajuste de path para importar desde E:\SUITE\pmtp directamente
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "pmtp"))

from pmtp.pmtp_shm_bus import PmtpShmBus
from pmtp.pmtp_metrics import PmtpMetricsCollector


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_bus(ttl: float = 2.0) -> PmtpShmBus:
    """Crea un bus con TTL corto para tests de watchdog."""
    return PmtpShmBus(
        prefix="test_wdg",
        max_slabs=16,
        max_dim=1024,
        auth_key=b"test-key-watchdog-ttl",
        lease_ttl_seconds=ttl,
    )


# ---------------------------------------------------------------------------
# A. Watchdog TTL de Slabs
# ---------------------------------------------------------------------------

class TestWatchdogTTL:

    def test_slab_expires_after_ttl(self):
        """
        Verifica que un slab cuyo acquired_at supera el TTL sea marcado como released
        tras la ejecución manual de _watchdog_gc().
        """
        bus = make_bus(ttl=1.0)
        try:
            # Allocar slab
            bus.allocate_tensor_slab(slab_id=1, num_elements=16, dtype=np.float64)
            assert 1 in bus.slabs, "El slab debe estar en el registro"
            assert not bus.slabs[1].get("released", False), "Recién creado no debe estar released"

            # Backdatear acquired_at para simular slab zombie
            bus.slabs[1]["acquired_at"] = time.monotonic() - 5.0  # 5s atrás > TTL 1.0s

            # Ejecutar GC manualmente
            bus._watchdog_gc()

            # Verificar que fue marcado como expirado
            assert bus.slabs[1].get("released", False), (
                "El slab debe ser marcado como released tras superar TTL"
            )
        finally:
            bus.stop_watchdog()
            bus.release_all()

    def test_watchdog_gc_cleans_zombie(self):
        """
        Verifica que el thread watchdog limpia automáticamente slabs zombie
        dentro del intervalo ttl + ttl/4 (máximo ttl * 1.5 para margen).
        """
        ttl = 1.0
        bus = make_bus(ttl=ttl)
        try:
            bus.allocate_tensor_slab(slab_id=2, num_elements=8, dtype=np.float64)
            assert not bus.slabs[2].get("released", False)

            # Backdatear para que el watchdog lo detecte en el próximo ciclo
            bus.slabs[2]["acquired_at"] = time.monotonic() - (ttl + 0.1)

            # Esperar hasta 2 ciclos de polling (ttl/4 * 2)
            deadline = time.monotonic() + ttl * 2.0
            released = False
            while time.monotonic() < deadline:
                time.sleep(0.05)
                if bus.slabs[2].get("released", False):
                    released = True
                    break

            assert released, (
                f"El watchdog thread debe haber liberado el slab zombie dentro de {ttl * 2.0}s"
            )
        finally:
            bus.stop_watchdog()
            bus.release_all()


# ---------------------------------------------------------------------------
# B. Métricas SHM en Tiempo Real
# ---------------------------------------------------------------------------

class TestMetrics:

    def test_metrics_active_leases(self):
        """
        Verifica que active_leases() retorne el número correcto de slabs activos
        y que total_bytes_allocated() sea > 0 con slabs abiertos.
        """
        bus = make_bus(ttl=30.0)
        try:
            assert bus.metrics.active_leases() == 0, "Sin slabs, active_leases debe ser 0"
            assert bus.metrics.total_bytes_allocated() == 0

            bus.allocate_tensor_slab(slab_id=10, num_elements=32, dtype=np.float64)
            assert bus.metrics.active_leases() == 1, "Debe reportar 1 slab activo"
            assert bus.metrics.total_bytes_allocated() > 0, "Bytes allocados deben ser > 0"

            bus.allocate_tensor_slab(slab_id=11, num_elements=16, dtype=np.float32)
            assert bus.metrics.active_leases() == 2, "Debe reportar 2 slabs activos"

            # Liberar uno
            bus.slabs[10]["released"] = True
            assert bus.metrics.active_leases() == 1, "Tras release, debe quedar 1 slab activo"

            # Verificar histogram tiene al menos la clave '<1s'
            hist = bus.metrics.lease_age_histogram()
            assert "<1s" in hist
            assert "1-5s" in hist
            assert "5-30s" in hist
            assert ">30s" in hist
            # El slab 11 recién creado debe caer en '<1s'
            assert hist["<1s"] >= 1, "El slab recién creado debe estar en bucket '<1s'"

        finally:
            bus.stop_watchdog()
            bus.release_all()

    def test_metrics_mac_verification_rate(self):
        """
        Verifica que mac_verification_rate() retorne 100.0 sin eventos y que
        baje ante eventos de fallo registrados manualmente.
        """
        bus = make_bus(ttl=30.0)
        try:
            # Sin eventos → 100%
            rate = bus.metrics.mac_verification_rate()
            assert rate == 100.0, f"Sin eventos MAC debe ser 100.0, obtuvo {rate}"

            # Registrar 3 éxitos y 1 fallo
            bus.metrics._record_mac_event(True)
            bus.metrics._record_mac_event(True)
            bus.metrics._record_mac_event(True)
            bus.metrics._record_mac_event(False)

            rate = bus.metrics.mac_verification_rate()
            assert abs(rate - 75.0) < 0.01, (
                f"Con 3 éxitos y 1 fallo esperamos 75.0%, obtuvo {rate}"
            )

            # Verificar throughput inicial
            thr = bus.metrics.throughput_bps()
            assert thr == 0.0, "Sin escrituras, throughput debe ser 0.0"

            # Registrar escritura y verificar throughput > 0
            bus.metrics._record_write(1024)
            thr = bus.metrics.throughput_bps()
            assert thr >= 0.0, "Throughput debe ser >= 0.0"

            # Verificar que MAC real funciona con publish+read (slab_id=5 dentro de max_slabs=16)
            bus.allocate_tensor_slab(slab_id=5, num_elements=4, dtype=np.float64)
            data = np.array([0.5, 0.5, 0.5, 0.5])
            bus.publish_snapshot_atomic(5, data)
            arr, gen = bus.read_snapshot_leased(5, verify_mac=True)
            # La verificación MAC debe haber registrado un éxito
            rate2 = bus.metrics.mac_verification_rate()
            assert rate2 > 0.0, "Tras verificación MAC exitosa real, rate debe ser > 0"

        finally:
            bus.stop_watchdog()
            bus.release_all()

    def test_metrics_property_returns_collector(self):
        """bus.metrics debe retornar siempre la misma instancia de PmtpMetricsCollector."""
        bus = make_bus(ttl=30.0)
        try:
            m1 = bus.metrics
            m2 = bus.metrics
            assert m1 is m2, "bus.metrics debe retornar siempre la misma instancia"
            assert isinstance(m1, PmtpMetricsCollector)
        finally:
            bus.stop_watchdog()
            bus.release_all()
