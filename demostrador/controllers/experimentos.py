"""Ruta del panel de Experimentos. No toca la base: todo corre en memoria.

Vercel corre cada función sin estado garantizado entre invocaciones, así que
esta ruta no intenta recordar la última corrida en el servidor: devuelve todo
de una vez (corridas, calentamiento y el panel estadístico ya calculado) y el
cliente arma los CSV para descargar desde esa misma respuesta.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from demostrador import config
from demostrador.services import estadistica, experimento

rutas = APIRouter(prefix="/api/experimentos")


class DisenoExperimento(BaseModel):
    tamanos: list[int] = Field(min_length=1, max_length=10)
    corridas_por_celda: int = 30
    corridas_calentamiento: int = 5
    semilla: int = 2026
    nivel_significancia: float = 0.05
    umbral_p95_s: float = 20.0
    replicas_bootstrap: int = 10000
    retardo_origen_ms: float = 50.0
    configuraciones: list[str] = Field(default_factory=lambda: list(config.CONFIGURACIONES))


@rutas.post("")
async def ejecutar(diseno: DisenoExperimento):
    try:
        resultado = await experimento.ejecutar(
            tamanos=diseno.tamanos, corridas_por_celda=diseno.corridas_por_celda,
            corridas_calentamiento=diseno.corridas_calentamiento, semilla=diseno.semilla,
            nivel_significancia=diseno.nivel_significancia, umbral_p95_s=diseno.umbral_p95_s,
            replicas_bootstrap=diseno.replicas_bootstrap, retardo_origen_ms=diseno.retardo_origen_ms,
            configuraciones=tuple(diseno.configuraciones))
    except experimento.ParametrosInvalidos as error:
        raise HTTPException(400, str(error)) from error

    panel = estadistica.bateria(
        resultado["corridas"], nivel_significancia=diseno.nivel_significancia,
        umbral_p95_s=diseno.umbral_p95_s, replicas_bootstrap=diseno.replicas_bootstrap,
        semilla=diseno.semilla, fuente="Corridas del experimento")
    return {**resultado, "panel": panel}
