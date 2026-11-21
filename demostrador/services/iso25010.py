"""Tabla de características ISO/IEC 25010, con evidencia tomada del propio
repositorio (conteo real de pruebas, workflows presentes) en vez de texto fijo.
Declara qué se evaluó y qué quedó fuera: eso es lo único que el resultado
permite afirmar.
"""
import ast
import json
from pathlib import Path

from demostrador import config

RAIZ = Path(__file__).resolve().parent.parent.parent
SNAPSHOT_PRUEBAS = Path(__file__).resolve().parent / "evidencia_pruebas.json"


def _contar_pruebas_en(carpeta: Path) -> tuple[int, int]:
    """(funciones de prueba, casos ejecutados contando @pytest.mark.parametrize)."""
    funciones, casos = 0, 0
    for archivo in sorted(carpeta.glob("test_*.py")):
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


def _contar_pruebas() -> tuple[int, int, str]:
    """(funciones, casos, procedencia de la evidencia).

    tests/ está en .vercelignore: no se despliega a producción (allí no debería ir
    código de prueba). Por eso, si la carpeta existe aquí, se cuenta en vivo; si no
    (como en la función de Vercel), se usa el snapshot versionado que scripts/
    actualizar_evidencia_pruebas.py genera a partir de tests/ y que CI mantiene
    sincronizado. Esto evita que la tabla reporte "0 pruebas" en producción cuando en
    realidad el repositorio tiene decenas: el número es real, solo que no se recalculó
    en esta misma máquina.
    """
    carpeta_tests = RAIZ / "tests"
    if carpeta_tests.is_dir():
        funciones, casos = _contar_pruebas_en(carpeta_tests)
        return funciones, casos, "medido en este entorno (carpeta tests/ presente)"
    if SNAPSHOT_PRUEBAS.is_file():
        datos = json.loads(SNAPSHOT_PRUEBAS.read_text(encoding="utf-8"))
        procedencia = (
            f"tomado del snapshot generado en commit {datos.get('generado_en_commit', '?')} "
            f"({datos.get('generado_en_utc', 'fecha desconocida')}); tests/ no se despliega a "
            "producción (ver .vercelignore)"
        )
        return datos.get("funciones", 0), datos.get("casos", 0), procedencia
    return 0, 0, "no se encontró tests/ ni el snapshot de evidencia_pruebas.json"


def _workflows() -> tuple[list[str], str]:
    """(nombres de workflow, procedencia). .github/ también está en .vercelignore,
    así que en producción se cae al mismo snapshot que _contar_pruebas()."""
    carpeta = RAIZ / ".github" / "workflows"
    if carpeta.is_dir():
        return sorted(p.name for p in carpeta.glob("*.yml")), "medido en este entorno"
    if SNAPSHOT_PRUEBAS.is_file():
        datos = json.loads(SNAPSHOT_PRUEBAS.read_text(encoding="utf-8"))
        return (
            datos.get("workflows", []),
            f"snapshot del commit {datos.get('generado_en_commit', '?')}; .github/ no se despliega (ver .vercelignore)",
        )
    return [], "no se encontró .github/workflows ni el snapshot"


def tabla() -> list[dict]:
    funciones, casos, procedencia_pruebas = _contar_pruebas()
    workflows, procedencia_workflows = _workflows()
    tiene_ci = bool(workflows)
    tiene_seguridad_ci = any("codeql" in w or "seguridad" in w or "security" in w for w in workflows)

    return [
        {"caracteristica": "Idoneidad funcional", "subcaracteristica": "Corrección funcional", "estado": "medido",
         "evidencia": "Las cuatro configuraciones se comparan contra lo que el modelo dice que deben entregar "
                      "(aciertos y salidas al origen deterministas, no otra implementación de referencia). "
                      "Ver /api/calidad/correccion."},
        {"caracteristica": "Eficiencia de desempeño", "subcaracteristica": "Comportamiento temporal", "estado": "medido",
         "evidencia": "Paneles de Experimentos y Estadística: mediana, p95, p99 por configuración y tamaño, "
                      "con Mann-Whitney, bootstrap y ANOVA factorial."},
        {"caracteristica": "Eficiencia de desempeño", "subcaracteristica": "Utilización de recursos", "estado": "medido",
         "evidencia": "Benchmark de escalado: tiempo de CPU (process_time, no de reloj de pared) y pico de "
                      "memoria del intérprete (tracemalloc) por corrida."},
        {"caracteristica": "Eficiencia de desempeño", "subcaracteristica": "Capacidad", "estado": "parcial",
         "evidencia": f"El benchmark escala N hasta {config.MAX_ESTACIONES} estaciones concurrentes dentro de "
                      "un solo proceso; no hay prueba de carga con múltiples procesos o usuarios simultáneos reales."},
        {"caracteristica": "Mantenibilidad", "subcaracteristica": "Analizabilidad / Modificabilidad", "estado": "medido",
         "evidencia": "Complejidad ciclomática (McCabe) y anidamiento máximo por archivo, calculados con `ast` "
                      "sobre el propio código. Ver /api/calidad/metricas-estaticas."},
        {"caracteristica": "Mantenibilidad", "subcaracteristica": "Capacidad de ser probada", "estado": "medido",
         "evidencia": f"{funciones} funciones de prueba ({casos} casos, con parametrize), {procedencia_pruebas}; "
                      f"CI ({procedencia_workflows}): "
                      f"{', '.join(workflows) if workflows else 'ningún workflow configurado'}."},
        {"caracteristica": "Fiabilidad", "subcaracteristica": "Madurez / Tolerancia a fallos", "estado": "no medido",
         "evidencia": "No se evaluó tasa de fallos ni recuperación: el origen y el enlace simulados no modelan errores."},
        {"caracteristica": "Seguridad", "subcaracteristica": "Confidencialidad / Autenticidad", "estado": "no medido",
         "evidencia": ("El CI ejecuta análisis de seguridad." if tiene_seguridad_ci
                       else "No se evaluó en este estudio: el CI no ejecuta análisis de seguridad ni auditoría de dependencias.")},
        {"caracteristica": "Usabilidad / Compatibilidad / Portabilidad", "subcaracteristica": "—", "estado": "no medido",
         "evidencia": "Fuera del alcance del estudio."},
    ]
