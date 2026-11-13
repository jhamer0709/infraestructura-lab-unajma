import csv
import io

from fastapi.testclient import TestClient

from api.index import app

cliente = TestClient(app)


def test_salud_y_configuraciones():
    assert cliente.get("/api/salud").json()["estado"] == "ok"
    datos = cliente.get("/api/configuraciones").json()
    assert datos["configuraciones"] == ["base", "cache", "mirror", "ambos"]
    assert datos["por_defecto"] == "base"


def test_sesion_devuelve_una_fila_por_estacion():
    r = cliente.post("/api/sesiones", json={"configuracion": "cache", "n": 4})
    assert r.status_code == 201
    cuerpo = r.json()
    assert [o["estacion"] for o in cuerpo["observaciones"]] == [1, 2, 3, 4]
    assert cuerpo["p95"] > 0


def test_sin_configuracion_usa_la_variable_de_entorno(monkeypatch):
    monkeypatch.setenv("CONFIGURACION", "ambos")
    r = cliente.post("/api/sesiones", json={"n": 1})
    assert r.json()["configuracion"] == "ambos"


def test_rechaza_entradas_invalidas():
    assert cliente.post("/api/sesiones", json={"configuracion": "otra", "n": 2}).status_code == 400
    assert cliente.post("/api/sesiones", json={"configuracion": "base", "n": 0}).status_code == 422
    assert cliente.post("/api/sesiones", json={"configuracion": "base", "n": 31}).status_code == 422


def test_resumen_excluye_calentamiento_y_csv_lo_conserva():
    cliente.post("/api/sesiones", json={"configuracion": "base", "n": 7})
    cliente.post("/api/sesiones", json={"configuracion": "base", "n": 7, "calentamiento": True})
    cliente.post("/api/sesiones", json={"configuracion": "cache", "n": 7})

    filas = {(f["n"], f["configuracion"]): f for f in cliente.get("/api/resumen").json()["filas"]}
    assert filas[(7, "base")]["sesiones"] == 1
    assert filas[(7, "base")]["reduccion_p95"] is None
    assert filas[(7, "cache")]["reduccion_p95"] > 0

    crudo = list(csv.DictReader(io.StringIO(cliente.get("/api/observaciones.csv").text)))
    de_n7 = [f for f in crudo if f["n"] == "7"]
    assert len(de_n7) == 21
    assert sum(f["calentamiento"] == "1" for f in de_n7) == 7
