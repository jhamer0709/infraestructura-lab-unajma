"""Cliente de una estación real del laboratorio: descarga la lista de
paquetes versionada según la configuración activa y registra el resultado.

Corre en cada estación por separado (una PC del laboratorio EPIS-UNAJMA).
Después de que todas las estaciones de una sesión terminaron, se consolidan
sus archivos con scripts/consolidar_sesion_laboratorio.py: salidas_origen y
sincronizacion_mirror son campos de SESIÓN, no de estación (ver
docs/PLAN_MEDICION.md sección 4), así que no se calculan aquí.

Solo biblioteca estándar. Reloj monotónico (time.monotonic()), no de pared,
como pide docs/PLAN_MEDICION.md para el laboratorio.

Enrutamiento (debe coincidir con demostrador/services/entrega.py, para que el
resultado real sea comparable con el modelo):
  base   -> siempre el origen real
  cache  -> siempre el proxy de caché (Nginx con proxy_cache; ver
            laboratorio/cache.conf)
  mirror -> lo espejable, del mirror local; lo demás, del origen
  ambos  -> lo espejable, del mirror local; lo demás, del proxy de caché

Para "cache" y "ambos", si una petición realmente llegó al origen (no se
sirvió desde la caché) se decide con la cabecera X-Cache-Status que
laboratorio/cache.conf agrega a la respuesta ($upstream_cache_status de
Nginx): todo menos HIT cuenta como salida real a origen (MISS, EXPIRED,
STALE, UPDATING, REVALIDATED, BYPASS, o la cabecera ausente).

Uso:
  python scripts/estacion_laboratorio.py \
      --configuracion cache --estacion pc-07 \
      --origen http://mirror-externo.ejemplo/paquetes \
      --cache http://10.0.0.5 --mirror http://10.0.0.6 \
      --salida resultados/pc-07.json
"""
import argparse
import json
import socket
import time
import urllib.request
from pathlib import Path

# Debe coincidir con demostrador/services/origen.py (PAQUETES): es la misma
# lista versionada, para que el resultado real sea comparable con el modelo.
# tests/test_estacion_laboratorio.py falla si se desincronizan.
PAQUETES = (
    {"nombre": "compilador", "espejable": True},
    {"nombre": "interprete", "espejable": True},
    {"nombre": "librerias-base", "espejable": True},
    {"nombre": "gestor-paquetes", "espejable": True},
    {"nombre": "imagen-contenedor", "espejable": False},
)

CONFIGURACIONES = ("base", "cache", "mirror", "ambos")


def destino(paquete: dict, configuracion: str) -> str:
    """A qué servidor va la petición: 'origen', 'cache' o 'mirror'."""
    espejable = paquete["espejable"]
    if configuracion == "base":
        return "origen"
    if configuracion == "cache":
        return "cache"
    if configuracion == "mirror":
        return "mirror" if espejable else "origen"
    if configuracion == "ambos":
        return "mirror" if espejable else "cache"
    raise ValueError(f"configuración desconocida: {configuracion}")


def url_de(paquete: dict, configuracion: str, bases: dict) -> str:
    destino_ = destino(paquete, configuracion)
    base = bases.get(destino_)
    if not base:
        raise ValueError(f"falta --{destino_} para la configuración '{configuracion}'")
    return f"{base.rstrip('/')}/{paquete['nombre']}"


def descargar(url: str, destino_: str) -> tuple[bool, bool]:
    """(éxito, fue_salida_a_origen).

    'origen' siempre cuenta como salida real; 'mirror' nunca (se sirve local
    por construcción); 'cache' depende de X-Cache-Status.
    """
    try:
        with urllib.request.urlopen(url, timeout=120) as r:
            while r.read(65536):
                pass
            if destino_ == "origen":
                return True, True
            if destino_ == "mirror":
                return True, False
            estado_cache = r.headers.get("X-Cache-Status", "").upper()
            return True, estado_cache != "HIT"
    except Exception:
        return False, False


def ejecutar(configuracion: str, bases: dict) -> dict:
    inicio = time.monotonic()
    aciertos = errores = 0
    salidas_origen_estacion = 0
    for paquete in PAQUETES:
        destino_ = destino(paquete, configuracion)
        url = url_de(paquete, configuracion, bases)
        ok, fue_origen = descargar(url, destino_)
        if ok:
            aciertos += 1
        else:
            errores += 1
        if fue_origen:
            salidas_origen_estacion += 1
    return {
        "configuracion": configuracion,
        "segundos": round(time.monotonic() - inicio, 4),
        "aciertos": aciertos, "errores": errores,
        "salidas_origen_estacion": salidas_origen_estacion,
    }


def main() -> None:
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--configuracion", required=True, choices=CONFIGURACIONES)
    a.add_argument("--estacion", default=socket.gethostname())
    a.add_argument("--origen", help="URL base del origen real (fuera de la LAN)")
    a.add_argument("--cache", help="URL base del proxy de caché (laboratorio/cache.conf)")
    a.add_argument("--mirror", help="URL base del mirror local (laboratorio/mirror.conf)")
    a.add_argument("--salida", required=True)
    arg = a.parse_args()

    bases = {"origen": arg.origen, "cache": arg.cache, "mirror": arg.mirror}
    resultado = {"estacion": arg.estacion, **ejecutar(arg.configuracion, bases)}

    ruta = Path(arg.salida)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(resultado, ensure_ascii=False))


if __name__ == "__main__":
    main()
