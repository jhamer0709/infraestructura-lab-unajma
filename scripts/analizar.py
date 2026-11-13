"""Mediana y p95 por modo y N, desde el CSV crudo de medir.py.

Uso: python scripts/analizar.py datos/medicion.csv
El p95 se reporta agrupado y por sesión (mínimo y máximo), porque las
estaciones de una misma sesión no son observaciones independientes.
"""
import csv
import math
import statistics
import sys
from collections import defaultdict


def p95(valores):
    v = sorted(valores)
    return v[max(0, math.ceil(0.95 * len(v)) - 1)]


def main(ruta):
    celdas = defaultdict(lambda: defaultdict(list))
    with open(ruta, encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            celdas[(int(fila["n"]), fila["modo"])][fila["sesion"]].append(float(fila["segundos"]))

    base = {}
    print(f"{'N':>3} {'modo':8} {'obs':>4} {'mediana':>8} {'p95':>8} {'p95 por sesión':>18} {'reducción':>10}")
    for (n, modo) in sorted(celdas, key=lambda c: (c[0], c[1] != "directo")):
        sesiones = celdas[(n, modo)]
        todos = [t for s in sesiones.values() for t in s]
        por_sesion = [p95(s) for s in sesiones.values()]
        valor = p95(todos)
        if modo == "directo":
            base[n] = valor
        reduccion = f"{100 * (1 - valor / base[n]):.1f} %" if modo != "directo" and n in base else "-"
        rango = f"{min(por_sesion):.2f}-{max(por_sesion):.2f}"
        print(f"{n:>3} {modo:8} {len(todos):>4} {statistics.median(todos):>8.2f} {valor:>8.2f} {rango:>18} {reduccion:>10}")


if __name__ == "__main__":
    main(sys.argv[1])
