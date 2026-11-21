import asyncio

import pytest

from demostrador.services import experimento


def _ejecutar(**kwargs):
    return asyncio.run(experimento.ejecutar(**kwargs))


def test_ejecuta_diseno_completo_y_descarta_calentamiento():
    r = _ejecutar(tamanos=[5, 10], corridas_por_celda=4, corridas_calentamiento=2,
                   semilla=1, replicas_bootstrap=200, retardo_origen_ms=5)
    assert len(r["corridas"]) == 2 * 4 * 4  # 2 tamaños x 4 configuraciones x 4 corridas
    assert len(r["calentamiento"]) == 2 * 4 * 2
    # el orden se registra y es una permutación de 1..N
    ordenes = sorted(c["orden"] for c in r["corridas"] + r["calentamiento"])
    assert ordenes == list(range(1, len(ordenes) + 1))


def test_semilla_reproduce_el_mismo_orden():
    a = _ejecutar(tamanos=[5], corridas_por_celda=3, corridas_calentamiento=0,
                  semilla=42, retardo_origen_ms=5)
    b = _ejecutar(tamanos=[5], corridas_por_celda=3, corridas_calentamiento=0,
                  semilla=42, retardo_origen_ms=5)
    secuencia_a = [(c["configuracion"], c["n"]) for c in a["corridas"]]
    secuencia_b = [(c["configuracion"], c["n"]) for c in b["corridas"]]
    assert secuencia_a == secuencia_b


def test_subconjunto_de_configuraciones():
    r = _ejecutar(tamanos=[5], corridas_por_celda=3, corridas_calentamiento=0,
                  configuraciones=("base", "ambos"), retardo_origen_ms=5)
    assert {c["configuracion"] for c in r["corridas"]} == {"base", "ambos"}


@pytest.mark.parametrize("kwargs", [
    {"tamanos": []},
    {"tamanos": [0]},
    {"tamanos": [999]},
    {"tamanos": [5], "corridas_por_celda": 0},
    {"tamanos": [5], "nivel_significancia": 1.5},
    {"tamanos": [5], "umbral_p95_s": -1},
    {"tamanos": [5], "configuraciones": ("no-existe",)},
])
def test_parametros_invalidos(kwargs):
    with pytest.raises(experimento.ParametrosInvalidos):
        _ejecutar(**kwargs)
