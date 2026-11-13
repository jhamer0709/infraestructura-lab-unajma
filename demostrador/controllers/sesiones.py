"""Rutas HTTP. Validan la entrada y delegan en el servicio."""
import csv
import io

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field

from demostrador import config
from demostrador.services.medicion import CAMPOS_CSV
from demostrador.services.origen import PAQUETES

rutas = APIRouter(prefix="/api")


class PedidoSesion(BaseModel):
    configuracion: str | None = None
    n: int = Field(ge=1, le=config.MAX_ESTACIONES)
    calentamiento: bool = False


@rutas.get("/salud")
def salud():
    return {"estado": "ok", "version": config.VERSION, "lista": config.VERSION_LISTA,
            "entorno": config.entorno()}


@rutas.get("/configuraciones")
def configuraciones():
    return {"configuraciones": list(config.CONFIGURACIONES),
            "por_defecto": config.configuracion_por_defecto(),
            "paquetes": [p.nombre for p in PAQUETES]}


@rutas.post("/sesiones", status_code=201)
async def crear_sesion(pedido: PedidoSesion, request: Request):
    codigo = pedido.configuracion or config.configuracion_por_defecto()
    if codigo not in config.CONFIGURACIONES:
        raise HTTPException(400, f"configuracion debe ser una de {config.CONFIGURACIONES}")
    return await request.app.state.medicion.ejecutar(codigo, pedido.n, pedido.calentamiento)


@rutas.get("/resumen")
def resumen(request: Request):
    return {"filas": request.app.state.medicion.resumen()}


@rutas.get("/observaciones.csv")
def observaciones_csv(request: Request):
    salida = io.StringIO()
    escritor = csv.writer(salida, lineterminator="\n")
    escritor.writerow(CAMPOS_CSV)
    escritor.writerows(request.app.state.medicion.filas_crudas())
    return Response(salida.getvalue(), media_type="text/csv; charset=utf-8")
