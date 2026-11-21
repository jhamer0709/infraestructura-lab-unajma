#!/usr/bin/env python3
"""Falla si demostrador/services/evidencia_pruebas.json (conteo de funciones/casos)
no coincide con lo que hay ahora mismo en tests/. Se usa en CI, donde tests/ sí existe,
para que el snapshot que ISO 25010 lee en producción nunca quede desactualizado en
silencio. Compara solo funciones/casos, no la fecha/commit de generación (esos cambian
en cada actualización por diseño).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.actualizar_evidencia_pruebas import contar_pruebas, SALIDA  # noqa: E402


def main() -> int:
    if not SALIDA.is_file():
        print(f"::error::falta {SALIDA}. Ejecuta scripts/actualizar_evidencia_pruebas.py.")
        return 1
    guardado = json.loads(SALIDA.read_text(encoding="utf-8"))
    funciones, casos = contar_pruebas()
    if (guardado.get("funciones"), guardado.get("casos")) != (funciones, casos):
        print(
            "::error::demostrador/services/evidencia_pruebas.json quedó desactualizado: "
            f"guarda {guardado.get('funciones')} funciones/{guardado.get('casos')} casos, "
            f"pero tests/ tiene {funciones} funciones/{casos} casos ahora. "
            "Ejecuta 'python scripts/actualizar_evidencia_pruebas.py' y commitea el resultado."
        )
        return 1
    print(f"OK: evidencia_pruebas.json coincide con tests/ ({funciones} funciones, {casos} casos).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
