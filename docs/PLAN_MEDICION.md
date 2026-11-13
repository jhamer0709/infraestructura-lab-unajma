# Plan de medición

Estado: **propuesta (v0.1)**. Describe cómo se mide; coincide con la Tabla VII y la sección III.E del artículo.

## 1. Qué se compara

| Variable | Valores |
|---|---|
| Configuración | línea base, caché, mirror, ambos (en v0.1 solo las dos primeras) |
| Estaciones concurrentes N | 1, 10, 30 |
| Controles | lista de paquetes versionada, hardware, SO, horario, enlace, caché frío al inicio |

## 2. Muestra

| N | Sesiones por configuración | Uso |
|---|---|---|
| 30 | 5 como objetivo, 3 como mínimo | Contraste de H1a y H1b |
| 10 | 3 | Descriptivo |
| 1 | 5 | Descriptivo |

La unidad de la prueba es la sesión, no la estación: las estaciones de una sesión comparten enlace y caché. Con 3 sesiones por configuración el resultado se reporta como descriptivo.

## 3. Protocolo de una sesión

1. Reconstruir el entorno desde la lista versionada y verificar la configuración activa.
2. Sesión de calentamiento, que se descarta y se anota.
3. Vaciar el caché.
4. Medir.
5. Guardar los datos crudos: una fila por estación.
6. Calcular los percentiles al final, desde el CSV.

Las configuraciones se ejecutan en orden aleatorio; el orden queda registrado.

## 4. Formato del CSV crudo

`fecha_utc, lista, modo, n, sesion, estacion, segundos, aciertos, errores`

Nunca se guarda un promedio. El archivo no se edita a mano.

## 5. Estadísticos

Mediana, p95 y dispersión, por sesión y agrupados. Reducción porcentual del p95 frente a la línea base del mismo N. Criterio de éxito: reducción de al menos 90 % en N = 30 (declarado antes de medir).

## 6. Cómo se ejecuta en el demostrador

```
python -m uvicorn api.index:app --port 8000
python scripts/medir.py --url http://127.0.0.1:8000 --n 1 10 30 --sesiones 5
python scripts/analizar.py datos/medicion.csv
```

## 7. Qué falta para el laboratorio

- Script cronometrado por estación con reloj monotónico (hoy el runner mide desde un solo equipo).
- Contador de tráfico en el router, en GB por sesión.
- Versiones reales de SO, paquetes y hardware.
- Confirmar cuántas sesiones con N = 30 permite el laboratorio.
