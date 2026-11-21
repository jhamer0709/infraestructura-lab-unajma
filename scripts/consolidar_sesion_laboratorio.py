"""Consolida los archivos de una sesión del laboratorio (uno por estación, de
scripts/estacion_laboratorio.py) en filas con el formato crudo de
docs/PLAN_MEDICION.md, el mismo que usa demostrador/services/medicion.py
(CAMPOS_CSV) y que lee scripts/analizar.py.

salidas_origen y sincronizacion_mirror son valores de SESIÓN, no de estación
(sección 4 del plan): se calculan aquí, sumando las salidas de cada estación,
no en el cliente de cada una.

Uso:
  python scripts/consolidar_sesion_laboratorio.py \
      --entorno laboratorio-epis --lista v1 --n 10 \
      --calentamiento 0 --sincronizacion-mirror-s 0 \
      resultados/pc-01.json resultados/pc-02.json ...
"""
import argparse
import csv
import uuid
import json
from datetime import datetime, timezone
from pathlib import Path

CAMPOS_CSV = ["fecha_utc", "entorno", "lista", "configuracion", "n", "sesion", "calentamiento",
              "estacion", "segundos", "aciertos", "errores", "salidas_origen", "sincronizacion_mirror"]


def consolidar(filas_estacion: list[dict], sincronizacion_mirror_s: float) -> tuple[str, int]:
    """(configuración de la sesión, salidas_origen de la sesión). Valida que
    todas las estaciones compartan la misma configuración."""
    configuraciones = {f["configuracion"] for f in filas_estacion}
    if len(configuraciones) != 1:
        raise ValueError(f"todas las estaciones de una sesión deben tener la misma "
                          f"configuración; se encontraron: {sorted(configuraciones)}")
    salidas_origen = sum(f["salidas_origen_estacion"] for f in filas_estacion)
    return configuraciones.pop(), salidas_origen


def main() -> None:
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("archivos", nargs="+", help="JSON de cada estación (de estacion_laboratorio.py)")
    a.add_argument("--entorno", required=True)
    a.add_argument("--lista", required=True, help="versión de la lista de paquetes medida")
    a.add_argument("--n", type=int, required=True, help="estaciones concurrentes de la sesión")
    a.add_argument("--sesion", default=None, help="id de sesión; por defecto se genera uno")
    a.add_argument("--calentamiento", type=int, choices=[0, 1], default=0)
    a.add_argument("--sincronizacion-mirror-s", type=float, default=0,
                   help="tiempo de sincronización del mirror antes de la sesión, en segundos "
                        "(0 si la configuración no usa mirror)")
    a.add_argument("--salida", default="datos/medicion_laboratorio.csv")
    arg = a.parse_args()

    filas_estacion = [json.loads(Path(p).read_text(encoding="utf-8")) for p in arg.archivos]
    configuracion, salidas_origen = consolidar(filas_estacion, arg.sincronizacion_mirror_s)
    sesion_id = arg.sesion or str(uuid.uuid4())
    fecha_utc = datetime.now(timezone.utc).isoformat(timespec="seconds")

    ruta = Path(arg.salida)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    nuevo = not ruta.exists()
    with open(ruta, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if nuevo:
            w.writerow(CAMPOS_CSV)
        for fila in filas_estacion:
            w.writerow([fecha_utc, arg.entorno, arg.lista, configuracion, arg.n, sesion_id,
                        arg.calentamiento, fila["estacion"], f"{fila['segundos']:.4f}",
                        fila["aciertos"], fila["errores"], salidas_origen,
                        arg.sincronizacion_mirror_s])
    print(f"{len(filas_estacion)} filas añadidas a {ruta} "
          f"(sesión {sesion_id}, configuración {configuracion}, salidas_origen={salidas_origen})")


if __name__ == "__main__":
    main()
