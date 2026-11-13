"""Conexión. PostgreSQL (Supabase, pooler de transacciones) o SQLite de respaldo."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from demostrador.models import Base


def crear_fabrica(url: str) -> sessionmaker:
    if url.startswith("sqlite"):
        motor = create_engine(url, connect_args={"check_same_thread": False})
    else:
        # Función sin servidor detrás de un pooler: sin pool propio y sin
        # sentencias preparadas, que el pooler de transacciones no admite.
        motor = create_engine(url, poolclass=NullPool, connect_args={"prepare_threshold": None})
    Base.metadata.create_all(motor)
    return sessionmaker(motor, expire_on_commit=False)
