import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402

from api import index  # noqa: E402

index.RETARDO_S = 0.01  # origen rápido para las pruebas
cliente = TestClient(index.app)


def setup_function():
    cliente.post("/api/cache/vaciar")


def test_salud():
    assert cliente.get("/api/salud").json()["estado"] == "ok"


def test_directo_siempre_sale_al_origen():
    for _ in range(3):
        assert cliente.get("/api/paquete/compilador?modo=directo").json()["acierto"] is False
    assert cliente.get("/api/cache/estado").json()["salidas_al_origen"] == 3


def test_cache_sale_una_sola_vez():
    primero = cliente.get("/api/paquete/compilador?modo=cache").json()
    segundo = cliente.get("/api/paquete/compilador?modo=cache").json()
    assert primero["acierto"] is False and segundo["acierto"] is True
    assert cliente.get("/api/cache/estado").json()["salidas_al_origen"] == 1


def test_vaciar_deja_el_cache_frio():
    cliente.get("/api/paquete/compilador?modo=cache")
    cliente.post("/api/cache/vaciar")
    assert cliente.get("/api/paquete/compilador?modo=cache").json()["acierto"] is False


def test_rechaza_paquete_y_modo_desconocidos():
    assert cliente.get("/api/paquete/otro").status_code == 404
    assert cliente.get("/api/paquete/compilador?modo=x").status_code == 400
