"""Cada configuración sale al origen exactamente las veces que le corresponde."""
import asyncio

import pytest

from demostrador.services import entrega
from demostrador.services.estadistica import p95
from demostrador.services.medicion import simular
from demostrador.services.origen import PAQUETES

N = 6
TOTAL = len(PAQUETES)                              # 5
NO_ESPEJABLES = sum(not p.espejable for p in PAQUETES)  # 1


@pytest.mark.parametrize("codigo, salidas, sincronizacion", [
    ("base", N * TOTAL, 0),                 # cada estación baja todo
    ("cache", TOTAL, 0),                    # cada paquete sale una sola vez
    ("mirror", N * NO_ESPEJABLES, TOTAL - NO_ESPEJABLES),
    ("ambos", NO_ESPEJABLES, TOTAL - NO_ESPEJABLES),
])
def test_salidas_al_origen(codigo, salidas, sincronizacion):
    r = asyncio.run(simular(codigo, N, 0.01))
    assert r["salidas_origen"] == salidas
    assert r["sincronizacion_mirror"] == sincronizacion
    assert len(r["filas"]) == N


def test_cache_parte_frio_en_cada_sesion():
    for _ in range(2):
        r = asyncio.run(simular("cache", 3, 0.01))
        assert r["salidas_origen"] == TOTAL
        assert min(f["aciertos"] for f in r["filas"]) == 0


def test_configuracion_desconocida():
    with pytest.raises(ValueError):
        entrega.crear("otra")


def test_p95_por_rango_mas_cercano():
    assert p95(range(1, 101)) == 95
    assert p95([3.0]) == 3.0
