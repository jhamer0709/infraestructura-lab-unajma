"""Mediana y p95 por configuración y N, desde el CSV crudo.

Uso: python scripts/analizar.py datos/medicion.csv

Descarta las sesiones de calentamiento. Reporta el p95 agrupado y por sesión
(mínimo y máximo), porque las estaciones de una misma sesión no son
observaciones independientes.
"""
import csv
import math
import statistics
import sys
from collections import defaultdict

ORDEN = ["base", "cache", "mirror", "ambos"]


def p95(valores):
    v = sorted(valores)
    return v[max(0, math.ceil(0.95 * len(v)) - 1)]


def main(ruta):
    celdas = defaultdict(lambda: defaultdict(list))
    with open(ruta, encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            if fila["calentamiento"] == "1":
                continue
            celdas[(int(fila["n"]), fila["configuracion"])][fila["sesion"]].append(float(fila["segundos"]))

    base = {}
    print(f"{'N':>3} {'config.':8} {'ses.':>4} {'obs':>4} {'mediana':>8} {'p95':>8} {'p95 por sesión':>16} {'reducción':>10}")
    for (n, codigo) in sorted(celdas, key=lambda c: (c[0], ORDEN.index(c[1]))):
        sesiones = celdas[(n, codigo)]
        todos = [t for s in sesiones.values() for t in s]
        por_sesion = [p95(s) for s in sesiones.values()]
        valor = p95(todos)
        if codigo == "base":
            base[n] = valor
        reduccion = f"{100 * (1 - valor / base[n]):.1f} %" if codigo != "base" and n in base else "-"
        rango = f"{min(por_sesion):.3f}-{max(por_sesion):.3f}"
        print(f"{n:>3} {codigo:8} {len(sesiones):>4} {len(todos):>4} {statistics.median(todos):>8.3f} "
              f"{valor:>8.3f} {rango:>16} {reduccion:>10}")


if __name__ == "__main__":
    main(sys.argv[1])
