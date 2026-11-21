import os
import tempfile

from fastapi.testclient import TestClient

from api.index import app
from demostrador.app import crear_app

cliente = TestClient(app)


def test_estadistica_endpoint_sin_sesiones_da_404():
    """Base propia y vacía: aislada de las sesiones que crean otros archivos de prueba."""
    original = os.environ.get("DATABASE_URL")
    carpeta = tempfile.mkdtemp()
    os.environ["DATABASE_URL"] = f"sqlite:///{carpeta}/vacia.db"
    try:
        cliente_vacio = TestClient(crear_app())
        r = cliente_vacio.get("/api/estadistica")
        assert r.status_code == 404
    finally:
        if original is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = original


def test_experimento_endpoint_devuelve_corridas_y_panel():
    cuerpo = {"tamanos": [5, 10], "corridas_por_celda": 4, "corridas_calentamiento": 1,
              "semilla": 9, "replicas_bootstrap": 200, "umbral_p95_s": 0.5, "retardo_origen_ms": 5}
    r = cliente.post("/api/experimentos", json=cuerpo)
    assert r.status_code == 200
    datos = r.json()
    assert len(datos["corridas"]) == 2 * 4 * 4
    assert datos["panel"]["fuente"] == "Corridas del experimento"
    assert datos["panel"]["n_corridas"] == len(datos["corridas"])


def test_experimento_endpoint_rechaza_parametros_invalidos():
    r = cliente.post("/api/experimentos", json={"tamanos": [999]})
    assert r.status_code == 400


def test_estadistica_endpoint_con_sesiones_reales():
    for cfg in ("base", "ambos"):
        cliente.post("/api/sesiones", json={"configuracion": cfg, "n": 3})
    r = cliente.get("/api/estadistica", params={"umbral_p95_s": 10})
    assert r.status_code == 200
    datos = r.json()
    assert datos["fuente"] == "Sesiones reales guardadas"
    assert datos["n_corridas"] >= 2
