# Sesión 1 · Planteamiento

**Título de trabajo:** Optimización de la infraestructura de laboratorios mediante servidor de caché y repositorio local (mirror)

## Contexto
En los laboratorios de cómputo de la Escuela Profesional de Ingeniería de Sistemas (EPIS) de la UNAJMA, las sesiones prácticas de programación, compilación y desarrollo se ejecutan de forma concurrente en estaciones con limitaciones de hardware por obsolescencia. Al iniciar la práctica, todas las estaciones descargan de internet las mismas dependencias y paquetes (sistema, lenguajes, librerías, imágenes de contenedor) por el mismo enlace de salida.

## Brecha (observación preliminar, por validar en OE-1)
El tiempo de descarga y preparación del entorno alcanzaría unos 6 minutos por estación con 30 equipos concurrentes y el enlace de salida se saturaría hasta cerca del 90 %. Estas cifras provienen de la observación del autor, no de una medición registrada. El umbral operativo de referencia es 30 segundos, declarado antes de medir (no se atribuye a una fuente externa).

## Pregunta de investigación (plantilla de la Clase 02)
¿En qué medida un servidor de caché y repositorio local (mirror) reduce el tiempo p95 de preparación de entornos de desarrollo y el tráfico de salida frente al acceso directo a internet, en los laboratorios de cómputo de la EPIS-UNAJMA con 30 estaciones concurrentes?

| Pieza | En esta pregunta |
|---|---|
| Solución propuesta | Servidor de caché y repositorio local (mirror) |
| Variables medibles | Tiempo p95 de preparación; tráfico de salida |
| Línea base | Acceso directo a internet |
| Contexto y restricciones | Laboratorios EPIS-UNAJMA, 30 estaciones, hardware limitado, enlace limitado |
