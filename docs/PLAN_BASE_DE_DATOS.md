# Plan de base de datos (Supabase / PostgreSQL)

Estado: **implementado en v0.2.** Modelos en `demostrador/models.py`; esquema en `supabase/migrations/0001_esquema.sql`.

## 1. Para qué

Guardar cada sesión con su contexto, de modo que cualquier percentil se pueda recalcular desde las filas crudas. No se guardan promedios ni percentiles.

No se registran datos personales ni identificadores reales de equipos: la estación se guarda como un número de 1 a N.

## 2. Convenciones

| Regla | Detalle |
|---|---|
| Prefijo | Tablas con `t_`, en español, singular, minúsculas con `_` |
| Clave primaria | `id BIGINT GENERATED ALWAYS AS IDENTITY` |
| Identificador público | `uuid UUID NOT NULL UNIQUE`; es el que devuelve la API |
| Fechas | `TIMESTAMPTZ`, guardadas en UTC |
| Tiempos medidos | `NUMERIC(10,4)` en segundos, nunca `float` |
| Borrado | Lógico, con `deleted_at` |
| Integridad | Claves foráneas con `ON DELETE RESTRICT`; `CHECK` en rangos |

Columnas estándar en todas las tablas: `id`, `uuid`, `created_at`, `updated_at`, `deleted_at`.

## 3. Tablas

| Tabla | Una fila es | Columnas propias |
|---|---|---|
| `t_configuracion` | Una de las cuatro configuraciones | `codigo`, `usa_cache`, `usa_mirror` |
| `t_lista_paquete` | Una versión de la lista de paquetes | `version`, `descripcion` |
| `t_sesion` | Una sesión de preparación | `configuracion_id`, `lista_paquete_id`, `n_estaciones`, `es_calentamiento`, `entorno`, `salidas_origen`, `sincronizacion_mirror`, `bytes_salida`, `iniciada_en` |
| `t_observacion` | Una estación en una sesión | `sesion_id`, `estacion`, `segundos`, `aciertos`, `errores` |

Relaciones: una configuración y una lista tienen muchas sesiones; una sesión tiene N observaciones.

Restricciones: `n_estaciones` entre 1 y 30; `estacion` mayor o igual a 1; `segundos` mayor que 0; `(sesion_id, estacion)` único.

## 4. Cambios frente a la propuesta de v0.1

| Propuesta | Implementado | Motivo |
|---|---|---|
| Tabla `t_trafico_sesion` | Columnas `salidas_origen` y `bytes_salida` en `t_sesion` | Hay un solo valor de tráfico por sesión; una tabla aparte no aportaba |
| `numero_sesion`, `orden_ejecucion` | Se derivan del `id` y de `iniciada_en` | Evita guardar un dato que ya está implícito |
| Importar el CSV a la base | El servicio escribe la sesión al terminar | La escritura ocurre después de medir, no durante |

## 5. Conexión

- Con `DATABASE_URL`: PostgreSQL. En Supabase se usa el pooler de transacciones (puerto 6543).
- Sin `DATABASE_URL`: SQLite local (`demostrador.db`), para desarrollo y pruebas. En Vercel ese archivo vive en `/tmp` y se pierde al reiniciar la instancia; por eso producción necesita `DATABASE_URL`.

Las tablas y los catálogos se crean al arrancar si no existen. El archivo de migración permite crearlas a mano y activa RLS sin políticas: la API pública de Supabase no ve estas tablas.

## 6. Verificación

Probado contra PostgreSQL local: migración, escritura de sesiones, resumen y exportación. La conexión a través del pooler de Supabase se verifica al desplegar (ver `docs/DESPLIEGUE.md`).

## 7. Pendiente para v1.0

- Cargar las sesiones del laboratorio con `entorno = laboratorio` y `bytes_salida` real.
- Confirmar que los datos del laboratorio no contienen información institucional antes de subirlos a una base en la nube.
