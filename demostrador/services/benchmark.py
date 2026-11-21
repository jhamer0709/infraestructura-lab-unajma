"""Prueba de escalado: cómo crecen el tiempo y el uso de recursos con N.

Mide tiempo de CPU (`time.process_time`, no se reparte entre tareas
concurrentes como el reloj de pared) y pico de memoria del intérprete
(`tracemalloc`) por corrida. El exponente de complejidad empírica es la
pendiente de la regresión log(tiempo) ~ log(N): ≈1 sugiere escalado lineal,
≈2 cuadrático. Es una medida del propio demostrador en este proceso, no del
hardware del laboratorio.
"""
import time
import tracemalloc

import numpy as np

from demostrador.services.estadistica import mediana
from demostrador.services.medicion import simular


async def correr(*, tamanos: list[int], repeticiones: int = 10, retardo_origen_ms: float = 1.0,
                  configuraciones: tuple = ("base", "cache", "mirror", "ambos")) -> dict:
    if not tamanos or any(t < 1 for t in tamanos):
        raise ValueError("tamaños debe tener valores positivos")
    if not (1 <= repeticiones <= 100):
        raise ValueError("repeticiones debe estar entre 1 y 100")
    retardo_s = retardo_origen_ms / 1000

    filas = []
    for codigo in configuraciones:
        for n in tamanos:
            tiempos_cpu, recibos_por_s = [], []
            for _ in range(repeticiones):
                tracemalloc.start()
                cpu_inicio = time.process_time()
                pared_inicio = time.perf_counter()
                resultado = await simular(codigo, n, retardo_s)
                pared = time.perf_counter() - pared_inicio
                cpu = time.process_time() - cpu_inicio
                _, pico = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                tiempos_cpu.append(cpu)
                recibos_por_s.append(len(resultado["filas"]) / pared if pared > 0 else float("inf"))
            filas.append({
                "configuracion": codigo, "n": n, "repeticiones": repeticiones,
                "cpu_mediana_s": round(mediana(tiempos_cpu), 6),
                "estaciones_por_s": round(mediana(recibos_por_s), 1),
                "pico_memoria_kb": round(pico / 1024, 1),
            })

    exponentes = {}
    for codigo in configuraciones:
        xs = np.log([f["n"] for f in filas if f["configuracion"] == codigo])
        ys = np.log([max(f["cpu_mediana_s"], 1e-9) for f in filas if f["configuracion"] == codigo])
        if len(set(xs)) > 1:
            pendiente, intercepto = np.polyfit(xs, ys, 1)
            exponentes[codigo] = round(float(pendiente), 2)
    return {"filas": filas, "exponente_complejidad": exponentes}
