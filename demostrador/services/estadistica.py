"""Estadísticos. Siempre se calculan desde las observaciones crudas."""
import math
import statistics


def p95(valores) -> float:
    """Percentil 95 por rango más cercano."""
    v = sorted(float(x) for x in valores)
    return v[max(0, math.ceil(0.95 * len(v)) - 1)]


def mediana(valores) -> float:
    return statistics.median(float(x) for x in valores)
