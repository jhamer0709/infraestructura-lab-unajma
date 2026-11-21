"""Rutas del panel de Rendimiento y calidad. Todo corre en memoria."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from demostrador import config
from demostrador.services import benchmark, calidad_codigo, correccion, iso25010

rutas = APIRouter(prefix="/api/calidad")


class PedidoCorreccion(BaseModel):
    n_estaciones: int = 20
    repeticiones: int = 10
    configuraciones: list[str] = Field(default_factory=lambda: list(config.CONFIGURACIONES))


class PedidoBenchmark(BaseModel):
    tamanos: list[int] = Field(min_length=1, max_length=10)
    repeticiones: int = 10
    retardo_origen_ms: float = 1.0
    configuraciones: list[str] = Field(default_factory=lambda: list(config.CONFIGURACIONES))


@rutas.post("/correccion")
async def ejecutar_correccion(pedido: PedidoCorreccion):
    if not (1 <= pedido.n_estaciones <= config.MAX_ESTACIONES):
        raise HTTPException(400, f"n_estaciones debe estar entre 1 y {config.MAX_ESTACIONES}")
    if not (1 <= pedido.repeticiones <= 200):
        raise HTTPException(400, "repeticiones debe estar entre 1 y 200")
    try:
        return await correccion.verificar(n_estaciones=pedido.n_estaciones, repeticiones=pedido.repeticiones,
                                           configuraciones=tuple(pedido.configuraciones))
    except ValueError as error:
        raise HTTPException(400, str(error)) from error


@rutas.post("/benchmark")
async def ejecutar_benchmark(pedido: PedidoBenchmark):
    try:
        return await benchmark.correr(tamanos=pedido.tamanos, repeticiones=pedido.repeticiones,
                                       retardo_origen_ms=pedido.retardo_origen_ms,
                                       configuraciones=tuple(pedido.configuraciones))
    except ValueError as error:
        raise HTTPException(400, str(error)) from error


@rutas.get("/metricas-estaticas")
def metricas_estaticas():
    return {"por_grupo": calidad_codigo.metricas_por_grupo(), "por_archivo": calidad_codigo.metricas_por_archivo()}


@rutas.get("/iso25010")
def iso_25010():
    return {"filas": iso25010.tabla()}
