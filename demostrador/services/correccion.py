"""Corrección funcional: compara lo que cada configuración entrega contra lo
que el modelo dice que DEBE entregar (`services/entrega.py` y `origen.py`),
no contra otra implementación. Con un catálogo fijo y N estaciones, los
aciertos y las salidas al origen son deterministas; cualquier diferencia es
un defecto real, no ruido de medición.
"""
from demostrador.services.medicion import simular
from demostrador.services.origen import PAQUETES

_NUM_PAQUETES = len(PAQUETES)
_NUM_ESPEJABLES = sum(p.espejable for p in PAQUETES)
_NUM_NO_ESPEJABLES = _NUM_PAQUETES - _NUM_ESPEJABLES


def _esperado(codigo: str, n: int) -> dict:
    if codigo == "base":
        return {"aciertos": 0, "salidas_origen": n * _NUM_PAQUETES}
    if codigo == "cache":
        return {"aciertos": _NUM_PAQUETES * (n - 1), "salidas_origen": _NUM_PAQUETES}
    if codigo == "mirror":
        return {"aciertos": _NUM_ESPEJABLES * n, "salidas_origen": n * _NUM_NO_ESPEJABLES}
    if codigo == "ambos":
        return {"aciertos": _NUM_ESPEJABLES * n + _NUM_NO_ESPEJABLES * max(0, n - 1),
                "salidas_origen": _NUM_NO_ESPEJABLES}
    raise ValueError(f"configuración desconocida: {codigo}")


async def verificar(*, n_estaciones: int = 20, repeticiones: int = 10,
                     configuraciones: tuple = ("base", "cache", "mirror", "ambos")) -> dict:
    """Corre cada configuración `repeticiones` veces y compara contra lo esperado."""
    filas, discrepancias = [], []
    for codigo in configuraciones:
        esperado = _esperado(codigo, n_estaciones)
        coinciden = 0
        for intento in range(1, repeticiones + 1):
            resultado = await simular(codigo, n_estaciones, 0.001)
            observado = {
                "aciertos": sum(f["aciertos"] for f in resultado["filas"]),
                "salidas_origen": resultado["salidas_origen"],
            }
            errores = sum(f["errores"] for f in resultado["filas"])
            estaciones_con_todos_los_paquetes = all(
                f["aciertos"] + 0 <= _NUM_PAQUETES for f in resultado["filas"])  # nunca más aciertos que paquetes
            ok = (observado == esperado and errores == 0 and estaciones_con_todos_los_paquetes)
            coinciden += int(ok)
            if not ok:
                discrepancias.append({"configuracion": codigo, "intento": intento,
                                       "esperado": esperado, "observado": observado, "errores": errores})
        filas.append({"configuracion": codigo, "corridas": repeticiones, "coinciden": coinciden,
                       "proporcion": round(100 * coinciden / repeticiones, 1), "esperado": esperado})
    return {
        "n_estaciones": n_estaciones, "repeticiones": repeticiones,
        "total_corridas": repeticiones * len(configuraciones),
        "total_coinciden": sum(f["coinciden"] for f in filas),
        "por_configuracion": filas, "discrepancias": discrepancias,
        "todo_correcto": not discrepancias,
    }
