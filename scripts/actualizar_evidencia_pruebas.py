#!/usr/bin/env python3
"""Recalcula el snapshot de evidencia de pruebas (demostrador/services/evidencia_pruebas.json)
a partir de la carpeta tests/ real.

Por qué existe: la carpeta tests/ está en .vercelignore (no se despliega a producción,
correctamente: el código de prueba no debería ir en la función serverless). Eso significa
que demostrador/services/iso25010.py, si solo mirara el sistema de archivos en vivo, vería
siempre 0 pruebas en producción aunque el repositorio tenga decenas. Este script calcula el
número real una vez (en el entorno de desarrollo o en CI, donde tests/ sí existe) y lo deja
en un archivo versionado que sí se despliega, con la fecha y el commit en que se generó, para
que la evidencia declare de dónde salió el dato en vez de aparentar una medición en vivo que
no es.

CI (pruebas.yml) ejecuta este script y falla si el snapshot quedó desactualizado respecto a
tests/, así nunca puede quedar desincronizado en silencio.
"""
import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "demostrador" / "services" / "evidencia_pruebas.json"


def contar_pruebas() -> tuple[int, int]:
    """(funciones de prueba, casos ejecutados contando @pytest.mark.parametrize)."""
    funciones, casos = 0, 0
    for archivo in sorted((RAIZ / "tests").glob("test_*.py")):
        arbol = ast.parse(archivo.read_text(encoding="utf-8"), filename=archivo.name)
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.FunctionDef) and nodo.name.startswith("test_"):
                funciones += 1
                n_params = 1
                for decorador in nodo.decorator_list:
                    if (isinstance(decorador, ast.Call) and len(decorador.args) >= 2
                            and isinstance(decorador.args[1], (ast.List, ast.Tuple))):
                        n_params = max(n_params, len(decorador.args[1].elts))
                casos += n_params
    return funciones, casos


def commit_actual() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ,
            capture_output=True, text=True, check=True, timeout=5,
        ).stdout.strip()
    except Exception:
        return "desconocido"


def main() -> None:
    funciones, casos = contar_pruebas()
    datos = {
        "funciones": funciones,
        "casos": casos,
        "generado_en_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generado_en_commit": commit_actual(),
    }
    SALIDA.write_text(json.dumps(datos, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Escrito {SALIDA.relative_to(RAIZ)}: {funciones} funciones, {casos} casos "
          f"(commit {datos['generado_en_commit']}).")


if __name__ == "__main__":
    main()
