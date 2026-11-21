"""Diseño de pruebas experimentales: las cuatro configuraciones del artículo, por tamaño.

Corre enteramente en memoria, con el mismo origen y enlace simulados que
`medicion.py` (`services/entrega.py` y `services/origen.py`): no guarda
sesiones en la base ni toca `t_sesion`/`t_observacion`. Sirve para validar el
procedimiento de análisis antes de aplicarlo a los datos reales del
laboratorio (`/api/resumen`, `/api/observaciones.csv`).

La unidad de la prueba es la corrida (una sesión con N estaciones), no la
estación: coincide con `docs/PLAN_MEDICION.md`. El orden de las corridas se
aleatoriza con la semilla declarada y queda registrado.
"""
import random
import time

from demostrador import config
from demostrador.services.estadistica import mediana, p95
from demostrador.services.medicion import simular
from demostrador.services.origen import PAQUETES


class ParametrosInvalidos(ValueError):
    pass


def _validar(tamanos, corridas_por_celda, corridas_calentamiento, replicas_bootstrap,
             nivel_significancia, umbral_p95_s, retardo_origen_ms, configuraciones):
    if not tamanos or any(t < 1 or t > config.MAX_ESTACIONES for t in tamanos):
        raise ParametrosInvalidos(f"tamaños debe tener valores entre 1 y {config.MAX_ESTACIONES}")
    if not configuraciones or any(c not in config.CONFIGURACIONES for c in configuraciones):
        raise ParametrosInvalidos(f"configuraciones debe ser un subconjunto de {config.CONFIGURACIONES}")
    if not (1 <= corridas_por_celda <= 200):
        raise ParametrosInvalidos("corridas por celda debe estar entre 1 y 200")
    if not (0 <= corridas_calentamiento <= 50):
        raise ParametrosInvalidos("corridas de calentamiento debe estar entre 0 y 50")
    if not (100 <= replicas_bootstrap <= 100000):
        raise ParametrosInvalidos("réplicas del bootstrap debe estar entre 100 y 100000")
    if not (0 < nivel_significancia < 1):
        raise ParametrosInvalidos("nivel de significancia debe estar entre 0 y 1")
    if umbral_p95_s <= 0:
        raise ParametrosInvalidos("umbral de aceptación p95 debe ser positivo")
    if retardo_origen_ms <= 0:
        raise ParametrosInvalidos("intensidad (retardo de origen) debe ser positiva")


async def ejecutar(*, tamanos: list[int], corridas_por_celda: int = 10, corridas_calentamiento: int = 2,
                    semilla: int = 2026, nivel_significancia: float = 0.05, umbral_p95_s: float = 20.0,
                    replicas_bootstrap: int = 10000, retardo_origen_ms: float = 5.0,
                    configuraciones: tuple = config.CONFIGURACIONES) -> dict:
    _validar(tamanos, corridas_por_celda, corridas_calentamiento, replicas_bootstrap,
             nivel_significancia, umbral_p95_s, retardo_origen_ms, configuraciones)
    retardo_s = retardo_origen_ms / 1000

    tareas = []
    for n in tamanos:
        for codigo in configuraciones:
            for _ in range(corridas_calentamiento):
                tareas.append({"tipo": "calentamiento", "n": n, "configuracion": codigo})
            for _ in range(corridas_por_celda):
                tareas.append({"tipo": "medicion", "n": n, "configuracion": codigo})

    orden = list(range(len(tareas)))
    random.Random(semilla).shuffle(orden)

    inicio_total = time.perf_counter()
    corridas, calentamiento = [], []
    for posicion, i in enumerate(orden, start=1):
        t = tareas[i]
        inicio = time.perf_counter()
        resultado = await simular(t["configuracion"], t["n"], retardo_s)
        duracion = time.perf_counter() - inicio
        tiempos = [f["segundos"] for f in resultado["filas"]]
        fila = {
            "orden": posicion, "configuracion": t["configuracion"], "n": t["n"],
            "mediana": round(mediana(tiempos), 6), "p95": round(p95(tiempos), 6),
            "duracion_corrida_s": round(duracion, 4),
            "salidas_origen": resultado["salidas_origen"],
            "sincronizacion_mirror": resultado["sincronizacion_mirror"],
        }
        (calentamiento if t["tipo"] == "calentamiento" else corridas).append(fila)
    duracion_total = time.perf_counter() - inicio_total

    return {
        "parametros": {
            "tamanos": tamanos, "corridas_por_celda": corridas_por_celda,
            "corridas_calentamiento": corridas_calentamiento, "semilla": semilla,
            "nivel_significancia": nivel_significancia, "umbral_p95_s": umbral_p95_s,
            "replicas_bootstrap": replicas_bootstrap, "retardo_origen_ms": retardo_origen_ms,
            "configuraciones": list(configuraciones), "productos_catalogo": len(PAQUETES),
        },
        "duracion_total_s": round(duracion_total, 3),
        "corridas": corridas,
        "calentamiento": calentamiento,
    }
