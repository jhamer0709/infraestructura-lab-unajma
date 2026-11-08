---
title: "Optimización de la infraestructura de laboratorios de cómputo mediante un servidor de caché y repositorio local (mirror) para reducir el tiempo de preparación de entornos"
author: "Jhamer Anderson Rojas Silva"
---

*Diplomado en Metodología Científica en Ingeniería de Sistemas, Universidad Nacional José María Arguedas, Andahuaylas, Perú*

**Resumen.** En los laboratorios de la Escuela Profesional de Ingeniería de Sistemas las prácticas se ejecutan de forma concurrente en estaciones con hardware limitado, y todas descargan las mismas dependencias por un único enlace de salida. La observación preliminar del autor indica unos 6 minutos de preparación por estación con 30 equipos y una saturación cercana al 90 % del enlace, cifras que se validarán en la medición de línea base. La literatura revisada coincide en que la descarga de paquetes pesa en el tiempo de arranque y de build [3], [4], y en que el caché reduce latencia o duración en entornos de centro de datos y de integración continua [5]–[7], pero ninguno de los diez estudios revisados lo mide en un laboratorio universitario con enlace limitado. Este trabajo evalúa, con un diseño antes y después de al menos tres corridas, 30 estaciones y condiciones controladas, si un servidor de caché y repositorio local (mirror) reduce el tiempo p95 de preparación en al menos 70 % y el tráfico de salida en al menos 90 %. [Resultados pendientes: sesión 7.]

**Palabras clave:** servidor de caché, repositorio local, mirror, tiempo de preparación, ancho de banda, laboratorios de cómputo

# I. Introducción

## A. Contexto y problema

La cercanía entre los datos y quien los consume es un principio conocido para reducir latencia y uso del enlace [1], [2]. En un laboratorio de cómputo ocurre lo contrario: al comenzar la práctica, 30 estaciones piden por internet los mismos paquetes, librerías e imágenes. Descargar paquetes representa el 76 % del tiempo de arranque de contenedores en un benchmark de 57 aplicaciones [3], y la descarga de dependencias es el 19,5 % de la mediana del tiempo de build en 22,2 millones de compilaciones de CI [4]. En la EPIS-UNAJMA el síntoma observado es una preparación de unos 6 minutos por estación con saturación cercana al 90 % del enlace (observación preliminar, por validar en OE-1). El umbral operativo de referencia es de 30 segundos, declarado antes de medir.

## B. Pregunta de investigación

¿En qué medida un servidor de caché y repositorio local (mirror) reduce el tiempo p95 de preparación de entornos de desarrollo y el tráfico de salida frente al acceso directo a internet, en los laboratorios de cómputo de la EPIS-UNAJMA con 30 estaciones concurrentes?

## C. Objetivos

**Objetivo general.** Evaluar en qué medida la implementación de un servidor de caché y repositorio local (mirror) reduce el tiempo p95 de preparación de entornos y el tráfico de salida frente al acceso directo a internet, en los laboratorios de la EPIS-UNAJMA.

- **OE1.** Medir la línea base de tiempo p95 de preparación, tráfico de salida y tasa de error con 30 estaciones concurrentes, en al menos tres corridas.
- **OE2.** Diseñar e implementar el nodo mirror/caché contenedorizado para la distribución centralizada de paquetes y dependencias.
- **OE3.** Comparar ambas condiciones bajo la misma carga y las mismas condiciones controladas, con caché fría y caché tibia.
- **OE4.** Determinar, con pruebas estadísticas, si las reducciones alcanzan los umbrales de H1a y H1b.

## D. Hipótesis

**H1a.** El mirror reduce el tiempo p95 de preparación del entorno por estación en al menos 70 % frente al acceso directo a internet, con 30 estaciones concurrentes y condiciones controladas.

**H1b.** El mirror reduce el tráfico de salida hacia internet por sesión práctica en al menos 90 % frente al acceso directo. Con caché tibia y 30 estaciones que piden el mismo conjunto de paquetes, solo una descarga sale a internet, lo que da una reducción teórica de 96,7 %.

**H0.** El mirror no produce una diferencia significativa en el tiempo p95 de preparación ni en el tráfico de salida.

Los umbrales se declaran antes de medir. Un umbral elegido después de ver el resultado compromete la validez de la conclusión. El experimento recoge evidencia para rechazar H0; si no alcanza, también es un resultado.

## E. Variables operacionalizadas

*Tabla I. Variables del estudio*

| Variable | Tipo | Medida | Instrumento | Línea base |
|:---|:---|:---|:---|:---|
| Acceso a paquetes (directo / con mirror) | Indep. | Nominal | Configuración de apt, pip, npm y Docker | Acceso directo |
| Tiempo de preparación, p95 (s) y mediana | Dep. | Razón | Script cronometrado; Locust o JMeter | Pre-intervención, 3 corridas o más |
| Tráfico de salida (Mbps pico; GB por sesión) | Dep. | Razón | SNMP o vnstat; Prometheus y Grafana | Pre-intervención, 3 corridas o más |
| Tasa de error o timeout (%) | Dep. | Razón | Registros del script | Pre-intervención |
| Tasa de aciertos de caché (%) | Monitoreo | Razón | Registros del proxy | No aplica |
| Estado de la caché (fría / tibia) | Control | Nominal | Vaciado previo | Fría |
| Hardware, 30 estaciones, lista de paquetes, SO, horario, enlace | Control | — | Inventario y lista versionada | Fijo |

# II. Estado del arte

## A. Protocolo de búsqueda

La revisión sigue un método sistemático de alcance acotado (versión corta de PRISMA). La pregunta se dividió en intervención, variable, comparación y contexto, con sinónimos en inglés y español. Las cadenas se aplican en IEEE Xplore, Scopus, ACM DL, Google Scholar y SciELO, con operadores OR entre sinónimos y AND entre conceptos. Los criterios se definieron antes de filtrar. Se incluyen estudios de 2016 a 2026, en revista o congreso con revisión por pares, que evalúen con mediciones y estén en inglés, español o portugués. Se excluyen notas de blog, white papers comerciales, estudios sin descripción de medición, sin texto completo o repetidos. Hasta cuatro de las diez referencias pueden ser preprints, documentación técnica o textos de contexto, declarados como tales.

## B. Embudo

*Tabla II. Flujo de selección (completar con los números del registro de búsqueda)*

| Etapa | N |
|:---|:---|
| Identificados por la cadena, en las bases | [completar] |
| Tras quitar duplicados | [completar] |
| Pasan título y resumen | [completar] |
| Leídos a texto completo | [completar] |
| Incluidos | 10 |

## C. Estudios revisados

Sobre el costo de la descarga: [3] muestra que descargar paquetes es el 76 % del arranque de contenedores y que solo se lee el 6,4 % de lo descargado, y [4] ubica la descarga de dependencias en 19,5 % de la mediana del tiempo de build. Sobre el efecto del caché: [5] analiza 75 días de trazas de registros Docker de IBM y reporta, en simulación, respuestas de 0,008 s con memoria frente a 0,07 s del almacenamiento de objetos para capas menores a 1 MB, con tasas de acierto de hasta 78 %; [6] cachea entornos de CI y acelera al menos el 87,9 % de 14.364 builds históricas; [7] encuentra, en 513.384 builds de Travis CI, que cerca de un tercio de los proyectos reduce su tiempo de build, con costos de mantenimiento (27 % tiene artefactos obsoletos), y es un preprint. Sobre enlaces limitados: [8] propone distribuir imágenes entre pares y reporta hasta 65 % menos de aprovisionamiento a 20 Mbps en un entorno emulado, pero a 500 Mbps el registro base fue más rápido, de modo que el beneficio depende del enlace. [9] caracteriza 167 TB de Docker Hub y halla que solo el 3 % de los archivos es único, lo que sustenta el potencial del caché. La guía técnica de la PyPA [10] documenta herramientas de mirror y caché para PyPI y afirma que aceleran la instalación y permiten trabajar sin conexión, sin aportar cifras.

*Tabla III. Matriz de literatura*

| Estudio | ¿Caché o mirror? | ¿Mide tiempo? | ¿Línea base? | ¿Lab. académico o enlace limitado? | Datos |
|:---|:---|:---|:---|:---|:---|
| [3] | Variante | Sí | Sí | No | Reales, laboratorio |
| [4] | No | Parcial | No aplica | No | Reales |
| [5] | Sí | Sí | Sí | No | Trazas, simulación |
| [6] | Sí | Sí | Sí | No | Reales |
| [7] | Sí | Sí | Sí | No | Reales (preprint) |
| [8] | Variante | Sí | Sí | Parcial | Emulados |
| [9] | No | No | No | No | Reales |
| [10] | Sí | No | No | No | Ninguno |

## D. Brecha

La literatura revisada coincide en que la descarga de paquetes y dependencias pesa en el tiempo de arranque y de build [3], [4] y en que el caché reduce latencia o duración [5]–[7]. De los diez estudios revisados, ninguno evalúa un mirror o caché local de paquetes en un laboratorio universitario, y los que usan un enlace limitado lo hacen en entornos emulados [8]. Ninguno reporta mediciones de tiempo de preparación con línea base en un laboratorio académico con enlace de salida limitado. Este trabajo mide ese efecto en los laboratorios de la EPIS-UNAJMA, declarando entorno, carga, número de corridas y umbrales antes de medir.

*Limitación de esta sección:* los resultados provienen de resúmenes y extractos; antes de entregar, las diez referencias deben leerse a texto completo y confirmarse la indexación en Scopus o WoS y el cuartil en Scimago.

# Referencias

[1] W. Shi, J. Cao, Q. Zhang, Y. Li, and L. Xu, "Edge computing: Vision and challenges," *IEEE Internet Things J.*, vol. 3, no. 5, pp. 637–646, Oct. 2016, doi: 10.1109/JIOT.2016.2579198.

[2] N. Abbas, Y. Zhang, A. Taherkordi, and T. Skeie, "Mobile edge computing: A survey," *IEEE Internet Things J.*, vol. 5, no. 1, pp. 450–465, Feb. 2018, doi: 10.1109/JIOT.2017.2750180.

[3] T. Harter, B. Salmon, R. Liu, A. C. Arpaci-Dusseau, and R. H. Arpaci-Dusseau, "Slacker: Fast distribution with lazy Docker containers," in *Proc. 14th USENIX Conf. File and Storage Technologies (FAST '16)*, Santa Clara, CA, USA, Feb. 2016, pp. 181–195.

[4] K. Gallaba, M. Lamothe, and S. McIntosh, "Lessons from eight years of operational data from a continuous integration service: An exploratory case study of CircleCI," in *Proc. 44th Int. Conf. Software Engineering (ICSE '22)*, Pittsburgh, PA, USA, May 2022, doi: 10.1145/3510003.3510211.

[5] A. Anwar *et al.*, "Improving Docker registry design based on production workload analysis," in *Proc. 16th USENIX Conf. File and Storage Technologies (FAST '18)*, Oakland, CA, USA, Feb. 2018, pp. 265–278.

[6] K. Gallaba, J. Ewart, Y. Junqueira, and S. McIntosh, "Accelerating continuous integration by caching environments and inferring dependencies," *IEEE Trans. Softw. Eng.*, vol. 48, no. 8, pp. 2040–2052, 2022. [DOI y número por confirmar.]

[7] T. A. Ghaleb, D. A. da Costa, and Y. Zou, "The promise and reality of continuous integration caching: An empirical study of Travis CI builds," arXiv:2601.19146, Jan. 2026 (preprint).

[8] S. Becker, F. Schmidt, and O. Kao, "EdgePier: P2P-based container image distribution in edge computing environments," arXiv:2109.12983, Sep. 2021, doi: 10.1109/IPCCC51483.2021.9679447. [Confirmar medio de publicación.]

[9] N. Zhao *et al.*, "Large-scale analysis of the Docker Hub dataset," in *Proc. IEEE Int. Conf. Cluster Computing (CLUSTER)*, Albuquerque, NM, USA, Sep. 2019, doi: 10.1109/CLUSTER.2019.8891000.

[10] Python Packaging Authority, "Package index mirrors and caches," *Python Packaging User Guide*. [Online]. Available: https://packaging.python.org/en/latest/guides/index-mirrors-and-caches/ (accessed Nov. 7, 2026).
