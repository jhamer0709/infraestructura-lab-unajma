"""Acceso a datos de sesiones y observaciones. Solo aquí se toca la base."""
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import selectinload, sessionmaker

from demostrador import config
from demostrador.models import Configuracion, ListaPaquete, Observacion, Sesion


class RepositorioSesiones:
    def __init__(self, fabrica: sessionmaker):
        self._fabrica = fabrica

    def asegurar_catalogos(self) -> None:
        with self._fabrica() as bd:
            existentes = set(bd.scalars(select(Configuracion.codigo)))
            for codigo in config.CONFIGURACIONES:
                if codigo not in existentes:
                    bd.add(Configuracion(codigo=codigo,
                                         usa_cache=codigo in ("cache", "ambos"),
                                         usa_mirror=codigo in ("mirror", "ambos")))
            if not bd.scalar(select(ListaPaquete).where(ListaPaquete.version == config.VERSION_LISTA)):
                bd.add(ListaPaquete(version=config.VERSION_LISTA,
                                    descripcion="Lista simulada del demostrador"))
            bd.commit()

    def guardar(self, *, codigo: str, n: int, calentamiento: bool, entorno: str,
                salidas_origen: int, sincronizacion_mirror: int, filas: list[dict]) -> Sesion:
        with self._fabrica() as bd:
            sesion = Sesion(
                configuracion=bd.scalars(select(Configuracion).where(Configuracion.codigo == codigo)).one(),
                lista=bd.scalars(select(ListaPaquete).where(ListaPaquete.version == config.VERSION_LISTA)).one(),
                n_estaciones=n, es_calentamiento=calentamiento, entorno=entorno,
                salidas_origen=salidas_origen, sincronizacion_mirror=sincronizacion_mirror,
                observaciones=[Observacion(estacion=f["estacion"],
                                           segundos=Decimal(f"{f['segundos']:.4f}"),
                                           aciertos=f["aciertos"], errores=f["errores"])
                               for f in filas])
            bd.add(sesion)
            bd.commit()
            return sesion

    def listar(self, incluir_calentamiento: bool = False) -> list[Sesion]:
        consulta = (select(Sesion).where(Sesion.deleted_at.is_(None))
                    .options(selectinload(Sesion.observaciones),
                             selectinload(Sesion.configuracion), selectinload(Sesion.lista))
                    .order_by(Sesion.id))
        if not incluir_calentamiento:
            consulta = consulta.where(Sesion.es_calentamiento.is_(False))
        with self._fabrica() as bd:
            return list(bd.scalars(consulta))
