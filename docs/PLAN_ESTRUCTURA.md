# Plan de estructura

Estado: **propuesta (v0.1)**. Lo marcado como v0.2 o v1.0 todavía no existe.

## 1. Qué es cada cosa

| Pieza | Para qué sirve | Dónde corre |
|---|---|---|
| Demostrador (`api/`, `public/`) | Validar el procedimiento: dos modos, caché frío, CSV crudo, p95 | Vercel y local |
| Ensayo con contenedores (`experimento/`) | Ensayar 30 clientes con enlace limitado antes del laboratorio | Local o CI (sin probar) |
| Medición real | Producir los resultados del artículo | Laboratorio EPIS-UNAJMA |

El demostrador y el ensayo usan datos sintéticos. Ningún número de ellos entra a la sección de resultados del artículo.

## 2. Carpetas

```
api/index.py          servicio: /api/paquete, /api/cache, /api/salud
public/index.html     página para lanzar una preparación y ver el p95
scripts/medir.py      runner: modos en orden aleatorio, calentamiento, CSV crudo
scripts/analizar.py   mediana y p95 por modo y N, desde el CSV
tests/                pruebas automáticas del servicio
docs/                 planes, ADR y documentos por sesión
paper/                artículo y figuras
experimento/          ensayo con Docker Compose
vercel.json           envía /api/* a la función; lo demás sale de public/
```

## 3. Evolución por entrega

| Entrega | Fecha | Estructura | Ramas |
|---|---|---|---|
| v0.1 | 13 nov. | Todo el servicio en `api/index.py`; caché en memoria | `dev` → `main` con PR |
| v0.2 | 18 nov. | Capas: controladores, servicios, repositorios; base de datos; modo `mirror` y `ambos` | se añade `release`; pruebas automáticas en cada PR |
| v1.0 | 20 nov. | Panel de resultados; análisis final | `dev` → `release` → `main` |

## 4. Reglas de trabajo

- Nada entra a `main` por push directo: siempre por PR desde `dev`.
- Un commit por cambio, con prefijo: `feat`, `fix`, `docs`, `test`, `chore`.
- Cada entrega se marca con una etiqueta (`v0.1`, `v0.2`, `v1.0`).
- Las configuraciones se eligen con una variable, nunca con ramas ni copias del código: así lo único que cambia entre mediciones es la intervención.

## 5. Correspondencia con el artículo

| Artículo | En el demostrador v0.1 |
|---|---|
| Línea base (acceso directo) | `modo=directo` |
| Caché bajo demanda | `modo=cache` |
| Mirror sincronizado, ambos | pendiente, v0.2 |
| Estaciones concurrentes N | `--n 1 10 30` en `medir.py` |
| Estado del caché: frío | `POST /api/cache/vaciar` antes de cada sesión |
| Lista de paquetes versionada | `VERSION_LISTA` en `api/index.py` |
| Tráfico de salida | `salidas_al_origen` (conteo, no GB) |

## 6. Límites declarados

- El origen y el enlace son simulados. El modelo supone que el enlace reparte su capacidad por igual entre descargas simultáneas; la reducción que muestra el demostrador es consecuencia de ese supuesto, no una medición.
- En Vercel el caché vive en la memoria de cada instancia. Con carga concurrente puede haber varias instancias y el conteo deja de ser exacto. La corrida de referencia del demostrador es la local.
