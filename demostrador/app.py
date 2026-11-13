"""Arma la aplicación: conecta repositorio, servicio y rutas."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from demostrador import config
from demostrador.controllers.sesiones import rutas
from demostrador.repositories.base_datos import crear_fabrica
from demostrador.repositories.sesiones import RepositorioSesiones
from demostrador.services.medicion import ServicioMedicion


def crear_app() -> FastAPI:
    app = FastAPI(title="Demostrador caché/mirror - UNAJMA", version=config.VERSION)

    repositorio = RepositorioSesiones(crear_fabrica(config.url_base_datos()))
    repositorio.asegurar_catalogos()
    app.state.medicion = ServicioMedicion(repositorio)
    app.include_router(rutas)

    # En local la aplicación sirve también la página. En Vercel la sirve
    # public/ y esta función solo recibe /api/*.
    publico = Path(__file__).resolve().parent.parent / "public"
    if publico.is_dir():
        app.mount("/", StaticFiles(directory=publico, html=True), name="publico")
    return app
