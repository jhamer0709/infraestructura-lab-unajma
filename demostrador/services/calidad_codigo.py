"""Métricas estáticas reales del propio código: complejidad ciclomática (McCabe)
y anidamiento máximo, por archivo. Se calculan con `ast`, sin dependencias
externas, para que corran igual en Vercel que en local.

Complejidad de una función = 1 + número de puntos de decisión (if/elif, for,
while, except, with, operadores booleanos `and`/`or`, comprensiones,
expresiones condicionales, `match`/`case`). Es la definición estándar de
McCabe aplicada nodo por nodo del AST, no una estimación.
"""
import ast
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
GRUPOS = {
    "Experimentos y Estadística": ["demostrador/services/experimento.py", "demostrador/services/estadistica.py"],
    "Entrega (las cuatro configuraciones)": ["demostrador/services/entrega.py", "demostrador/services/origen.py"],
    "Medición y persistencia": ["demostrador/services/medicion.py", "demostrador/repositories/sesiones.py",
                                 "demostrador/repositories/base_datos.py", "demostrador/models.py"],
    "Rutas HTTP (controladores)": ["demostrador/controllers/sesiones.py", "demostrador/controllers/experimentos.py",
                                    "demostrador/controllers/estadistica.py", "demostrador/controllers/calidad.py"],
}


class _VisitanteFuncion(ast.NodeVisitor):
    """Cuenta puntos de decisión y profundidad de anidamiento dentro de una función."""

    def __init__(self):
        self.complejidad = 1
        self.profundidad = 0
        self.profundidad_max = 0

    def _decision(self, nodo):
        self.complejidad += 1
        self._anidado(nodo)

    def _anidado(self, nodo):
        self.profundidad += 1
        self.profundidad_max = max(self.profundidad_max, self.profundidad)
        self.generic_visit(nodo)
        self.profundidad -= 1

    def visit_If(self, nodo):
        self._decision(nodo)

    def visit_For(self, nodo):
        self._decision(nodo)

    def visit_AsyncFor(self, nodo):
        self._decision(nodo)

    def visit_While(self, nodo):
        self._decision(nodo)

    def visit_ExceptHandler(self, nodo):
        self._decision(nodo)

    def visit_With(self, nodo):
        self._anidado(nodo)  # no es un punto de decisión, pero sí anida

    def visit_AsyncWith(self, nodo):
        self._anidado(nodo)

    def visit_BoolOp(self, nodo):
        self.complejidad += len(nodo.values) - 1
        self.generic_visit(nodo)

    def visit_IfExp(self, nodo):
        self.complejidad += 1
        self.generic_visit(nodo)

    def visit_comprehension(self, nodo):
        self.complejidad += 1 + len(nodo.ifs)
        self.generic_visit(nodo)

    def visit_Match(self, nodo):
        self.complejidad += max(0, len(nodo.cases) - 1)
        self._anidado(nodo)


def _funciones(arbol: ast.AST):
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield nodo


def analizar_archivo(ruta_relativa: str) -> dict:
    ruta = RAIZ / ruta_relativa
    texto = ruta.read_text(encoding="utf-8")
    arbol = ast.parse(texto, filename=ruta_relativa)
    funciones = list(_funciones(arbol))
    complejidades, anidamientos = [], []
    for f in funciones:
        v = _VisitanteFuncion()
        for hijo in ast.iter_child_nodes(f):
            v.visit(hijo)
        complejidades.append(v.complejidad)
        anidamientos.append(v.profundidad_max)
    lineas = len([l for l in texto.splitlines() if l.strip()])
    return {
        "archivo": ruta_relativa, "lineas_codigo": lineas, "funciones": len(funciones),
        "complejidad_total": sum(complejidades),
        "complejidad_media": round(sum(complejidades) / len(complejidades), 2) if complejidades else 0,
        "complejidad_max": max(complejidades) if complejidades else 0,
        "anidamiento_max": max(anidamientos) if anidamientos else 0,
    }


def metricas_por_grupo() -> list:
    filas = []
    for grupo, archivos in GRUPOS.items():
        existentes = [a for a in archivos if (RAIZ / a).is_file()]
        if not existentes:
            continue
        m = [analizar_archivo(a) for a in existentes]
        filas.append({
            "grupo": grupo, "archivos": [x["archivo"] for x in m],
            "lineas_codigo": sum(x["lineas_codigo"] for x in m),
            "funciones": sum(x["funciones"] for x in m),
            "complejidad_total": sum(x["complejidad_total"] for x in m),
            "complejidad_media": round(sum(x["complejidad_total"] for x in m) / max(1, sum(x["funciones"] for x in m)), 2),
            "complejidad_max": max((x["complejidad_max"] for x in m), default=0),
            "anidamiento_max": max((x["anidamiento_max"] for x in m), default=0),
        })
    return filas


def metricas_por_archivo() -> list:
    archivos = sorted({a for lista in GRUPOS.values() for a in lista if (RAIZ / a).is_file()})
    return [analizar_archivo(a) for a in archivos]
