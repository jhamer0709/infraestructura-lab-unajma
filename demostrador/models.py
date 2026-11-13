"""Modelo de datos. Convenciones en docs/PLAN_BASE_DE_DATOS.md."""
import uuid as _uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey,
                        Identity, Integer, Numeric, String, UniqueConstraint, Uuid)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

ID = BigInteger().with_variant(Integer, "sqlite")


def ahora() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Estandar:
    """Columnas comunes a todas las tablas."""
    id: Mapped[int] = mapped_column(ID, Identity(always=True), primary_key=True)
    uuid: Mapped[_uuid.UUID] = mapped_column(Uuid, default=_uuid.uuid4, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=ahora, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=ahora, onupdate=ahora, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Configuracion(Estandar, Base):
    __tablename__ = "t_configuracion"
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    usa_cache: Mapped[bool] = mapped_column(Boolean, nullable=False)
    usa_mirror: Mapped[bool] = mapped_column(Boolean, nullable=False)


class ListaPaquete(Estandar, Base):
    __tablename__ = "t_lista_paquete"
    version: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    descripcion: Mapped[str] = mapped_column(String(200), nullable=False, default="")


class Sesion(Estandar, Base):
    __tablename__ = "t_sesion"
    __table_args__ = (CheckConstraint("n_estaciones BETWEEN 1 AND 30", name="ck_sesion_n"),)
    configuracion_id: Mapped[int] = mapped_column(ForeignKey("t_configuracion.id", ondelete="RESTRICT"), nullable=False)
    lista_paquete_id: Mapped[int] = mapped_column(ForeignKey("t_lista_paquete.id", ondelete="RESTRICT"), nullable=False)
    n_estaciones: Mapped[int] = mapped_column(Integer, nullable=False)
    es_calentamiento: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    entorno: Mapped[str] = mapped_column(String(20), nullable=False)
    salidas_origen: Mapped[int] = mapped_column(Integer, nullable=False)
    sincronizacion_mirror: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    bytes_salida: Mapped[int | None] = mapped_column(BigInteger)  # solo laboratorio
    iniciada_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=ahora, nullable=False)

    configuracion: Mapped[Configuracion] = relationship()
    lista: Mapped[ListaPaquete] = relationship()
    observaciones: Mapped[list["Observacion"]] = relationship(back_populates="sesion", order_by="Observacion.estacion")


class Observacion(Estandar, Base):
    __tablename__ = "t_observacion"
    __table_args__ = (
        UniqueConstraint("sesion_id", "estacion", name="uq_observacion_sesion_estacion"),
        CheckConstraint("segundos > 0", name="ck_observacion_segundos"),
        CheckConstraint("estacion >= 1", name="ck_observacion_estacion"),
    )
    sesion_id: Mapped[int] = mapped_column(ForeignKey("t_sesion.id", ondelete="RESTRICT"), nullable=False, index=True)
    estacion: Mapped[int] = mapped_column(Integer, nullable=False)
    segundos: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    aciertos: Mapped[int] = mapped_column(Integer, nullable=False)
    errores: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    sesion: Mapped[Sesion] = relationship(back_populates="observaciones")
