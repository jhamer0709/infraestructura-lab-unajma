# ADR-001 · Arquitectura de ejecución para el experimento de caché y mirror
**Fecha:** 12/11/2026 · **Estado:** Aceptada (se revisa si OE1 contradice que el cuello de botella es el enlace de salida)

## Contexto
Las 30 estaciones del laboratorio descargan las mismas dependencias por un único enlace. Observación preliminar (por validar en OE1): ~6 min de preparación y ~90 % de saturación del enlace. Umbral operativo de referencia: 30 s. Hipótesis: H1a (p95 −90 %) y H1b (tráfico −90 %).

## Decisión
Un nodo único dentro de la LAN del laboratorio con dos componentes activables por separado: proxy de caché bajo demanda y mirror sincronizado. Las estaciones se apuntan al nodo; el resto (hardware, lista de paquetes, enlace) queda fijo.

## Alternativas descartadas
- **Mirror en la nube:** no alivia el enlace de salida del campus; el tráfico sigue saliendo.
- **Caché entre estaciones (P2P, línea de EdgePier [8]):** no permite medir el mirror por separado y exige software en 30 estaciones.
- **Microservicios:** no aplica; el problema no es de escalado por partes ni de organización de equipos.

## Consecuencias
- A favor: control total del entorno; permite separar el efecto del caché y del mirror; el enlace es el único recurso compartido.
- En contra: el nodo es un punto único de falla durante la sesión.
- En contra: no se prueba elasticidad ni otro hardware; el resultado no generaliza a otro laboratorio.
- En contra: hay que mantener la sincronización del mirror y reservar disco.

## Pendiente
Las valoraciones de esfuerzo de la Tabla VI son estimaciones cualitativas del autor, no medidas.
