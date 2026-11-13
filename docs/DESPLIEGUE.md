# Despliegue

## 1. Flujo de ramas

```
dev  ──PR──▶  release  ──PR──▶  main
```

| Rama | Para qué | Despliegue en Vercel |
|---|---|---|
| `dev` | Trabajo diario | Vista previa por cada PR |
| `release` | Versión candidata: se prueba completa antes de publicar | Vista previa |
| `main` | Lo publicado | Producción |

En cada PR corren las pruebas (`.github/workflows/pruebas.yml`). No se fusiona con pruebas en rojo.

## 2. Variables de entorno

| Variable | Para qué | Valor por defecto |
|---|---|---|
| `DATABASE_URL` | Conexión a PostgreSQL | SQLite local |
| `CONFIGURACION` | Configuración cuando el pedido no indica una | `base` |
| `ORIGEN_RETARDO_MS` | Tiempo del origen simulado para un paquete de peso 1 | `50` |
| `ENTORNO` | Etiqueta guardada con cada sesión | `demostrador` |

En Vercel: Settings → Environment Variables. Después de cambiarlas hay que volver a desplegar.

## 3. Base de datos en Supabase

1. Crear un proyecto en Supabase y guardar la contraseña de la base.
2. En SQL Editor, pegar y ejecutar `supabase/migrations/0001_esquema.sql`.
3. En Connect, copiar la cadena **Transaction pooler** (puerto 6543) y reemplazar `[YOUR-PASSWORD]`.
4. En Vercel, crear la variable `DATABASE_URL` con esa cadena, para Production y Preview.
5. Volver a desplegar y ejecutar una sesión desde la página.
6. En Supabase, Table Editor: comprobar que `t_sesion` y `t_observacion` tienen filas.

La cadena de conexión contiene la contraseña: no va al repositorio, a capturas ni a chats.

## 4. Mismo código, una sola base

Todas las configuraciones corren sobre el mismo despliegue, el mismo código y la misma base. Lo único que cambia es el código de configuración del pedido. Si cada configuración tuviera su propio despliegue o su propia base, una diferencia de datos o de región se confundiría con el efecto de la intervención.

Para fijar una configuración por despliegue (por ejemplo, un entorno solo con `base` y otro solo con `ambos`) basta dar a cada uno un valor distinto de `CONFIGURACION` y la misma `DATABASE_URL`.

## 5. Límites del despliegue

- Una sesión se ejecuta completa dentro de una sola invocación, con un máximo de 60 s (`vercel.json`). Con los valores por defecto, la más larga (línea base, N = 30) dura cerca de 7 s.
- Sin `DATABASE_URL`, las sesiones se guardan en un archivo temporal de la instancia y se pierden.
- El primer pedido tras un rato sin uso tarda más (arranque en frío). Ese tiempo no entra en `segundos`, que se mide dentro de la sesión.
