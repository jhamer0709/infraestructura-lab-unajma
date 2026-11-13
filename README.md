# Optimización de la infraestructura de laboratorios mediante servidor de caché y repositorio local (mirror)

Diplomado en Metodología Científica en Ingeniería de Sistemas · Módulo IV (Cloud Computing, DevOps y Arquitectura de Software) · UNAJMA

Repositorio del artículo y de su prototipo. El historial es la bitácora de la investigación: un commit por cambio, y nada entra a `main` sin PR.

## Entregas

| Etiqueta | Fecha | Contenido |
|---|---|---|
| `v0.1` | 13 nov. | Planes como propuesta, demostrador mínimo con dos modos, pruebas, despliegue en Vercel |
| `v0.2` | 18 nov. | Capas, base de datos, cuatro configuraciones, resumen, pruebas automáticas en cada PR |
| `v1.0` | 20 nov. | Panel de resultados, análisis final, artículo con resultados |

## Estructura

| Carpeta | Contenido |
|---|---|
| `api/` | Punto de entrada del servicio |
| `demostrador/` | Capas: controladores, servicios, repositorios y modelos |
| `public/` | Página: ejecutar una sesión y ver el resumen |
| `scripts/` | `medir.py` (runner) y `analizar.py` (mediana y p95 desde el CSV crudo) |
| `tests/` | Pruebas automáticas; corren en cada PR |
| `supabase/migrations/` | Esquema de la base de datos |
| `docs/` | Planes de estructura, base de datos y medición; despliegue; ADR; documentos por sesión |
| `paper/` | Artículo (`articulo.md`, `Articulo_IMRyD.docx`) y figuras |
| `experimento/` | Ensayo con Docker Compose |

## Configuraciones

El servicio ejecuta las cuatro configuraciones del artículo: `base`, `cache`, `mirror` y `ambos`. Se eligen con un código en el pedido o con la variable `CONFIGURACION`; el resto del código es el mismo. Variables de entorno y base de datos: `docs/DESPLIEGUE.md` y `.env.example`.

## Ejecutar en local

```
python -m venv .venv
.venv\Scripts\activate            # Windows; en Linux o macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest
python -m uvicorn api.index:app --port 8000
```

Abrir http://127.0.0.1:8000. Sin `DATABASE_URL` usa SQLite local. Para medir, ver `docs/PLAN_MEDICION.md`.

## Qué es dato real y qué no

El demostrador y el ensayo usan un origen simulado: validan el procedimiento. Los resultados del artículo salen de la medición en el laboratorio.

## Convención de commits

`feat`, `fix`, `test`, `chore`, y `docs(sesion-0X)` o `docs(paper)` para documentos.

## Hoja de ruta

| Entrega | Actividad | Estado |
|---|---|---|
| v0.2 | Pruebas automáticas en cada PR, capas, modos mirror y ambos, base de datos | En curso |
| v0.2 | Ensayo con contenedores (`experimento/`) | Por validar |
| v1.0 | Inventario del laboratorio: SO, paquetes y hardware | Programado |
| v1.0 | Medición en el laboratorio y sección de resultados | Programado |
| v1.0 | Registro de búsqueda y matriz de literatura consolidados | En curso |
