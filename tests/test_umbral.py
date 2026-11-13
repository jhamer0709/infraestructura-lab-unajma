"""Prueba con umbral declarado antes de ejecutar.

Sobre el modelo simulado, con 30 estaciones, la configuración `ambos` debe
reducir el p95 y las salidas al origen en al menos 90 % frente a la base
(mismos umbrales que H1a y H1b). Detecta regresiones del modelo y de las
configuraciones; no es evidencia para el artículo.
"""
import asyncio

from demostrador.services.estadistica import p95
from demostrador.services.medicion import simular

UMBRAL = 0.90
N = 30


def test_ambos_alcanza_el_umbral_con_30_estaciones():
    base = asyncio.run(simular("base", N, 0.02))
    ambos = asyncio.run(simular("ambos", N, 0.02))

    p95_base = p95(f["segundos"] for f in base["filas"])
    p95_ambos = p95(f["segundos"] for f in ambos["filas"])

    assert 1 - p95_ambos / p95_base >= UMBRAL
    assert 1 - ambos["salidas_origen"] / base["salidas_origen"] >= UMBRAL
