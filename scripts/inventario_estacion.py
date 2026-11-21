"""Inventario de una estación real del laboratorio: SO, paquetes y hardware.

Corresponde al ítem de la hoja de ruta "Inventario del laboratorio: SO,
paquetes y hardware" (v1.0) y al control "lista de paquetes versionada,
hardware, SO" de docs/PLAN_MEDICION.md sección 1. Se ejecuta UNA VEZ por
estación (antes de medir, y de nuevo si algo cambia) y el resultado se
versiona junto con los datos crudos, para poder declarar bajo qué entorno se
midió.

Pensado para Ubuntu/Debian (usa apt/dpkg); en otra distribución, las
secciones que no apliquen quedan vacías en vez de fallar.

Solo biblioteca estándar (subprocess, platform, socket). No requiere permisos
de administrador: todo lo que lee es de solo lectura (apt list, dpkg -l,
/proc, uname).

Uso:
  python scripts/inventario_estacion.py --salida resultados/inventario/pc-07.json
"""
import argparse
import json
import platform
import re
import socket
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Lo mínimo que importa para comparar el entorno entre estaciones y con lo
# declarado en el artículo: lo que usa el gestor de paquetes mismo y, si están
# instalados, el compilador/intérprete que representan "compilador" e
# "interprete" en demostrador/services/origen.py.
PAQUETES_CLAVE = ["apt", "dpkg", "gcc", "python3", "docker"]


def _correr(comando: list[str]) -> str | None:
    try:
        r = subprocess.run(comando, capture_output=True, text=True, timeout=10)
        return r.stdout.strip() if r.returncode == 0 else None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def _os_release() -> dict:
    ruta = Path("/etc/os-release")
    if not ruta.is_file():
        return {}
    datos = {}
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        if "=" in linea:
            clave, _, valor = linea.partition("=")
            datos[clave] = valor.strip('"')
    return datos


def _version_paquete(nombre: str) -> str | None:
    salida = _correr(["dpkg-query", "-W", "-f=${Version}", nombre])
    return salida or None


def _memoria_kb() -> int | None:
    ruta = Path("/proc/meminfo")
    if not ruta.is_file():
        return None
    m = re.search(r"MemTotal:\s*(\d+)\s*kB", ruta.read_text(encoding="utf-8"))
    return int(m.group(1)) if m else None


def inventario() -> dict:
    os_info = _os_release()
    return {
        "fecha_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "estacion": socket.gethostname(),
        "so": {
            "nombre": os_info.get("PRETTY_NAME") or platform.platform(),
            "id": os_info.get("ID"), "version_id": os_info.get("VERSION_ID"),
            "kernel": platform.release(),
            "arquitectura": platform.machine(),
        },
        "hardware": {
            "cpu": platform.processor() or _correr(["lscpu"]),
            "nucleos_logicos": subprocess.os.cpu_count(),
            "memoria_total_kb": _memoria_kb(),
        },
        "paquetes": {nombre: _version_paquete(nombre) for nombre in PAQUETES_CLAVE},
        "python_version": platform.python_version(),
    }


def main() -> None:
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--salida", required=True)
    arg = a.parse_args()

    datos = inventario()
    ruta = Path(arg.salida)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(datos, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
