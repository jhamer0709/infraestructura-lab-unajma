"""Demostrador del método de medición (v0.1).

Simula la preparación de un entorno: cada "estación" pide la misma lista de
paquetes. Dos modos, elegidos por parámetro, igual que las configuraciones
del artículo:

  directo  cada pedido va al origen (línea base)
  cache    el primer pedido va al origen; los demás reciben la copia guardada

El origen es SIMULADO con un retardo fijo. Este servicio valida el
procedimiento (modos, caché frío, CSV crudo, p95); los resultados del
artículo se miden en el laboratorio, no aquí.
"""
import asyncio
import os
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

VERSION_LISTA = "2026-11-12"
# Lista versionada (variable de control): nombre -> peso relativo de descarga.
PAQUETES = {
    "compilador": 1.0,
    "interprete": 0.8,
    "librerias-base": 0.6,
    "gestor-paquetes": 0.3,
    "imagen-contenedor": 1.5,
}
RETARDO_S = float(os.getenv("ORIGEN_RETARDO_MS", "400")) / 1000
MODOS = ("directo", "cache")

app = FastAPI(title="Demostrador caché/mirror - UNAJMA", version="0.1.0")

_cache: dict[str, bytes] = {}
_candados: dict[str, asyncio.Lock] = {}
_salidas_al_origen = 0


_descargas_activas = 0
_PASO_S = 0.01


async def _descargar_del_origen(nombre: str) -> bytes:
    """Origen simulado tras un enlace compartido.

    Supuesto del modelo: el enlace reparte su capacidad por igual entre las
    descargas simultáneas. Una descarga sola tarda RETARDO_S x peso; con k
    descargas a la vez, cada una avanza a 1/k de esa velocidad.
    """
    global _salidas_al_origen, _descargas_activas
    _salidas_al_origen += 1
    _descargas_activas += 1
    try:
        pendiente = RETARDO_S * PAQUETES[nombre]
        while pendiente > 0:
            await asyncio.sleep(_PASO_S)
            pendiente -= _PASO_S / _descargas_activas
    finally:
        _descargas_activas -= 1
    return nombre.encode()


@app.get("/api/salud")
async def salud():
    return {"estado": "ok", "version": app.version, "lista": VERSION_LISTA}


@app.get("/api/paquetes")
async def paquetes():
    return {"lista": VERSION_LISTA, "paquetes": list(PAQUETES)}


@app.get("/api/paquete/{nombre}")
async def paquete(nombre: str, modo: str = "directo"):
    if nombre not in PAQUETES:
        raise HTTPException(404, "paquete fuera de la lista versionada")
    if modo not in MODOS:
        raise HTTPException(400, f"modo debe ser uno de {MODOS}")

    inicio = time.perf_counter()
    acierto = False
    if modo == "directo":
        await _descargar_del_origen(nombre)
    else:
        # Un candado por paquete: los pedidos concurrentes del mismo paquete
        # esperan a que termine el primero, en vez de salir todos al origen.
        candado = _candados.setdefault(nombre, asyncio.Lock())
        async with candado:
            if nombre in _cache:
                acierto = True
            else:
                _cache[nombre] = await _descargar_del_origen(nombre)
    return {
        "paquete": nombre,
        "modo": modo,
        "acierto": acierto,
        "segundos_servidor": round(time.perf_counter() - inicio, 4),
    }


@app.post("/api/cache/vaciar")
async def vaciar():
    """Deja el caché frío. Se llama antes de cada sesión medida."""
    global _salidas_al_origen
    _cache.clear()
    _salidas_al_origen = 0
    return {"cache": "vacio"}


@app.get("/api/cache/estado")
async def estado():
    return {"guardados": len(_cache), "salidas_al_origen": _salidas_al_origen}


# En local, la misma aplicación sirve la página. En Vercel la sirve la
# carpeta public/ y esta función solo recibe /api/*.
_publico = Path(__file__).resolve().parent.parent / "public"
if _publico.is_dir():
    app.mount("/", StaticFiles(directory=_publico, html=True), name="publico")
