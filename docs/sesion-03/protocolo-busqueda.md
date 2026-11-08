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
