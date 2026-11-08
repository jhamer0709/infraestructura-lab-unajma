# Tabla de extracción (10 referencias)

Estado de verificación: autores, medio, año y páginas o DOI se confirmaron en páginas de la editorial, del grupo autor o de arXiv. Los resultados salen del resumen o de extractos consultados. **Falta la pasada 2 (texto completo) por el autor antes de entregar.**

| N.º | Cita corta | Problema que aborda | Qué propone | Cómo lo evaluó | Resultado principal | Limitaciones (mías, a confirmar) | Para qué me sirve | ¿Seria? |
|---|---|---|---|---|---|---|---|---|
| [1] | Shi et al., 2016 | Latencia y uso de red al depender de la nube | Visión del cómputo en el borde | Conceptual | Marco de desafíos | Sin mediciones | Marco conceptual de cercanía de datos | IEEE IoT J (Scimago: confirmar cuartil) |
| [2] | Abbas et al., 2018 | Panorama de MEC | Revisión de arquitectura y casos | Revisión | Taxonomía | Sin mediciones; móvil | Contexto | IEEE IoT J (confirmar) |
| [3] | Harter et al., 2016 | Arranque lento de contenedores | Slacker, carga perezosa de imágenes | HelloBench, 57 aplicaciones | Descargar paquetes es 76 % del arranque; solo se lee el 6,4 % de lo descargado; mejora de 5x en despliegue | Datacenter; almacenamiento compartido | Justifica que la descarga domina el tiempo de preparación | FAST (USENIX), revisión por pares |
| [4] | Gallaba, Lamothe y McIntosh, 2022 | Cómo se usa el tiempo en CI | Estudio de 22,2 millones de compilaciones (CircleCI) | Análisis de datos operativos | La descarga de dependencias es 19,5 % de la mediana del tiempo de build | No intervienen; no es laboratorio | Evidencia real del peso de las dependencias | ICSE '22 (ACM) |
| [5] | Anwar et al., 2018 | Diseño del registro Docker | Caché de capas y precarga | 75 días de trazas de IBM; simulación | Con memoria, respuesta de 0,008 s frente a 0,07 s de Swift en capas menores a 1 MB; aciertos hasta 78 % | Simulación sobre trazas; datacenter | Referencia de efecto de caché sobre latencia y de tasa de aciertos | FAST (USENIX) |
| [6] | Gallaba et al., 2022 | Builds de CI lentos | Kotinos: caché de entornos e inferencia de dependencias | 14.364 builds históricas | Acelera al menos 87,9 % de las builds; 74 % de ellas ~2x | Entorno de CI, no de red | Base de método de comparación con histórico | IEEE TSE (Q1: confirmar) |
| [7] | Ghaleb, da Costa y Zou, 2026 | Adopción real del caché en CI | Estudio empírico en Travis CI | 513.384 builds, 1.279 proyectos | ~1/3 de proyectos reduce el build; 27 % tiene artefactos obsoletos | Preprint sin revisión; CI | Advierte costos de mantenimiento del caché | arXiv, preprint (declarar) |
| [8] | Becker, Schmidt y Kao, 2021 | Saturación del enlace al registro central en el borde | EdgePier, registro P2P sobre IPFS | 6 VM, tc-NetEm, 10 repeticiones | Hasta 65 % menos de aprovisionamiento a 20 Mbps; a 500 Mbps el registro base fue más rápido | Entorno emulado; edge | Antecedente más cercano: ancho de banda limitado y concurrencia; muestra que el beneficio depende del enlace | IEEE (DOI); venue por confirmar |
| [9] | Zhao et al., 2019 | Qué contienen los registros públicos | Análisis de Docker Hub | 167 TB de imágenes | Solo 3 % de los archivos es único | No mide tiempos | Sustenta el potencial de caché y deduplicación | IEEE CLUSTER |
| [10] | PyPA, guía técnica | Cómo montar mirrors y cachés de PyPI | Catálogo de herramientas (devpi, bandersnatch, etc.) | Ninguna | Declara que acelera instalaciones y permite trabajo sin conexión | Sin cifras | Respaldo técnico de la intervención en pip | Documentación oficial (declarar) |

**Candidato leído y descartado:** Weeraddana et al., FSE 2024 (DOI 10.1145/3660823). Mide builds desperdiciadas por dependencias no usadas, no el tiempo de descarga. Motivo de exclusión: no mide la variable.

Mínimo de indexadas: [1], [2], [4], [6], [9] y, a confirmar en Scopus o WoS, [3], [5], [8]. Preprint: [7]. Documentación técnica: [10].
