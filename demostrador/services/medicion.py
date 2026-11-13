"""Ejecuta una sesión de preparación, la guarda y resume lo guardado."""
import asyncio
import time
from collections import defaultdict
from datetime import timezone

from demostrador import config
from demostrador.repositories.sesiones import RepositorioSesiones
from demostrador.services import entrega
from demostrador.services.estadistica import mediana, p95
from demostrador.services.origen import PAQUETES, Contexto, Enlace


async def simular(codigo: str, n: int, retardo_s: float) -> dict:
    """N estaciones concurrentes preparan su entorno. El caché parte frío."""
    estrategia = entrega.crear(codigo)
    ctx = Contexto(enlace=Enlace(retardo_s))

    async def estacion(numero: int) -> dict:
        inicio = time.perf_counter()
        aciertos = 0
        for paquete in PAQUETES:
            aciertos += await estrategia.entregar(paquete, ctx)
        return {"estacion": numero, "segundos": time.perf_counter() - inicio,
                "aciertos": aciertos, "errores": 0}

    filas = await asyncio.gather(*(estacion(i) for i in range(1, n + 1)))
    return {"filas": list(filas), "salidas_origen": ctx.enlace.salidas,
            "sincronizacion_mirror": estrategia.sincronizacion()}


def _utc(fecha) -> str:
    """SQLite devuelve fechas sin zona; se guardaron en UTC."""
    if fecha.tzinfo is None:
        fecha = fecha.replace(tzinfo=timezone.utc)
    return fecha.astimezone(timezone.utc).isoformat(timespec="seconds")


class ServicioMedicion:
    def __init__(self, repositorio: RepositorioSesiones):
        self._repo = repositorio

    async def ejecutar(self, codigo: str, n: int, calentamiento: bool = False) -> dict:
        resultado = await simular(codigo, n, config.retardo_origen_s())
        sesion = self._repo.guardar(
            codigo=codigo, n=n, calentamiento=calentamiento, entorno=config.entorno(),
            salidas_origen=resultado["salidas_origen"],
            sincronizacion_mirror=resultado["sincronizacion_mirror"],
            filas=resultado["filas"])
        tiempos = [f["segundos"] for f in resultado["filas"]]
        return {
            "sesion": str(sesion.uuid), "configuracion": codigo, "n": n,
            "calentamiento": calentamiento, "p95": round(p95(tiempos), 4),
            "mediana": round(mediana(tiempos), 4),
            "salidas_origen": resultado["salidas_origen"],
            "sincronizacion_mirror": resultado["sincronizacion_mirror"],
            "paquetes": len(PAQUETES),
            "observaciones": [{**f, "segundos": round(f["segundos"], 4)} for f in resultado["filas"]],
        }

    def resumen(self) -> list[dict]:
        """Una fila por (N, configuración). La reducción es frente a la base del mismo N."""
        celdas = defaultdict(list)
        for s in self._repo.listar():
            celdas[(s.n_estaciones, s.configuracion.codigo)].append(s)

        orden = {c: i for i, c in enumerate(config.CONFIGURACIONES)}
        filas, base = [], {}
        for (n, codigo) in sorted(celdas, key=lambda c: (c[0], orden[c[1]])):
            sesiones = celdas[(n, codigo)]
            por_sesion = [p95([o.segundos for o in s.observaciones]) for s in sesiones]
            todos = [o.segundos for s in sesiones for o in s.observaciones]
            salidas = round(mediana([s.salidas_origen for s in sesiones]), 1)
            valor = p95(todos)
            if codigo == "base":
                base[n] = (valor, salidas)
            fila = {"n": n, "configuracion": codigo, "sesiones": len(sesiones),
                    "observaciones": len(todos), "mediana": round(mediana(todos), 4),
                    "p95": round(valor, 4), "p95_sesion_min": round(min(por_sesion), 4),
                    "p95_sesion_max": round(max(por_sesion), 4), "salidas_origen": salidas,
                    "reduccion_p95": None, "reduccion_salidas": None}
            if codigo != "base" and n in base:
                fila["reduccion_p95"] = round(100 * (1 - valor / base[n][0]), 1)
                fila["reduccion_salidas"] = round(100 * (1 - salidas / base[n][1]), 1)
            filas.append(fila)
        return filas

    def filas_crudas(self) -> list[list]:
        """Una fila por estación y sesión, incluidas las de calentamiento."""
        return [[_utc(s.iniciada_en), s.entorno, s.lista.version,
                 s.configuracion.codigo, s.n_estaciones, str(s.uuid), int(s.es_calentamiento),
                 o.estacion, f"{o.segundos:.4f}", o.aciertos, o.errores,
                 s.salidas_origen, s.sincronizacion_mirror]
                for s in self._repo.listar(incluir_calentamiento=True) for o in s.observaciones]


CAMPOS_CSV = ["fecha_utc", "entorno", "lista", "configuracion", "n", "sesion", "calentamiento",
              "estacion", "segundos", "aciertos", "errores", "salidas_origen", "sincronizacion_mirror"]
