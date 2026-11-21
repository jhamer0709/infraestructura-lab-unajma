import asyncio

from fastapi.testclient import TestClient

from api.index import app
from demostrador.services import benchmark, calidad_codigo, correccion, iso25010

cliente = TestClient(app)


def test_correccion_coincide_siempre_con_lo_esperado():
    r = asyncio.run(correccion.verificar(n_estaciones=10, repeticiones=5))
    assert r["todo_correcto"] is True
    assert r["total_coinciden"] == r["total_corridas"] == 5 * 4
    assert r["discrepancias"] == []


def test_correccion_detecta_configuracion_invalida_como_error_de_la_capa_superior():
    import pytest
    with pytest.raises(ValueError):
        asyncio.run(correccion.verificar(n_estaciones=5, repeticiones=1, configuraciones=("no-existe",)))


def test_benchmark_devuelve_una_fila_por_configuracion_y_tamano():
    r = asyncio.run(benchmark.correr(tamanos=[5, 10], repeticiones=2, retardo_origen_ms=1,
                                      configuraciones=("base", "ambos")))
    assert len(r["filas"]) == 2 * 2
    assert set(r["exponente_complejidad"]) == {"base", "ambos"}
    assert all(f["estaciones_por_s"] > 0 for f in r["filas"])


def test_metricas_estaticas_cubren_los_archivos_reales():
    filas = calidad_codigo.metricas_por_archivo()
    nombres = {f["archivo"] for f in filas}
    assert "demostrador/services/entrega.py" in nombres
    assert all(f["complejidad_total"] >= f["funciones"] for f in filas)  # mínimo 1 por función


def test_iso25010_declara_nueve_filas_con_estado_valido():
    filas = iso25010.tabla()
    assert len(filas) == 9
    assert {f["estado"] for f in filas} <= {"medido", "parcial", "no medido"}


def test_iso25010_cuenta_pruebas_en_vivo_cuando_existe_tests():
    # tests/ existe en este entorno (es el que se está ejecutando ahora mismo), así
    # que debe contarse en vivo y no caer al snapshot.
    funciones, casos, procedencia = iso25010._contar_pruebas()
    assert funciones > 0 and casos >= funciones
    assert "medido en este entorno" in procedencia


def test_iso25010_usa_snapshot_cuando_no_hay_carpeta_tests_ni_github(tmp_path, monkeypatch):
    # Simula el entorno de producción (Vercel), donde ni tests/ ni .github/ se
    # despliegan (.vercelignore): debe caer al snapshot versionado en vez de
    # reportar 0 pruebas y "ningún workflow configurado".
    snapshot = tmp_path / "evidencia_pruebas.json"
    snapshot.write_text(
        '{"funciones": 29, "casos": 38, "workflows": ["pruebas.yml"], '
        '"generado_en_utc": "2026-01-01T00:00:00Z", "generado_en_commit": "abc123"}',
        encoding="utf-8",
    )
    carpeta_vacia = tmp_path / "no-existe-tests-ni-github-aqui"
    monkeypatch.setattr(iso25010, "RAIZ", carpeta_vacia)
    monkeypatch.setattr(iso25010, "SNAPSHOT_PRUEBAS", snapshot)

    funciones, casos, procedencia = iso25010._contar_pruebas()
    assert (funciones, casos) == (29, 38)
    assert "snapshot generado en commit abc123" in procedencia
    assert "no se despliega a producción" in procedencia

    workflows, procedencia_wf = iso25010._workflows()
    assert workflows == ["pruebas.yml"]
    assert "snapshot del commit abc123" in procedencia_wf

    # Y esa procedencia debe quedar visible en la fila de la tabla, no solo en la cifra.
    fila = next(f for f in iso25010.tabla() if f["subcaracteristica"] == "Capacidad de ser probada")
    assert "29 funciones de prueba (38 casos" in fila["evidencia"]
    assert "snapshot generado en commit abc123" in fila["evidencia"]
    assert "pruebas.yml" in fila["evidencia"]


def test_endpoint_correccion():
    r = cliente.post("/api/calidad/correccion", json={"n_estaciones": 8, "repeticiones": 3})
    assert r.status_code == 200
    assert r.json()["todo_correcto"] is True


def test_endpoint_benchmark():
    r = cliente.post("/api/calidad/benchmark", json={"tamanos": [5, 10], "repeticiones": 2, "retardo_origen_ms": 1})
    assert r.status_code == 200
    assert len(r.json()["filas"]) == 2 * 4


def test_endpoint_metricas_y_iso():
    assert cliente.get("/api/calidad/metricas-estaticas").status_code == 200
    r = cliente.get("/api/calidad/iso25010")
    assert r.status_code == 200
    assert len(r.json()["filas"]) == 9
