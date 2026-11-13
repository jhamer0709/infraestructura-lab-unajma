# Plan de estructura

Estado: **implementado en v0.2**. Lo marcado como v1.0 todavía no existe.

## 1. Qué es cada cosa

| Pieza | Para qué sirve | Dónde corre |
|---|---|---|
| Demostrador (`api/`, `demostrador/`, `public/`) | Validar el procedimiento: cuatro configuraciones, caché frío, datos crudos, p95 | Vercel y local |
| Ensayo con contenedores (`experimento/`) | Ensayar 30 clientes con enlace limitado antes del laboratorio | Local o CI (por validar) |
| Medición real | Producir los resultados del artículo | Laboratorio EPIS-UNAJMA |

El demostrador y el ensayo usan datos sintéticos. Ningún número de ellos entra a la sección de resultados del artículo.

## 2. Capas

```
api/index.py                    punto de entrada (Vercel y uvicorn)
demostrador/
  app.py                        arma la aplicación: une las capas
  config.py                     variables de entorno
  models.py                     tablas (SQLAlchemy)
  controllers/sesiones.py       rutas HTTP: validan y delegan
  services/
    origen.py                   origen y enlace simulados; lista de paquetes
    entrega.py                  las cuatro configuraciones, una clase cada una
    medicion.py                 ejecuta una sesión, la guarda y la resume
    estadistica.py              mediana y p95
  repositories/
    base_datos.py               conexión: PostgreSQL o SQLite
    sesiones.py                 lectura y escritura de sesiones
public/index.html               página: ejecutar una sesión y ver el resumen
scripts/medir.py, analizar.py   runner y análisis desde el CSV crudo
tests/                          pruebas automáticas
supabase/migrations/            esquema SQL
```

Regla de dependencias: controladores → servicios → repositorios. Un controlador no toca la base; un repositorio no conoce HTTP.

Solo `api/index.py` está dentro de `api/`, para que Vercel despliegue una única función.

## 3. Cómo se elige la configuración

Las cuatro configuraciones del artículo son cuatro clases con la misma interfaz (`services/entrega.py`). Una función elige la clase a partir de un código (`base`, `cache`, `mirror`, `ambos`), que llega en el pedido o, si falta, en la variable de entorno `CONFIGURACION`. El resto del código es idéntico entre configuraciones: lo único que cambia entre mediciones es la intervención.

## 4. Rutas

| Ruta | Qué hace |
|---|---|
| `GET /api/salud` | Versión del servicio y de la lista de paquetes |
| `GET /api/configuraciones` | Configuraciones disponibles y la que rige por defecto |
| `POST /api/sesiones` | Ejecuta una sesión con N estaciones y la guarda |
| `GET /api/resumen` | Mediana, p95 y reducción por configuración y N |
| `GET /api/observaciones.csv` | Datos crudos: una fila por estación y sesión |

## 5. Evolución por entrega

| Entrega | Estructura | Ramas |
|---|---|---|
| v0.1 | Todo el servicio en `api/index.py`; caché en memoria; dos configuraciones | `dev` → `main` con PR |
| v0.2 | Capas; base de datos; cuatro configuraciones; resumen; pruebas automáticas en cada PR | `dev` → `release` → `main` |
| v1.0 | Datos del laboratorio cargados; análisis final | igual |

## 6. Reglas de trabajo

- Nada entra a `main` ni a `release` por push directo: siempre por PR.
- Un commit por cambio, con prefijo: `feat`, `fix`, `docs`, `test`, `chore`, `refactor`, `ci`.
- Cada entrega se marca con una etiqueta (`v0.1`, `v0.2`, `v1.0`).
- Las pruebas corren solas en cada PR; no se fusiona con pruebas en rojo.

## 7. Correspondencia con el artículo

| Artículo | En el demostrador |
|---|---|
| Línea base, caché, mirror, ambos | `base`, `cache`, `mirror`, `ambos` |
| Estaciones concurrentes N | campo `n` del pedido (1 a 30) |
| Estado del caché: frío | cada sesión crea un caché vacío |
| Lista de paquetes versionada | `VERSION_LISTA` y `PAQUETES` |
| Tiempo de preparación por estación | `t_observacion.segundos` |
| Tráfico de salida | `t_sesion.salidas_origen` (conteo); `bytes_salida` queda para el laboratorio |
| Sincronización del mirror, fuera de la sesión | `t_sesion.sincronizacion_mirror`, reportada aparte |

## 8. Supuestos y límites del modelo

- El enlace reparte su capacidad por igual entre descargas simultáneas.
- La entrega desde la LAN cuesta el 2 % del tiempo del origen.
- El mirror contiene los paquetes de repositorio, no las imágenes de contenedor; por eso `mirror` y `ambos` dan resultados distintos.
- Las reducciones que muestra el demostrador son consecuencia de estos supuestos, no mediciones.
