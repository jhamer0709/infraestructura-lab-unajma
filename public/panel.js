/* Dibuja el panel estadístico devuelto por /api/experimentos o /api/estadistica.
 * Compartido entre experimentos.html y estadistica.html: el objeto `panel`
 * tiene la misma forma venga de donde venga (ver demostrador/services/estadistica.py:bateria). */

/* fetch que espera JSON y da un mensaje legible si el servidor devolvió otra
 * cosa (por ejemplo la página de error de Vercel cuando la función se pasó
 * del tiempo límite, que no es JSON). */
async function fetchJSON(url, opciones) {
  const r = await fetch(url, opciones);
  const texto = await r.text();
  let datos;
  try {
    datos = JSON.parse(texto);
  } catch {
    throw new Error(r.ok
      ? "La respuesta no es JSON (" + texto.slice(0, 120) + ")"
      : `HTTP ${r.status}: la función tardó demasiado o falló antes de responder. ` +
        "Prueba con menos corridas, tamaños más chicos o un retardo de origen menor.");
  }
  if (!r.ok) throw new Error(datos.detail || `HTTP ${r.status}`);
  return datos;
}

const fmt = (v, d = 3) => (v === null || v === undefined ? "–" : Number(v).toFixed(d));
const pct = (v) => (v === null || v === undefined ? "–" : Number(v).toFixed(1) + " %");
const sino = (v) => (v === null || v === undefined ? "–" : v ? "✓" : "✗");
const pformat = (v) => (v === null || v === undefined ? "–" : v < 0.001 ? "< 0,001" : v.toFixed(4));

function tabla(cabeceras, filas) {
  return `<table><thead><tr>${cabeceras.map((c) => `<th>${c}</th>`).join("")}</tr></thead>
    <tbody>${filas.length ? filas.join("") : `<tr><td colspan="${cabeceras.length}">Sin datos.</td></tr>`}</tbody></table>`;
}

function renderPanel(contenedorId, panel) {
  const el = document.getElementById(contenedorId);
  if (!panel || !panel.n_corridas) {
    el.innerHTML = `<p class="nota">${panel && panel.fuente ? panel.fuente + ": " : ""}sin corridas todavía.</p>`;
    return;
  }

  const descriptiva = tabla(
    ["Motor", "N", "Mediana", "P90", "P95", "P99", "Media", "Desv.", "IC media", "Mín.", "Máx."],
    panel.descriptiva.map((d) => `<tr><td><span class="pill">${d.motor}</span></td><td>${d.n}</td>
      <td>${fmt(d.mediana)}</td><td>${fmt(d.p90)}</td><td>${fmt(d.p95)}</td><td>${fmt(d.p99)}</td>
      <td>${fmt(d.media)}</td><td>${fmt(d.desv)}</td><td>[${fmt(d.ic_media[0])} ; ${fmt(d.ic_media[1])}]</td>
      <td>${fmt(d.min)}</td><td>${fmt(d.max)}</td></tr>`));

  const normalidad = tabla(
    ["Motor", "N", "Asimetría", "Curtosis exc.", "JB", "p", "Normal", "Decisión"],
    panel.supuestos.normalidad.map((s) => `<tr><td><span class="pill">${s.motor}</span></td><td>${s.n}</td>
      <td>${fmt(s.asimetria, 2)}</td><td>${fmt(s.curtosis_exc, 2)}</td><td>${fmt(s.jb, 2)}</td>
      <td>${pformat(s.p)}</td><td>${sino(s.normal)}</td>
      <td>${s.p === null ? s.decision : (s.normal ? "No se rechaza normalidad" : "Se rechaza normalidad: usar pruebas no paramétricas")}
        ${s.p !== null ? `(p = ${pformat(s.p)} ${s.normal ? "≥" : "<"} α = ${panel.alfa}).` : ""}</td></tr>`));
  const lev = panel.supuestos.homogeneidad_levene;
  const levTxt = lev.p === null ? lev.decision
    : `Levene: F = ${fmt(lev.f, 2)} (${lev.gl[0]}, ${lev.gl[1]}) · p ${pformat(lev.p)} &nbsp; <strong>${lev.iguales ? "Varianzas iguales" : "Varianzas distintas: usar Welch o no paramétrica"} (p ${lev.p < panel.alfa ? "<" : "≥"} α = ${panel.alfa}).</strong>`;

  const resultadosCondicion = tabla(
    ["Motor", "N", "Sesiones", "Mediana", "P95", "P99", "Media", "Desv.", "IC media", "¿P95 ≤ umbral?"],
    panel.resultados_por_condicion.map((f) => `<tr><td><span class="pill">${f.motor}</span></td><td>#${f.n}</td>
      <td>${f.sesiones}</td><td>${fmt(f.mediana)}</td><td>${fmt(f.p95)}</td><td>${fmt(f.p99)}</td>
      <td>${fmt(f.media)}</td><td>${fmt(f.desv)}</td><td>[${fmt(f.ic_media[0])} ; ${fmt(f.ic_media[1])}]</td>
      <td>${sino(f.p95_bajo_umbral)}</td></tr>`));

  const comparacion = tabla(
    ["N", "Configuración", "Mediana base", "Mediana config.", "Δ mediana", "IC Δ (bootstrap)", "p (Mann-Whitney)",
     "Reducción", "Aceleración", "r (rank-biserial)", "¿Significativo?"],
    panel.comparacion_por_tamano.map((c) => `<tr><td>${c.n}</td><td><span class="pill">${c.configuracion}</span></td>
      <td>${fmt(c.mediana_base)}</td><td>${fmt(c.mediana_config)}</td><td>${fmt(c.delta_mediana)}</td>
      <td>[${fmt(c.ic_bootstrap[0])} ; ${fmt(c.ic_bootstrap[1])}]</td><td>${pformat(c.p)}</td>
      <td>${pct(c.reduccion_pct)}</td><td>${c.aceleracion ?? "–"}×</td><td>${fmt(c.r_rank_biserial, 2)}</td>
      <td>${c.identicas ? "idénticas" : sino(c.significativo)}</td></tr>`));

  const correlEntries = Object.entries(panel.correlacion_regresion || {});
  const correlacion = tabla(
    ["Motor", "N obs.", "Spearman ρ", "p", "Pearson r", "p", "Pendiente (s/estación)", "R²", "Decisión"],
    correlEntries.map(([motor, r]) => `<tr><td><span class="pill">${motor}</span></td><td>${r.n}</td>
      <td>${fmt(r.spearman.rho)}</td><td>${pformat(r.spearman.p)}</td><td>${fmt(r.pearson.r)}</td>
      <td>${pformat(r.pearson.p)}</td><td>${fmt(r.pendiente_s_por_unidad, 6)}</td><td>${fmt(r.r2)}</td>
      <td>${r.pearson.p < panel.alfa ? "El tiempo depende del tamaño de la sesión" : "Sin relación significativa"}
        (p ${r.pearson.p < panel.alfa ? "<" : "≥"} α = ${panel.alfa}).</td></tr>`));

  const cumplEntries = Object.entries(panel.cumplimiento_umbral || {});
  const cumplimiento = tabla(
    ["Motor", "N", "Dentro del umbral", "Proporción", "IC Wilson 95 %", "P95", "¿P95 ≤ umbral?", "t", "p (unilateral)", "Decisión"],
    cumplEntries.map(([motor, c]) => `<tr><td><span class="pill">${motor}</span></td><td>${c.n}</td>
      <td>${c.dentro_umbral}</td><td>${pct(c.proporcion)}</td><td>[${c.ic_wilson_95[0]} % ; ${c.ic_wilson_95[1]} %]</td>
      <td>${fmt(c.p95)}</td><td>${sino(c.p95_bajo_umbral)}</td><td>${fmt(c.t, 3) ?? "–"}</td>
      <td>${pformat(c.p_unilateral)}</td><td>${c.decision}</td></tr>`));

  const anova = tabla(
    ["Fuente", "SC", "GL", "CM", "F", "p", "η²"],
    (panel.anova_factorial || []).map((a) => `<tr><td>${a.fuente}</td><td>${fmt(a.sc, 4)}</td><td>${a.gl}</td>
      <td>${fmt(a.cm, 4)}</td><td>${a.f === null ? "–" : fmt(a.f, 2)}</td><td>${pformat(a.p)}</td>
      <td>${a.eta2 === null ? "–" : fmt(a.eta2, 3)}</td></tr>`));

  const c = panel.conclusion || {};
  const conclusionFilas = [
    ["¿Se rechaza H0 (no hay diferencia) en todos los tamaños?", c.rechaza_h0_todos_los_tamanos],
    ["¿Todas las configuraciones cumplen p95 ≤ umbral en todos los tamaños?", c.cumple_umbral_p95_todas_las_configuraciones],
    ["¿La reducción de p95 alcanza 90 % en el tamaño máximo (criterio del artículo, H1a/H1b)?", c.reduccion_90pct_en_n_maximo],
  ].map(([t, v]) => `<tr><td>${t}</td><td>${v === null ? "–" : (v ? "Sí" : "No")}</td></tr>`);

  el.innerHTML = `
    <div class="tarjeta"><h3>Descriptiva (s)</h3>
      <p class="nota">Fuente: ${panel.fuente} · ${panel.n_corridas} corridas · α = ${panel.alfa}</p>
      ${descriptiva}</div>

    <div class="tarjeta"><h3>1. Supuestos</h3>
      <p class="nota">Normalidad (Jarque-Bera, H0: los datos son normales) y homogeneidad de varianzas (Levene/Brown-Forsythe, H0: varianzas iguales).</p>
      ${normalidad}<p class="nota">${levTxt}</p></div>

    <div class="tarjeta"><h3>2. Comparación frente a la línea base</h3>
      <p class="nota">H0: no hay diferencia en el tiempo de preparación. Prueba recomendada según los supuestos: Mann-Whitney (no se cumplen los supuestos paramétricos en general).</p>
      ${comparacion}</div>

    <div class="tarjeta"><h3>3. Tamaño de la sesión y tiempo</h3>
      <p class="nota">Correlación (Spearman, Pearson) y regresión lineal tiempo ~ N estaciones. Requiere sesiones de distinto tamaño.</p>
      ${correlacion}</div>

    <div class="tarjeta"><h3>4. Cumplimiento del umbral (${fmt(panel.umbral_p95_s, 2)} s)</h3>
      <p class="nota">H0: la media ≥ umbral; H1: la media &lt; umbral (t de una muestra, unilateral). Se reporta además p95 y la proporción de corridas dentro del umbral con IC de Wilson.</p>
      ${cumplimiento}</div>

    <div class="tarjeta"><h3>5. Tabla de resultados por condición (s)</h3>${resultadosCondicion}</div>

    <div class="tarjeta"><h3>ANOVA factorial (ln(tiempo))</h3>${anova}
      <p class="nota">Complementario: la interacción Configuración × N indica si la ventaja de cada configuración crece con el tamaño de la sesión.</p></div>

    <div class="tarjeta"><h3>Conclusión automática</h3>
      ${tabla(["Pregunta", "Respuesta"], conclusionFilas)}
      <p class="nota">${c.nota || ""}</p></div>`;
}

/* Arma y descarga un CSV en el navegador a partir de una lista de objetos. */
function descargarCSV(nombre, filas, campos) {
  if (!filas || !filas.length) return;
  const cab = campos.join(",");
  const cuerpo = filas.map((f) => campos.map((c) => JSON.stringify(f[c] ?? "")).join(",")).join("\n");
  const blob = new Blob([cab + "\n" + cuerpo], { type: "text/csv;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = nombre;
  a.click();
  URL.revokeObjectURL(a.href);
}
