# Medición real en el laboratorio EPIS-UNAJMA

Esto es lo que falta de `docs/PLAN_MEDICION.md` sección 7, ya implementado:
un cliente por estación con reloj monotónico que escribe el mismo formato
crudo que usa el resto del proyecto. Lo que falta todavía es desplegarlo en
el laboratorio real y ejecutarlo: nada de esto corrió contra hardware real,
solo contra servidores HTTP locales en este entorno (ver los mensajes de
commit de `scripts/estacion_laboratorio.py` y
`scripts/consolidar_sesion_laboratorio.py`).

## 1. Qué hay que desplegar

| Pieza | Dónde | Con qué |
|---|---|---|
| Caché | Un host de la LAN | `cache.conf` (Nginx), editando `<ORIGEN_REAL>` |
| Mirror | Otro host de la LAN (o el mismo) | `mirror.conf` (Nginx), con los 4 paquetes espejables copiados a `/var/www/mirror` |
| Origen | Fuera de la LAN | El repositorio o mirror externo real que se esté comparando (no hace falta montar nada: ya existe) |

`base` no necesita caché ni mirror: todas las estaciones van directo al origen real.

## 2. Por estación

```
python scripts/inventario_estacion.py --salida resultados/inventario/<estacion>.json
python scripts/estacion_laboratorio.py \
    --configuracion <base|cache|mirror|ambos> --estacion <nombre> \
    --origen <url-origen-real> \
    --cache <url-proxy-cache>      # si la configuración usa caché
    --mirror <url-mirror-local>    # si la configuración usa mirror
    --salida resultados/<sesion>/<estacion>.json
```

El inventario se corre una vez por estación (o de nuevo si algo cambia);
la medición, una vez por sesión y estación.

## 3. Por sesión (después de que todas las estaciones terminaron)

```
python scripts/consolidar_sesion_laboratorio.py \
    --entorno laboratorio-epis --lista <version-de-la-lista> --n <estaciones> \
    --calentamiento 0 --sincronizacion-mirror-s <segundos, 0 si no aplica> \
    --salida datos/medicion_laboratorio.csv \
    resultados/<sesion>/*.json
```

Repetir con `--calentamiento 1` para la sesión de calentamiento (se guarda
marcada, no entra al análisis: `scripts/analizar.py` ya la descarta).

`salidas_origen` y `sincronizacion_mirror` son valores de la SESIÓN completa,
no de cada estación (sección 4 del plan): el script los calcula sumando las
estaciones, no hay que calcularlos a mano.

## 4. Analizar

```
python scripts/analizar.py datos/medicion_laboratorio.csv
```

Mismo analizador que ya usa el demostrador: compara mediana, p95 y reducción
frente a la línea base del mismo N.

## 5. Qué falta confirmar antes de medir en serio

- Cuántas sesiones con N = 30 permite el laboratorio (PLAN_MEDICION.md: 5 como
  objetivo, 3 como mínimo).
- El contador de tráfico del router, en GB por sesión (no lo cubre nada de
  aquí: es una lectura manual o del propio router).
- Que `<ORIGEN_REAL>` en `cache.conf` apunte a algo que de verdad represente
  "internet" para los cinco paquetes del artículo, y que los 4 espejables
  tengan copia real en `/var/www/mirror` antes de medir `mirror`/`ambos`.
