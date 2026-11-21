"""Pruebas del pipeline de medición real del laboratorio: enrutamiento del
cliente por estación y consolidación de sesión. No usa red real; los casos de
red (descarga, cabecera X-Cache-Status) se prueban con un servidor HTTP local
efímero.
"""
import http.server
import json
import sys
import threading
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import estacion_laboratorio as el  # noqa: E402
import consolidar_sesion_laboratorio as cl  # noqa: E402


def test_paquetes_coincide_con_el_modelo_simulado():
    # Debe ser la misma lista (nombre y espejabilidad) que
    # demostrador/services/origen.py, o el resultado real deja de ser
    # comparable con el modelo (docs/PLAN_ESTRUCTURA.md sección 7).
    from demostrador.services.origen import PAQUETES as PAQUETES_MODELO
    esperado = tuple((p.nombre, p.espejable) for p in PAQUETES_MODELO)
    obtenido = tuple((p["nombre"], p["espejable"]) for p in el.PAQUETES)
    assert obtenido == esperado


@pytest.mark.parametrize("configuracion,nombre,espejable,esperado", [
    ("base", "compilador", True, "origen"),
    ("base", "imagen-contenedor", False, "origen"),
    ("cache", "compilador", True, "cache"),
    ("cache", "imagen-contenedor", False, "cache"),
    ("mirror", "compilador", True, "mirror"),
    ("mirror", "imagen-contenedor", False, "origen"),
    ("ambos", "compilador", True, "mirror"),
    ("ambos", "imagen-contenedor", False, "cache"),
])
def test_destino_coincide_con_entrega_py(configuracion, nombre, espejable, esperado):
    assert el.destino({"nombre": nombre, "espejable": espejable}, configuracion) == esperado


def test_url_de_exige_la_base_correspondiente():
    paquete = {"nombre": "compilador", "espejable": True}
    with pytest.raises(ValueError, match="--cache"):
        el.url_de(paquete, "cache", {"origen": "http://o"})


class _ServidorPrueba(http.server.ThreadingHTTPServer):
    allow_reuse_address = True


def _servir(contenido: bytes, cabeceras: dict[str, str]):
    """Servidor HTTP efímero en un hilo; devuelve (base_url, detener)."""
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            for k, v in cabeceras.items():
                self.send_header(k, v)
            self.send_header("Content-Length", str(len(contenido)))
            self.end_headers()
            self.wfile.write(contenido)

        def log_message(self, *a):
            pass

    servidor = _ServidorPrueba(("127.0.0.1", 0), Handler)
    hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
    hilo.start()
    puerto = servidor.server_address[1]
    return f"http://127.0.0.1:{puerto}", servidor.shutdown


def test_descargar_origen_siempre_cuenta_como_salida():
    base, detener = _servir(b"x" * 100, {})
    try:
        ok, fue_origen = el.descargar(f"{base}/compilador", "origen")
        assert ok and fue_origen
    finally:
        detener()


def test_descargar_mirror_nunca_cuenta_como_salida():
    base, detener = _servir(b"x" * 100, {})
    try:
        ok, fue_origen = el.descargar(f"{base}/compilador", "mirror")
        assert ok and not fue_origen
    finally:
        detener()


@pytest.mark.parametrize("estado_cache,fue_origen_esperado", [
    ("MISS", True), ("EXPIRED", True), ("BYPASS", True), ("HIT", False),
])
def test_descargar_cache_usa_x_cache_status(estado_cache, fue_origen_esperado):
    base, detener = _servir(b"x" * 100, {"X-Cache-Status": estado_cache})
    try:
        ok, fue_origen = el.descargar(f"{base}/compilador", "cache")
        assert ok and fue_origen is fue_origen_esperado
    finally:
        detener()


def test_descargar_sin_cabecera_cache_cuenta_como_salida():
    # Si el proxy real no manda X-Cache-Status (mal configurado), más vale
    # sobrestimar las salidas a origen que subestimarlas en silencio.
    base, detener = _servir(b"x" * 100, {})
    try:
        ok, fue_origen = el.descargar(f"{base}/compilador", "cache")
        assert ok and fue_origen
    finally:
        detener()


def test_descargar_falla_con_url_invalida():
    ok, fue_origen = el.descargar("http://127.0.0.1:1/no-existe", "origen")
    assert not ok and not fue_origen


def test_ejecutar_cuenta_aciertos_y_salidas_para_mirror():
    base, detener = _servir(b"x" * 10, {})
    try:
        resultado = el.ejecutar("mirror", {"origen": base, "mirror": base})
        assert resultado["aciertos"] == len(el.PAQUETES)
        assert resultado["errores"] == 0
        # Solo 'imagen-contenedor' (no espejable) sale a origen.
        assert resultado["salidas_origen_estacion"] == 1
    finally:
        detener()


def test_consolidar_suma_salidas_origen_de_todas_las_estaciones():
    filas = [
        {"estacion": "pc-01", "configuracion": "cache", "segundos": 1.0, "aciertos": 5,
         "errores": 0, "salidas_origen_estacion": 5},
        {"estacion": "pc-02", "configuracion": "cache", "segundos": 0.5, "aciertos": 5,
         "errores": 0, "salidas_origen_estacion": 0},
    ]
    configuracion, salidas_origen = cl.consolidar(filas, sincronizacion_mirror_s=0)
    assert configuracion == "cache"
    assert salidas_origen == 5


def test_consolidar_rechaza_configuraciones_mezcladas():
    filas = [
        {"estacion": "pc-01", "configuracion": "cache", "segundos": 1.0, "aciertos": 5,
         "errores": 0, "salidas_origen_estacion": 5},
        {"estacion": "pc-02", "configuracion": "mirror", "segundos": 0.5, "aciertos": 5,
         "errores": 0, "salidas_origen_estacion": 1},
    ]
    with pytest.raises(ValueError, match="misma configuración"):
        cl.consolidar(filas, sincronizacion_mirror_s=0)


def test_consolidar_sesion_escribe_el_csv_con_las_columnas_del_proyecto(tmp_path):
    archivos = []
    for nombre, salidas in [("pc-01", 5), ("pc-02", 0)]:
        ruta = tmp_path / f"{nombre}.json"
        ruta.write_text(json.dumps({"estacion": nombre, "configuracion": "cache",
                                     "segundos": 1.234, "aciertos": 5, "errores": 0,
                                     "salidas_origen_estacion": salidas}), encoding="utf-8")
        archivos.append(str(ruta))

    salida_csv = tmp_path / "medicion_laboratorio.csv"
    import sys as _sys
    argv_original = _sys.argv
    _sys.argv = ["consolidar_sesion_laboratorio.py", "--entorno", "lab-prueba", "--lista", "v1",
                 "--n", "2", "--sesion", "sesion-1", "--salida", str(salida_csv), *archivos]
    try:
        cl.main()
    finally:
        _sys.argv = argv_original

    contenido = salida_csv.read_text(encoding="utf-8").splitlines()
    assert contenido[0] == ",".join(cl.CAMPOS_CSV)
    assert len(contenido) == 3  # cabecera + 2 estaciones
    assert "sesion-1" in contenido[1] and ",5," in contenido[1] + contenido[2]
