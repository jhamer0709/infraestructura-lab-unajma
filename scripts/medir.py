"""Runner de medición. Solo biblioteca estándar.

Uso:
  python scripts/medir.py --url http://127.0.0.1:8000
  python scripts/medir.py --url https://TU-PROYECTO.vercel.app --n 1 10 30 --sesiones 5

Por cada modo (en orden aleatorio) y cada N: una sesión de calentamiento que
se descarta, luego las sesiones medidas. Antes de cada sesión se vacía el
caché (caché frío). Escribe una fila por estación y sesión; los percentiles
se calculan después, con analizar.py.
"""
import argparse
import csv
import json
import random
import threading
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

CAMPOS = ["fecha_utc", "lista", "modo", "n", "sesion", "estacion",
          "segundos", "aciertos", "errores"]


def pedir(url, metodo="GET"):
    with urllib.request.urlopen(urllib.request.Request(url, method=metodo), timeout=120) as r:
        return json.load(r)


def estacion(base, modo, paquetes, salida, indice):
    inicio = time.monotonic()
    aciertos = errores = 0
    for p in paquetes:
        try:
            aciertos += bool(pedir(f"{base}/api/paquete/{p}?modo={modo}")["acierto"])
        except Exception:
            errores += 1
    salida[indice] = (time.monotonic() - inicio, aciertos, errores)


def sesion(base, modo, n, paquetes):
    pedir(f"{base}/api/cache/vaciar", "POST")
    salida = [None] * n
    hilos = [threading.Thread(target=estacion, args=(base, modo, paquetes, salida, i))
             for i in range(n)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()
    return salida


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--url", required=True)
    a.add_argument("--n", type=int, nargs="+", default=[1, 10, 30])
    a.add_argument("--sesiones", type=int, default=5)
    a.add_argument("--salida", default="datos/medicion.csv")
    a.add_argument("--semilla", type=int, default=None)
    arg = a.parse_args()

    base = arg.url.rstrip("/")
    info = pedir(f"{base}/api/paquetes")
    modos = ["directo", "cache"]
    random.Random(arg.semilla).shuffle(modos)

    ruta = Path(arg.salida)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(CAMPOS)
        for modo in modos:
            for n in arg.n:
                sesion(base, modo, n, info["paquetes"])  # calentamiento, descartado
                for s in range(1, arg.sesiones + 1):
                    ahora = datetime.now(timezone.utc).isoformat(timespec="seconds")
                    for i, (seg, ac, err) in enumerate(sesion(base, modo, n, info["paquetes"]), 1):
                        w.writerow([ahora, info["lista"], modo, n, s, i, f"{seg:.4f}", ac, err])
                    print(f"modo={modo} n={n} sesion={s} lista")
    print(f"orden de modos: {modos} · datos en {ruta}")


if __name__ == "__main__":
    main()
