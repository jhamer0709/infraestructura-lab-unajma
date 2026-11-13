# ADR-002: la sesión se ejecuta en una sola invocación y se guarda en la base

Fecha: 12 de noviembre de 2026 · Estado: aceptada · Reemplaza la forma de medir de v0.1

## Contexto

En v0.1 la página lanzaba un pedido HTTP por paquete y por estación, y el caché y los contadores vivían en la memoria del servicio. Al probarlo en Vercel con 10 estaciones:

- En modo directo se contaron 45 salidas al origen; debían ser 50.
- En modo caché se contaron 10; debían ser 5.
- Los tiempos por estación salieron escalonados, no parejos como en local.

Causa: la plataforma reparte los pedidos concurrentes entre varias instancias, y cada una tenía su propio caché, su propio contador y su propio enlace simulado. El número dependía de cuántas instancias se levantaran, es decir, de algo ajeno a la intervención.

## Decisión

1. Una sesión completa (N estaciones, todos los paquetes) se ejecuta dentro de una sola invocación del servicio, con un estado creado para esa sesión.
2. Al terminar, la sesión y sus observaciones se escriben en PostgreSQL. El resumen y el CSV se calculan desde esas filas.

## Alternativas

| Opción | Corrige el conteo | Costo | Veredicto |
|---|---|---|---|
| A. Sesión en una invocación + base de datos | Sí | Bajo: una tabla de sesiones y otra de observaciones | Elegida |
| B. Caché y contadores en un almacén compartido (Redis) | Sí, si además se coordinan los candados entre instancias | Alto: otro servicio y bloqueo distribuido | Descartada |
| C. Mantener el estado en memoria | No | Ninguno | Descartada |

## Consecuencias

A favor:

- El resultado de una sesión no depende del número de instancias.
- Cada sesión queda guardada con su configuración, N, lista y entorno; todo percentil es recalculable.
- El caché parte frío en cada sesión por construcción, sin un paso manual de vaciado.

En contra:

- El tiempo ya no incluye el viaje por la red entre el navegador y el servicio. Para el demostrador es deseable; en el laboratorio el tiempo debe tomarse en cada estación, como indica el artículo.
- La duración de una sesión queda limitada por el tiempo máximo de una invocación (60 s).
- Las estaciones son tareas concurrentes de un mismo proceso, no equipos distintos: el modelo no reproduce diferencias de hardware entre estaciones.
- Se añade una dependencia externa (la base de datos) y una credencial que custodiar.
