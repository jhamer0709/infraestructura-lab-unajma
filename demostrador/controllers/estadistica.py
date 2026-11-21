"""Ruta del panel de Estadística sobre las sesiones reales guardadas."""
from fastapi import APIRouter, HTTPException, Request

from demostrador.services import estadistica as estadistica_servicio

rutas = APIRouter(prefix="/api/estadistica")


@rutas.get("")
def calcular(request: Request, alfa: float = 0.05, umbral_p95_s: float = 20.0,
             replicas_bootstrap: int = 10000, semilla: int = 0):
    if not (0 < alfa < 1):
        raise HTTPException(400, "alfa debe estar entre 0 y 1")
    if umbral_p95_s <= 0:
        raise HTTPException(400, "umbral_p95_s debe ser positivo")
    corridas = request.app.state.medicion.corridas()
    if not corridas:
        raise HTTPException(404, "todavía no hay sesiones reales guardadas; "
                                  "ejecuta al menos una desde la página de Sesiones")
    return estadistica_servicio.bateria(
        corridas, nivel_significancia=alfa, umbral_p95_s=umbral_p95_s,
        replicas_bootstrap=replicas_bootstrap, semilla=semilla,
        fuente="Sesiones reales guardadas")
