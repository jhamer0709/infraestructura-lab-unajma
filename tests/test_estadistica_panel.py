import asyncio

from demostrador.services import estadistica, experimento


def _corridas():
    r = asyncio.run(experimento.ejecutar(tamanos=[5, 10], corridas_por_celda=6, corridas_calentamiento=1,
                                          semilla=3, replicas_bootstrap=300, retardo_origen_ms=5))
    return r["corridas"]


def test_bateria_devuelve_todas_las_secciones():
    panel = estadistica.bateria(_corridas(), nivel_significancia=0.05, umbral_p95_s=0.5,
                                replicas_bootstrap=300, semilla=3, fuente="prueba")
    assert panel["configuraciones"] == ["ambos", "base", "cache", "mirror"]
    assert panel["tamanos"] == [5, 10]
    assert len(panel["descriptiva"]) == 4
    assert len(panel["supuestos"]["normalidad"]) == 4
    assert panel["supuestos"]["homogeneidad_levene"]["p"] is not None
    # línea base siempre más lenta que las otras tres configuraciones, en ambos tamaños
    assert len(panel["comparacion_por_tamano"]) == 2 * 3
    assert all(c["reduccion_pct"] > 0 for c in panel["comparacion_por_tamano"])
    assert len(panel["anova_factorial"]) == 4  # configuración, N, interacción, error
    assert panel["conclusion"]["rechaza_h0_todos_los_tamanos"] is True
    # el tamaño (n) de la condición no se confunde con el conteo de sesiones
    fila = panel["resultados_por_condicion"][0]
    assert fila["n"] in (5, 10)
    assert fila["sesiones"] == 6


def test_bateria_sin_corridas_no_revienta():
    panel = estadistica.bateria([], fuente="vacío")
    assert panel["n_corridas"] == 0
    assert panel["descriptiva"] == []
    assert panel["comparacion_por_tamano"] == []


def test_wilson_y_cumplimiento_umbral():
    assert estadistica.wilson_ic(0, 0) == [0.0, 0.0]
    r = estadistica.cumplimiento_umbral([0.1, 0.2, 0.3, 5.0], umbral_s=1.0)
    assert r["dentro_umbral"] == 3
    assert r["proporcion"] == 75.0
