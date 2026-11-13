"""Configuración leída del entorno. Ver .env.example."""
import os

VERSION = "0.2.0"
VERSION_LISTA = "2026-11-12"
CONFIGURACIONES = ("base", "cache", "mirror", "ambos")
MAX_ESTACIONES = 30

# Entrega local (caché o mirror en la LAN) como fracción del tiempo del origen.
FRACCION_LOCAL = 0.02


def configuracion_por_defecto() -> str:
    valor = os.getenv("CONFIGURACION", "base").strip().lower()
    return valor if valor in CONFIGURACIONES else "base"


def retardo_origen_s() -> float:
    return float(os.getenv("ORIGEN_RETARDO_MS", "50")) / 1000


def entorno() -> str:
    return os.getenv("ENTORNO", "demostrador")


def url_base_datos() -> str:
    """PostgreSQL si hay DATABASE_URL; si no, SQLite local como respaldo."""
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        carpeta = "/tmp" if os.getenv("VERCEL") else "."
        return f"sqlite:///{carpeta}/demostrador.db"
    for prefijo in ("postgres://", "postgresql://"):
        if url.startswith(prefijo):
            return "postgresql+psycopg://" + url[len(prefijo):]
    return url
