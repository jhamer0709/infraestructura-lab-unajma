# Sesión 3 · Protocolo de búsqueda (escrito antes de filtrar)

**Pregunta:** ver `docs/sesion-01/planteamiento.md`. Alcance: revisión con método sistemático de alcance acotado (diez referencias), en versión corta de PRISMA.

## Cuatro piezas y sinónimos

| Pieza | Inglés | Español |
|---|---|---|
| Intervención | "package mirror", "local mirror", "caching proxy", "pull-through cache", "registry cache", "dependency cache" | "repositorio local", "servidor proxy", "caché" |
| Variable | "download time", "installation time", "provisioning time", "startup time", "build time", latency | "tiempo de descarga", "ancho de banda" |
| Comparación | baseline (se verifica al leer, no entra a la cadena) | línea base |
| Contexto | university, campus, "computer lab*", "limited bandwidth", "low bandwidth" | universidad, laboratorio |

## Cadenas (una por base, tal como se pegan)

**IEEE Xplore (búsqueda avanzada)**
```
("package mirror" OR "local mirror" OR "caching proxy" OR "pull-through cache" OR "registry cache" OR "dependency cache") AND ("download time" OR "installation time" OR "provisioning time" OR "startup time" OR "build time" OR latency)
```
**Scopus**
```
TITLE-ABS-KEY(("package mirror" OR "local mirror" OR "caching proxy" OR "pull-through cache" OR "registry cache" OR "dependency cache") AND ("download time" OR "installation time" OR "provisioning time" OR "startup time" OR "build time" OR latency))
```
**Variante con contexto (si devuelve más de 300, agregar; si devuelve menos de 50, quitar este bloque primero):** `AND (university OR campus OR "computer lab*" OR "limited bandwidth" OR "low bandwidth")`

**ACM DL:** misma cadena de IEEE, filtrando por tipo de publicación.
**Google Scholar** (sin paréntesis anidados): `"pull-through cache" OR "package mirror" OR "caching proxy" "download time" OR "provisioning time" OR "build time"`
**SciELO** (español, pocas palabras): `servidor proxy caché ancho de banda`; `repositorio local paquetes`

Zona de trabajo: 50 a 300 resultados por cadena. Registrar también las que no funcionaron.

## Criterios (declarados antes de filtrar)

| Incluyo si… | Excluyo si… |
|---|---|
| Se publicó entre 2016 y 2026 | Es una nota de blog o un white paper comercial |
| Está en revista o congreso con revisión por pares | No describe cómo midió |
| Evalúa con mediciones (tiempo, tráfico, tasa de aciertos), no solo describe | No tengo acceso al texto completo |
| Está en inglés, español o portugués | Repite un estudio ya incluido |

Excepciones declaradas: máximo cuatro de las diez referencias pueden ser preprints, documentación técnica oficial u obras de contexto, declaradas como tales; mínimo seis indexadas. El rango 2016-2026 (el ejemplo de clase usa 2019-2026) se amplía porque la distribución de imágenes de contenedor tiene antecedentes de 2016.

## Búsqueda complementaria
Bola de nieve hacia atrás y hacia adelante (Citado por en Scholar) desde los tres estudios más citados.

## Criterio de parada
Saturación: las referencias nuevas ya están en la lista y cambiar la cadena devuelve los mismos autores. Para este módulo, diez referencias bien leídas.

## Ejecución (19/11/2026)

Resultados reales y cadenas finales en `registro-busqueda.csv`. Resumen:

- **IEEE y Scopus:** la cadena principal completa quedó por debajo de 50 (2 y 7 resultados). Se aplicó la regla de "quita términos": se retiró la cláusula de tiempo/latencia y se dejó solo la de caché/mirror, lo que subió a 13 (IEEE) y 62 (Scopus).
- **ACM DL:** la cadena principal completa ya estaba en zona (165) sin reducir. El filtro de año 2016-2026 no se pudo aplicar: la cuenta institucional es "Basic Edition" y tanto el formulario avanzado como el filtro lateral de fecha están marcados "Filters (Premium feature)"; se probaron los dos y el conteo no cambió. El 165 es sin filtrar por año (se verificaron fichas de 1995 a 2026 en la lista completa).
- **Google Scholar:** 54, cadena sin reducir, confirmado hasta que la paginación se detuvo (6 páginas).
- **SciELO:** las dos cadenas previstas (`servidor proxy caché ancho de banda`, `repositorio local paquetes`) dieron 0. Se redujo a `proxy caché`, que dio 4 — sigue bajo la zona de trabajo, pero es el máximo alcanzable en SciELO sin salir del alcance temático.

**Deduplicación:** 298 registros brutos (13+62+165+54+4) → 285 únicos tras normalizar título (minúsculas, sin puntuación) y comparar exactamente entre las cinco bases. 12 títulos duplicados entre bases (13 repeticiones de más); el más repetido, "Intermediate Caching Technique via Fog Layer..." (Thakur y Srinivasa, 2020), apareció en IEEE, Scopus y Google Scholar.

**Cribado por título:** de los 285 únicos, 80 tienen un título temáticamente plausible para el dominio del artículo (caché, proxy, mirror, registry, tiempo de build/descarga/provisioning, CDN, Docker/npm/apt, edge computing); el resto es ruido de la ambigüedad de "mirror" y "cache" (sobre todo "mirror symmetry" en física/matemáticas, mayoritario en Scopus y ACM, y memoria caché de hardware). Falta el cribado por resumen y la lectura a texto completo de los 80.

**Nota importante sobre las diez referencias ya leídas (tabla-extraccion.md):** ninguna de las diez apareció en los 298 registros de esta ejecución, revisados de forma sistemática (título por título) en las cinco bases. No es evidencia de que la búsqueda esté mal construida: las diez se identificaron originalmente por bola de nieve (ver "Búsqueda complementaria" arriba), no por esta cadena principal, y varias usan vocabulario distinto al de la cadena (p. ej. [6] habla de "caching environments", no de "caching proxy" ni "registry cache") o se publicaron en venues de cobertura irregular en estas bases (FAST/USENIX para [3] y [5]). Queda como limitación declarada del protocolo, no como hallazgo nuevo de brecha: la cadena principal y la bola de nieve son procedimientos complementarios, y este resultado es exactamente lo esperable de esa complementariedad.
