# Sesión 2 · Variables, objetivos e hipótesis

## Objetivo general
Evaluar en qué medida la implementación de un servidor de caché y repositorio local (mirror) reduce el tiempo p95 de preparación de entornos y el tráfico de salida frente al acceso directo a internet, en los laboratorios de la EPIS-UNAJMA.

## Objetivos específicos
- **OE-1.** Medir la línea base de tiempo p95 de preparación, tráfico de salida y tasa de error con 30 estaciones concurrentes, en al menos tres corridas.
- **OE-2.** Diseñar e implementar el nodo mirror/caché contenedorizado para la distribución centralizada de paquetes y dependencias.
- **OE-3.** Comparar ambas condiciones (acceso directo y con mirror) bajo la misma carga y las mismas condiciones controladas, con caché fría y caché tibia.
- **OE-4.** Determinar, con pruebas estadísticas, si las reducciones alcanzan los umbrales de H1a y H1b.

Prueba rápida: cumplir OE-1 a OE-4 basta para cumplir el general.

## Hipótesis
- **H1a.** El mirror reduce el tiempo p95 de preparación del entorno por estación en al menos 70 % frente al acceso directo a internet, con 30 estaciones concurrentes y condiciones controladas.
- **H1b.** El mirror reduce el tráfico de salida hacia internet por sesión práctica en al menos 90 % frente al acceso directo. Justificación: si las 30 estaciones piden el mismo conjunto de paquetes, con caché tibia solo una descarga sale a internet, lo que da una reducción teórica de 1 - 1/30 = 96,7 %.
- **H0.** El mirror no produce una diferencia significativa en el tiempo p95 de preparación ni en el tráfico de salida.

Aviso de coherencia: una reducción de 70 % sobre 360 s deja el p95 en 108 s, todavía por encima del umbral operativo de 30 s. Llegar a 30 s exigiría una reducción de 91,7 %. Decidir si el umbral de 30 s es meta deseable o parte de la hipótesis.

## Tabla de variables (Clase 02: variable · indicador · instrumento · línea base)

| Variable | Tipo | Medida | Instrumento | Línea base |
|---|---|---|---|---|
| Acceso a paquetes (directo / con mirror) | Independiente | Nominal, 2 niveles | Configuración de apt, pip, npm y Docker hacia internet o hacia el mirror | Acceso directo a internet |
| Tiempo de preparación por estación, p95 (s) y mediana | Dependiente | Razón | Script cronometrado por estación; Locust o JMeter para concurrencia | Pre-intervención, 3 corridas o más (preliminar: ~360 s) |
| Tráfico de salida (Mbps pico; GB por sesión) | Dependiente | Razón | SNMP o vnstat en el router; Prometheus y Grafana | Pre-intervención, 3 corridas o más (preliminar: ~90 % del enlace) |
| Tasa de error o timeout (%) | Dependiente secundaria | Razón | Registros del script | Pre-intervención |
| Tasa de aciertos de caché (%) | Monitoreo del mecanismo | Razón | Registros del proxy o repositorio | No aplica (0 % sin mirror) |
| Capacidad ocupada del mirror (GB) y latencia local (ms) | Costo del mirror | Razón | df y du; cURL | No aplica |
| Estado de la caché (fría / tibia) | Control, variado a propósito | Nominal | Procedimiento de vaciado antes de la corrida | Fría |
| Hardware, N.º de estaciones (30), lista de paquetes y versiones, SO, horario, capacidad del enlace | Control, fijo | — | Inventario y lista versionada en el repositorio | Fijo |
