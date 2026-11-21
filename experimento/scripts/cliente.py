"""Cliente de una estación: descarga el paquete y registra el tiempo.

Reemplaza a cliente.sh: ese usaba `bc` y `date +%N`, que no existen en la
imagen alpine:3 por defecto (BusyBox `date` no soporta %N y `bc` no viene
instalado), así que la corrida fallaba o escribía campos vacíos. Además
docs/PLAN_MEDICION.md pide reloj monotónico para medir, no reloj de pared:
`date` no lo es (puede saltar con un ajuste de hora), `time.monotonic()` sí.

Escribe una fila por estación: id_estacion,segundos,bytes,estado
(mismo formato que antes; scripts/analizar.py no cambia).

Solo biblioteca estándar: la imagen solo necesita python3, no paquetes extra.
"""
import os
import socket
import time
import urllib.request

OBJETIVO = os.environ.get("OBJETIVO", "http://origen/paquete.bin")
USE_CACHE = os.environ.get("USE_CACHE")
URL = "http://cache/paquete.bin" if USE_CACHE else OBJETIVO
SALIDA = "/resultados/corrida.csv"


def main() -> None:
    inicio = time.monotonic()
    estado = 0
    total_bytes = 0
    try:
        with urllib.request.urlopen(URL, timeout=120) as r:
            while True:
                trozo = r.read(65536)
                if not trozo:
                    break
                total_bytes += len(trozo)
    except Exception:
        estado = 1
    segundos = time.monotonic() - inicio

    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, "a", encoding="utf-8") as f:
        f.write(f"{socket.gethostname()},{segundos:.6f},{total_bytes},{estado}\n")


if __name__ == "__main__":
    main()
