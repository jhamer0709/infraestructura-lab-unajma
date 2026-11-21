"""Estadísticos. Siempre se calculan desde las observaciones crudas.

Las funciones de `p95` y `mediana` no usan numpy/scipy a propósito: son las
que corren en el camino caliente de cada sesión (`medicion.py`). El resto de
este módulo (normalidad, comparación entre configuraciones, ANOVA, bootstrap)
solo se usa al pedir el panel de Estadística, así que puede apoyarse en scipy.
"""
import math
import statistics

import numpy as np
from scipy import stats as sstats


def p95(valores) -> float:
    """Percentil 95 por rango más cercano."""
    v = sorted(float(x) for x in valores)
    return v[max(0, math.ceil(0.95 * len(v)) - 1)]


def mediana(valores) -> float:
    return statistics.median(float(x) for x in valores)


def p(valores, q: float) -> float:
    v = sorted(float(x) for x in valores)
    return v[max(0, math.ceil(q * len(v)) - 1)]


def descriptiva(valores) -> dict:
    """Mediana, percentiles, media, desviación e intervalo de confianza de la media."""
    v = np.asarray([float(x) for x in valores], dtype=float)
    n = len(v)
    media = float(v.mean())
    desv = float(v.std(ddof=1)) if n > 1 else 0.0
    if n > 1:
        err = desv / math.sqrt(n)
        delta = sstats.t.ppf(0.975, n - 1) * err
    else:
        delta = 0.0
    return {
        "n": n, "mediana": mediana(v), "p90": p(v, 0.90), "p95": p95(v), "p99": p(v, 0.99),
        "media": media, "desv": desv, "ic_media": [round(media - delta, 4), round(media + delta, 4)],
        "min": float(v.min()), "max": float(v.max()),
    }


def normalidad(valores) -> dict:
    """Jarque-Bera. H0: los datos provienen de una normal."""
    v = np.asarray([float(x) for x in valores], dtype=float)
    n = len(v)
    if n < 8:
        return {"n": n, "asimetria": None, "curtosis_exc": None, "jb": None, "p": None,
                "normal": None, "decision": "n < 8: no aplica Jarque-Bera."}
    jb, pval = sstats.jarque_bera(v)
    return {
        "n": n, "asimetria": round(float(sstats.skew(v)), 2),
        "curtosis_exc": round(float(sstats.kurtosis(v)), 2),
        "jb": round(float(jb), 2), "p": round(float(pval), 6), "normal": bool(pval >= 0.05),
    }


def homogeneidad_levene(grupos: list) -> dict:
    """Levene centrado en la mediana (Brown-Forsythe). H0: varianzas iguales."""
    gs = [np.asarray([float(x) for x in g], dtype=float) for g in grupos if len(g) > 1]
    if len(gs) < 2:
        return {"f": None, "gl": None, "p": None, "iguales": None,
                "decision": "Se requieren al menos dos grupos con más de una observación."}
    f, pval = sstats.levene(*gs, center="median")
    return {"f": round(float(f), 2), "gl": [len(gs) - 1, sum(len(g) for g in gs) - len(gs)],
            "p": round(float(pval), 6), "iguales": bool(pval >= 0.05)}


def mann_whitney(a, b) -> dict:
    """Mann-Whitney U, dos colas, con tamaño del efecto r (rank-biserial)."""
    a = np.asarray([float(x) for x in a], dtype=float)
    b = np.asarray([float(x) for x in b], dtype=float)
    u, pval = sstats.mannwhitneyu(a, b, alternative="two-sided")
    r = 1 - (2 * u) / (len(a) * len(b))
    return {"u": float(u), "p": float(pval), "r_rank_biserial": round(float(r), 4)}


def welch_t(a, b) -> dict | None:
    """None cuando algún grupo tiene menos de dos observaciones: la varianza no está definida."""
    a = np.asarray([float(x) for x in a], dtype=float)
    b = np.asarray([float(x) for x in b], dtype=float)
    if len(a) < 2 or len(b) < 2:
        return None
    t, pval = sstats.ttest_ind(a, b, equal_var=False)
    va, vb = a.var(ddof=1), b.var(ddof=1)
    sp = math.sqrt((va + vb) / 2)
    d = (a.mean() - b.mean()) / sp if sp else None
    # Welch-Satterthwaite
    if va == 0 and vb == 0:
        gl = None
    else:
        gl = (va / len(a) + vb / len(b)) ** 2 / ((va / len(a)) ** 2 / (len(a) - 1) + (vb / len(b)) ** 2 / (len(b) - 1))
    return {"t": float(t) if not math.isnan(t) else None, "gl": round(float(gl), 1) if gl is not None else None,
            "p": float(pval) if not math.isnan(pval) else None, "d": round(float(d), 2) if d is not None else None}


def kruskal_wallis(grupos: list) -> dict:
    gs = [np.asarray([float(x) for x in g], dtype=float) for g in grupos if len(g)]
    if len(gs) < 2:
        return {"h": None, "gl": None, "p": None, "epsilon2": None}
    h, pval = sstats.kruskal(*gs)
    n = sum(len(g) for g in gs)
    epsilon2 = float(h) / (n - 1) if n > 1 else None
    return {"h": round(float(h), 2), "gl": len(gs) - 1, "p": float(pval),
            "epsilon2": round(epsilon2, 2) if epsilon2 is not None else None}


def bootstrap_diferencia_mediana(a, b, reps: int = 10000, seed: int = 0) -> dict:
    """IC por remuestreo (percentil) de la diferencia de medianas, mediana(a) - mediana(b)."""
    rng = np.random.default_rng(seed)
    a = np.asarray([float(x) for x in a], dtype=float)
    b = np.asarray([float(x) for x in b], dtype=float)
    deltas = np.empty(reps)
    for i in range(reps):
        ra = rng.choice(a, size=len(a), replace=True)
        rb = rng.choice(b, size=len(b), replace=True)
        deltas[i] = np.median(ra) - np.median(rb)
    delta_obs = float(np.median(a) - np.median(b))
    lo, hi = np.percentile(deltas, [2.5, 97.5])
    return {"delta_mediana": round(delta_obs, 6), "ic": [round(float(lo), 6), round(float(hi), 6)],
            "replicas": reps}


def correlacion_regresion(x, y) -> dict:
    x = np.asarray([float(v) for v in x], dtype=float)
    y = np.asarray([float(v) for v in y], dtype=float)
    rho, p_rho = sstats.spearmanr(x, y)
    r, p_r = sstats.pearsonr(x, y)
    pendiente, intercepto, r_lin, p_lin, _ = sstats.linregress(x, y)
    return {
        "n": len(x),
        "spearman": {"rho": round(float(rho), 4), "p": float(p_rho)},
        "pearson": {"r": round(float(r), 4), "p": float(p_r)},
        "pendiente_s_por_unidad": round(float(pendiente), 6), "r2": round(float(r_lin) ** 2, 4),
    }


def wilson_ic(aciertos: int, n: int, confianza: float = 0.95) -> list:
    """Intervalo de Wilson para una proporción."""
    if n == 0:
        return [0.0, 0.0]
    z = sstats.norm.ppf(1 - (1 - confianza) / 2)
    ph = aciertos / n
    denom = 1 + z**2 / n
    centro = ph + z**2 / (2 * n)
    radio = z * math.sqrt(ph * (1 - ph) / n + z**2 / (4 * n**2))
    return [round(max(0, (centro - radio) / denom) * 100, 1), round(min(1, (centro + radio) / denom) * 100, 1)]


def cumplimiento_umbral(valores, umbral_s: float) -> dict:
    """H0: la media >= umbral; H1: la media < umbral (t de una muestra, unilateral)."""
    v = np.asarray([float(x) for x in valores], dtype=float)
    n = len(v)
    dentro = int(np.sum(v <= umbral_s))
    resultado = {"n": n, "dentro_umbral": dentro, "proporcion": round(100 * dentro / n, 1) if n else 0.0,
                 "ic_wilson_95": wilson_ic(dentro, n), "p95": round(p95(v), 6) if n else None,
                 "p95_bajo_umbral": bool(p95(v) <= umbral_s) if n else None}
    if n > 1 and v.std(ddof=1) > 0:
        t, p_two = sstats.ttest_1samp(v, umbral_s)
        p_uno = p_two / 2 if t < 0 else 1 - p_two / 2
        resultado.update({"t": round(float(t), 3), "p_unilateral": float(p_uno),
                           "decision": "La media es significativamente menor que el umbral."
                           if p_uno < 0.05 and t < 0 else "No se rechaza H0 (media >= umbral)."})
    else:
        resultado.update({"t": None, "p_unilateral": None, "decision": "n insuficiente o varianza nula."})
    return resultado


def anova_factorial_log(filas: list) -> list:
    """ANOVA factorial de dos factores sobre ln(tiempo): configuración x N.

    `filas` es una lista de dicts con al menos {configuracion, n, segundos}.
    Diseño balanceado esperado; con celdas vacías o desbalanceadas se
    calculan tipo-I (secuenciales) con mínimos cuadrados, sin interpretar
    más allá de lo que el diseño permite.
    """
    configuraciones = sorted({f["configuracion"] for f in filas})
    tamanos = sorted({f["n"] for f in filas})
    if len(configuraciones) < 2 or len(tamanos) < 2:
        return []
    y = np.array([math.log(float(f["segundos"])) for f in filas])
    c_idx = {c: i for i, c in enumerate(configuraciones)}
    n_idx = {n: i for i, n in enumerate(tamanos)}
    a = len(configuraciones)
    b = len(tamanos)

    def dummies(idx_map, valor_col, k):
        m = np.zeros((len(filas), k - 1))
        for row, f in enumerate(filas):
            j = idx_map[f[valor_col]]
            if j > 0:
                m[row, j - 1] = 1
        return m

    xa = dummies(c_idx, "configuracion", a)
    xb = dummies(n_idx, "n", b)
    xab = np.einsum("ij,ik->ijk", xa, xb).reshape(len(filas), -1) if a > 1 and b > 1 else np.zeros((len(filas), 0))

    def sc_modelo(cols):
        if cols.shape[1] == 0:
            return 0.0, np.full_like(y, y.mean())
        x = np.column_stack([np.ones(len(filas)), cols])
        beta, *_ = np.linalg.lstsq(x, y, rcond=None)
        pred = x @ beta
        return float(np.sum((pred - y.mean()) ** 2)), pred

    sc_a, _ = sc_modelo(xa)
    sc_ab_solo = np.column_stack([xa, xb]) if xb.shape[1] else xa
    sc_a_b, _ = sc_modelo(sc_ab_solo)
    sc_b = sc_a_b - sc_a
    sc_total_modelo, pred_completo = sc_modelo(np.column_stack([xa, xb, xab]) if xab.shape[1] else sc_ab_solo)
    sc_ab = sc_total_modelo - sc_a_b
    sc_total = float(np.sum((y - y.mean()) ** 2))
    sc_error = float(np.sum((y - pred_completo) ** 2))

    gl_a, gl_b = a - 1, b - 1
    gl_ab = gl_a * gl_b
    gl_err = len(filas) - (gl_a + gl_b + gl_ab + 1)
    if gl_err <= 0:
        return []
    cm_err = sc_error / gl_err

    def fila(nombre, sc, gl):
        cm = sc / gl if gl else 0.0
        f = cm / cm_err if cm_err > 0 else float("nan")
        pval = float(1 - sstats.f.cdf(f, gl, gl_err)) if cm_err > 0 and not math.isnan(f) else None
        eta2 = sc / sc_total if sc_total else 0.0
        return {"fuente": nombre, "sc": round(sc, 4), "gl": gl, "cm": round(cm, 4),
                "f": round(f, 2) if not math.isnan(f) else None, "p": pval, "eta2": round(eta2, 3)}

    filas_out = [fila("Configuración", sc_a, gl_a)]
    if gl_b:
        filas_out.append(fila("N (tamaño)", sc_b, gl_b))
        if gl_ab:
            filas_out.append(fila("Configuración × N", sc_ab, gl_ab))
    filas_out.append({"fuente": "Error", "sc": round(sc_error, 4), "gl": gl_err,
                       "cm": round(cm_err, 4), "f": None, "p": None, "eta2": None})
    return filas_out


def _limpiar(obj):
    """Reemplaza NaN/Infinity por None: json no los acepta y algún estadístico
    queda indefinido cuando una celda tiene muy pocas observaciones."""
    if isinstance(obj, dict):
        return {k: _limpiar(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_limpiar(v) for v in obj]
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    return obj


def bateria(corridas: list, *, nivel_significancia: float = 0.05, umbral_p95_s: float = 20.0,
            replicas_bootstrap: int = 10000, semilla: int = 0, fuente: str = "") -> dict:
    """Panel de Estadística completo sobre una lista de corridas.

    `corridas` es una lista de dicts {configuracion, n, p95} — una fila por
    sesión medida (la unidad de la prueba, según `docs/PLAN_MEDICION.md`), no
    por estación. Sirve igual para las corridas sintéticas del panel de
    Experimentos que para las sesiones reales guardadas en la base.
    """
    configuraciones = sorted({c["configuracion"] for c in corridas})
    tamanos = sorted({c["n"] for c in corridas})
    alfa = nivel_significancia
    por_config = {cfg: [c["p95"] for c in corridas if c["configuracion"] == cfg] for cfg in configuraciones}

    descriptiva_s = {cfg: {"motor": cfg, **descriptiva(v)} for cfg, v in por_config.items() if v}
    supuestos = {cfg: {"motor": cfg, **normalidad(v)} for cfg, v in por_config.items() if v}
    homogeneidad = homogeneidad_levene([v for v in por_config.values() if len(v) > 1])

    base = "base" if "base" in por_config else (configuraciones[0] if configuraciones else None)
    comparaciones_globales = {}
    if base:
        for cfg in configuraciones:
            if cfg == base or not por_config.get(cfg) or not por_config.get(base):
                continue
            a, b = por_config[base], por_config[cfg]
            comparaciones_globales[cfg] = {
                "mann_whitney": mann_whitney(a, b), "welch_t": welch_t(a, b),
                "bootstrap": bootstrap_diferencia_mediana(a, b, replicas_bootstrap, semilla),
            }
    kw = kruskal_wallis(list(por_config.values())) if len(por_config) > 2 else None

    resultados_por_condicion = []
    comparacion_por_tamano = []
    base_por_n = {}
    for n in tamanos:
        for cfg in configuraciones:
            valores = [c["p95"] for c in corridas if c["n"] == n and c["configuracion"] == cfg]
            if not valores:
                continue
            d = descriptiva(valores)
            if cfg == base:
                base_por_n[n] = d["mediana"]
            sesiones = d.pop("n")  # descriptiva() usa "n" para el conteo de observaciones
            fila = {"motor": cfg, "n": n, "sesiones": sesiones, **d,
                    "p95_bajo_umbral": bool(d["p95"] <= umbral_p95_s)}
            resultados_por_condicion.append(fila)
        if base and base in {c["configuracion"] for c in corridas if c["n"] == n}:
            a = [c["p95"] for c in corridas if c["n"] == n and c["configuracion"] == base]
            for cfg in configuraciones:
                if cfg == base:
                    continue
                b = [c["p95"] for c in corridas if c["n"] == n and c["configuracion"] == cfg]
                if not b:
                    continue
                mw = mann_whitney(a, b)
                boot = bootstrap_diferencia_mediana(a, b, replicas_bootstrap, semilla)
                med_a, med_b = mediana(a), mediana(b)
                p_valido = mw["p"] if not math.isnan(mw["p"]) else None
                comparacion_por_tamano.append({
                    "n": n, "configuracion": cfg, "mediana_base": round(med_a, 6),
                    "mediana_config": round(med_b, 6), "delta_mediana": round(med_a - med_b, 6),
                    "ic_bootstrap": boot["ic"], "p": p_valido,
                    "significativo": (p_valido < alfa) if p_valido is not None else None,
                    "reduccion_pct": round(100 * (1 - med_b / med_a), 1) if med_a else None,
                    "aceleracion": round(med_a / med_b, 1) if med_b else None,
                    "r_rank_biserial": mw["r_rank_biserial"],
                    "identicas": bool(med_a == med_b),
                })

    correlaciones = {}
    for cfg in configuraciones:
        xs = [c["n"] for c in corridas if c["configuracion"] == cfg]
        ys = [c["p95"] for c in corridas if c["configuracion"] == cfg]
        if len(set(xs)) > 1 and len(ys) > 2:
            correlaciones[cfg] = correlacion_regresion(xs, ys)

    cumplimiento = {cfg: cumplimiento_umbral(v, umbral_p95_s) for cfg, v in por_config.items() if v}

    anova = anova_factorial_log([{"configuracion": c["configuracion"], "n": c["n"], "segundos": c["p95"]}
                                  for c in corridas])

    todas_rechazan = all(comp["significativo"] for comp in comparacion_por_tamano) if comparacion_por_tamano else None
    todas_cumplen_umbral = all(d["p95_bajo_umbral"] for d in resultados_por_condicion) if resultados_por_condicion else None
    reduccion_90_en_max_n = None
    if tamanos:
        n_max = max(tamanos)
        reducciones_n_max = [c["reduccion_pct"] for c in comparacion_por_tamano if c["n"] == n_max]
        if reducciones_n_max:
            reduccion_90_en_max_n = all(r is not None and r >= 90 for r in reducciones_n_max)

    return _limpiar({
        "fuente": fuente, "n_corridas": len(corridas), "configuraciones": configuraciones,
        "tamanos": tamanos, "alfa": alfa, "umbral_p95_s": umbral_p95_s,
        "descriptiva": list(descriptiva_s.values()),
        "supuestos": {"normalidad": list(supuestos.values()), "homogeneidad_levene": homogeneidad},
        "comparaciones_globales": comparaciones_globales, "kruskal_wallis": kw,
        "resultados_por_condicion": resultados_por_condicion,
        "comparacion_por_tamano": comparacion_por_tamano,
        "correlacion_regresion": correlaciones, "cumplimiento_umbral": cumplimiento,
        "anova_factorial": anova,
        "conclusion": {
            "rechaza_h0_todos_los_tamanos": todas_rechazan,
            "cumple_umbral_p95_todas_las_configuraciones": todas_cumplen_umbral,
            "reduccion_90pct_en_n_maximo": reduccion_90_en_max_n,
            "nota": "La significancia se reporta junto al tamaño del efecto; "
                    "el criterio de cumplimiento del artículo es la reducción de p95 "
                    "frente a la línea base, no solo el valor p.",
        },
    })
