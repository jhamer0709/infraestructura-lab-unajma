# Plan de base de datos (PostgreSQL)

Estado: **propuesta para aprobar (v0.1). Todavía no se ha cambiado código.** En v0.1 los datos viven en el CSV crudo de `scripts/medir.py`. La base se implementa en v0.2.

## 1. Para qué

Guardar cada medición con su contexto, de modo que cualquier percentil se pueda recalcular desde las filas crudas. No se guardan promedios ni percentiles.

No se registran datos personales ni identificadores reales de equipos institucionales: la estación se guarda como un número de 1 a N.

## 2. Convenciones

Tomadas de las que mostró el docente en el taller; por confirmar con él.

| Regla | Detalle |
|---|---|
| Prefijo | Tablas con `t_`, en español, singular, minúsculas con `_` |
| Clave primaria | `id BIGINT GENERATED ALWAYS AS IDENTITY` |
| Identificador público | `uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid()` |
| Fechas | `TIMESTAMPTZ` en UTC |
| Tiempos medidos | `NUMERIC(10,4)` en segundos, nunca `float` |
| Borrado | Lógico, con `deleted_at` |
| Integridad | Claves foráneas con `ON DELETE RESTRICT`; `CHECK` en rangos |

Columnas estándar en todas las tablas: `id`, `uuid`, `created_at`, `updated_at`, `deleted_at`.

## 3. Tablas

| Tabla | Una fila es | Columnas propias |
|---|---|---|
| `t_configuracion` | Una de las cuatro configuraciones | `codigo` (base, cache, mirror, ambos), `usa_cache`, `usa_mirror` |
| `t_lista_paquete` | Una versión de la lista de paquetes | `version`, `descripcion` |
| `t_sesion` | Una sesión de preparación | `configuracion_id`, `lista_paquete_id`, `n_estaciones`, `numero_sesion`, `es_calentamiento`, `orden_ejecucion`, `entorno` (demostrador, ensayo, laboratorio), `iniciada_en` |
| `t_observacion` | Una estación en una sesión | `sesion_id`, `estacion`, `segundos`, `aciertos`, `errores` |
| `t_trafico_sesion` | El tráfico de salida de una sesión | `sesion_id`, `bytes_salida`, `instrumento` |

Relaciones: una configuración y una lista tienen muchas sesiones; una sesión tiene N observaciones y una fila de tráfico.

Restricciones: `n_estaciones` entre 1 y 30; `estacion` entre 1 y `n_estaciones`; `segundos` mayor que 0; `(sesion_id, estacion)` único.

## 4. Decisiones abiertas

- **Proveedor.** Supabase, como en el taller, u otro PostgreSQL gestionado. Se decide en v0.2 y se registra en un ADR.
- **Carga de datos.** Importar el CSV al terminar cada sesión, o escribir desde el servicio. Se prefiere importar: el CSV sigue siendo la fuente y la base no interviene durante la medición.
- **Datos del laboratorio.** Si se publican en una base en la nube, confirmar antes que no contienen información institucional.

## 5. Qué queda fuera

Usuarios, permisos y auditoría por usuario: el demostrador no tiene inicio de sesión.
