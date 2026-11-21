# Optimización de la infraestructura de laboratorios mediante servidor de caché y repositorio local (mirror)

Diplomado en Metodología Científica en Ingeniería de Sistemas · Módulo IV (Cloud Computing, DevOps y Arquitectura de Software) · UNAJMA

**Autores:** Jhamer Anderson Rojas Silva, Edwing Alcides Maquera Flores, Richard Carrion Abollaneda, Ruben Apaza Apaza y Norma Catacora Flores.

Repositorio del artículo y de su prototipo. El historial es la bitácora de la investigación: un commit por cambio, y nada entra a `main` sin PR.

## Entregas

| Etiqueta | Fecha | Contenido |
|---|---|---|
| `v0.1` | 13 nov. | Planes como propuesta, demostrador mínimo con dos modos, pruebas, despliegue en Vercel |
| `v0.2` | 18 nov. | Capas, base de datos, cuatro configuraciones, resumen, pruebas automáticas en cada PR |
| `v0.3` | 20 nov. | Paneles de Experimentos, Estadística (normalidad, Mann-Whitney, bootstrap, ANOVA factorial) y Rendimiento y calidad (ISO/IEC 25010) |
| `v1.0` | por confirmar | Medición en el laboratorio, artículo con resultados |

## Estructura

| Carpeta | Contenido |
|---|---|
| `api/` | Punto de entrada del servicio |
| `demostrador/` | Capas: controladores, servicios, repositorios y modelos |
| `public/` | Páginas: Sesiones (ejecutar y ver el resumen), Experimentos (diseño paramétrico), Estadística (pruebas sobre las sesiones reales) y Rendimiento y calidad (ISO/IEC 25010) |
| `scripts/` | `medir.py`/`analizar.py` (demostrador); `estacion_laboratorio.py`, `consolidar_sesion_laboratorio.py` e `inventario_estacion.py` (laboratorio real) |
| `tests/` | Pruebas automáticas; corren en cada PR |
| `supabase/migrations/` | Esquema de la base de datos |
| `docs/` | Planes de estructura, base de datos y medición; despliegue; ADR; documentos por sesión |
| `paper/` | Artículo (`articulo.md`, `Articulo_IMRyD.docx`) y figuras |
| `experimento/` | Ensayo con Docker Compose |
| `laboratorio/` | Configuración de Nginx (caché, mirror) y guía para medir en el laboratorio real |

## Configuraciones

El servicio ejecuta las cuatro configuraciones del artículo: `base`, `cache`, `mirror` y `ambos`. Se eligen con un código en el pedido o con la variable `CONFIGURACION`; el resto del código es el mismo. Variables de entorno y base de datos: `docs/DESPLIEGUE.md` y `.env.example`.

## Experimentos y Estadística

- **`/experimentos.html` → `POST /api/experimentos`:** corre un diseño factorial (tamaños × configuraciones) en memoria, con calentamiento descartado y orden aleatorizado por semilla. No guarda nada en la base; el panel estadístico se calcula sobre esas corridas y las descargas CSV/JSON se arman en el navegador.
- **`/estadistica.html` → `GET /api/estadistica`:** el mismo panel estadístico, pero sobre las sesiones reales guardadas (las que se ejecutan desde Sesiones).
- El panel incluye: descriptiva, normalidad (Jarque-Bera), homogeneidad de varianzas (Levene), Mann-Whitney y bootstrap de cada configuración frente a la línea base, correlación y regresión (N vs. tiempo), cumplimiento del umbral p95 declarado (t de una muestra + IC de Wilson) y ANOVA factorial sobre ln(tiempo). Implementado en `demostrador/services/estadistica.py` y `demostrador/services/experimento.py`.
- Con parámetros grandes (muchas corridas × tamaños altos) el experimento puede acercarse al límite de `maxDuration` de la función en Vercel (`vercel.json`); en el despliegue conviene mantener valores moderados.

## Rendimiento y calidad

- **`/calidad.html` → `POST /api/calidad/correccion`:** corrección funcional. Con un catálogo fijo, los aciertos y las salidas al origen de cada configuración son deterministas (`demostrador/services/correccion.py` los calcula a partir del modelo, no de otra implementación); la ruta compara lo observado contra lo esperado en N repeticiones.
- **`POST /api/calidad/benchmark`:** escalado con N. Mide tiempo de CPU y memoria pico por corrida y estima el exponente de complejidad empírica (pendiente log-log).
- **`GET /api/calidad/metricas-estaticas`:** complejidad ciclomática (McCabe) y anidamiento máximo por archivo, calculados con `ast` sobre el propio código — no es una estimación.
- **`GET /api/calidad/iso25010`:** tabla de características ISO/IEC 25010 con evidencia tomada del repositorio (conteo real de pruebas, workflows de CI presentes). Declara qué se midió, qué quedó parcial y qué no se evaluó.

## Ejecutar en local

```
python -m venv .venv
.venv\Scripts\activate            # Windows; en Linux o macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest
python -m uvicorn api.index:app --port 8000
```

Abrir http://127.0.0.1:8000. Sin `DATABASE_URL` usa SQLite local. Para medir, ver `docs/PLAN_MEDICION.md`.

## Medición en el laboratorio

- **`scripts/estacion_laboratorio.py`:** cliente de una estación real. Mismo enrutamiento que
  `demostrador/services/entrega.py` (`base`/`cache`/`mirror`/`ambos`), reloj monotónico, y detecta
  si una petición salió de verdad a origen leyendo `X-Cache-Status` (lo agrega `laboratorio/cache.conf`).
- **`scripts/consolidar_sesion_laboratorio.py`:** junta los archivos de todas las estaciones de una
  sesión en el formato crudo de `docs/PLAN_MEDICION.md` (el mismo `CAMPOS_CSV` que usa el demostrador),
  calculando `salidas_origen` a nivel de sesión.
- **`scripts/inventario_estacion.py`:** SO, paquetes (`apt`/`dpkg`) y hardware de una estación.
- **`laboratorio/`:** configuración real de Nginx para el proxy de caché y el mirror, y la guía de
  despliegue. Probado contra servidores HTTP locales, no contra hardware del laboratorio todavía.

## Qué es dato real y qué no

El demostrador y el ensayo usan un origen simulado: validan el procedimiento. Los resultados del artículo salen de la medición en el laboratorio.

## Convención de commits

`feat`, `fix`, `test`, `chore`, y `docs(sesion-0X)` o `docs(paper)` para documentos.

## Hoja de ruta

| Entrega | Actividad | Estado |
|---|---|---|
| v0.2 | Pruebas automáticas en cada PR, capas, modos mirror y ambos, base de datos | En curso |
| v0.2 | Ensayo con contenedores (`experimento/`) | Por validar |
| v0.3 | Panel de Experimentos (diseño factorial en memoria) | Hecho |
| v0.3 | Panel de Estadística (sobre sesiones reales guardadas) | Hecho |
| v0.3 | Rendimiento y calidad: ISO/IEC 25010, complejidad de código, benchmark de escalado | Hecho |
| v1.0 | Inventario del laboratorio: SO, paquetes y hardware | Script listo; falta correrlo en el laboratorio |
| v1.0 | Medición en el laboratorio y sección de resultados | Scripts y configuración de Nginx listos (`laboratorio/`); falta desplegar y medir de verdad |
| v1.0 | Registro de búsqueda y matriz de literatura consolidados | En curso |
