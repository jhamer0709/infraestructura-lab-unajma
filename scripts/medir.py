"""Runner de medición. Solo biblioteca estándar.

Uso:
  python scripts/medir.py --url http://127.0.0.1:8000
  python scripts/medir.py --url https://infraestructura-lab-unajma.vercel.app --sesiones 5

Recorre las configuraciones en orden aleatorio. Por cada configuración y cada
N ejecuta una sesión de calentamiento (se guarda marcada y no entra al
resumen) y luego las sesiones medidas. Cada sesión parte de caché frío. Al
terminar descarga el CSV crudo: una fila por estación y sesión.
"""
import argparse
import json
import random
import urllib.request
from pathlib import Path

CONFIGURACIONES = ["base", "cache", "mirror", "ambos"]


def sesion(base, configuracion, n, calentamiento=False):
    cuerpo = json.dumps({"configuracion": configuracion, "n": n,
                         "calentamiento": calentamiento}).encode()
    pedido = urllib.request.Request(f"{base}/api/sesiones", data=cuerpo, method="POST",
                                    headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(pedido, timeout=120) as r:
        return json.load(r)


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--url", required=True)
    a.add_argument("--n", type=int, nargs="+", default=[1, 10, 30])
    a.add_argument("--sesiones", type=int, default=5)
    a.add_argument("--salida", default="datos/medicion.csv")
    a.add_argument("--semilla", type=int, default=None)
    arg = a.parse_args()

    base = arg.url.rstrip("/")
    orden = CONFIGURACIONES[:]
    random.Random(arg.semilla).shuffle(orden)
    print(f"orden de configuraciones: {orden}")

    for configuracion in orden:
        for n in arg.n:
            sesion(base, configuracion, n, calentamiento=True)
            for numero in range(1, arg.sesiones + 1):
                r = sesion(base, configuracion, n)
                print(f"{configuracion:7} n={n:<2} sesion={numero} p95={r['p95']:.3f}s "
                      f"salidas={r['salidas_origen']}")

    ruta = Path(arg.salida)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(f"{base}/api/observaciones.csv", timeout=120) as r:
        ruta.write_bytes(r.read())
    print(f"CSV crudo en {ruta}")


if __name__ == "__main__":
    main()
