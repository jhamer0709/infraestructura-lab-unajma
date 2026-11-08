# Auditoría de la matriz original (Avance Sesión 01, versión 2)

Comparada con las listas de chequeo de las clases 02 y 03.

| # | Hallazgo | Regla de clase | Corrección aplicada |
|---|---|---|---|
| 1 | La variable dependiente usa «tiempo medio» | «Nunca usen el promedio»; se mide p95 o p99 | p95 como indicador principal y mediana de apoyo |
| 2 | Los indicadores de la V.I. (tasa de aciertos, GB ocupados, uptime) miden el mirror, no la variable independiente | La independiente es lo que se cambia y casi siempre tiene dos valores: con y sin | V.I. = acceso directo / con mirror; esos indicadores pasan a monitoreo del mecanismo y costo |
| 3 | El throughput de salida aparece como indicador de la V.I. y como variable dependiente en el texto | Cada variable tiene un solo rol | Tráfico de salida pasa a variable dependiente |
| 4 | Faltan variables de control y la columna de línea base | La tabla lleva variable, indicador, instrumento y línea base; sin control, la diferencia puede venir de otra causa | Se agregan control (hardware, 30 estaciones, lista de paquetes, SO, horario, enlace) y estado de la caché fría o tibia |
| 5 | La pregunta incluye «impacto sobre los equipos limitados», que ninguna variable ni objetivo mide | La pregunta nombra solución, variable, línea base y contexto, y el general responde lo que se preguntó | El hardware pasa a contexto y control; la pregunta se reescribe |
| 6 | La hipótesis tiene magnitud solo para el tiempo (70 %), no para el ancho de banda; se llama «general» | Plantilla con magnitud; H0 y H1 | H1a (70 %), H1b (90 %, justificado) y H0 |
| 7 | 70 % deja el tiempo en 108 s, sobre el umbral de 30 s; «estándar de la industria» sin fuente | Si no hay número verificable, es creencia | Umbral de 30 s declarado como operativo y marcado la decisión; cifras de brecha como preliminares |
| 8 | OE-1 «Diagnosticar» no fija entregable | Verbos con entregable | OE-1 mide la línea base, con 30 estaciones y 3 corridas o más |
| 9 | Referencias [1], [3], [4] no se pudieron verificar como están escritas | Mínimo seis indexadas y verificadas | Ver abajo |
| 10 | Dos capturas pegadas corresponden a otro tema (recibos en Python) | — | Solo se tomó su formato |

## Referencias de la versión original
- [2] Abbas et al., IEEE IoT J., 2018: existe como registro en IEEE Xplore y dblp. Se conserva.
- [1] «Edge computing: Vision, challenges, and roadmaps» (Dastjerdi y Buyya, 2016): no encontré ese título. Encontré «Edge Computing: Vision and Challenges» de Shi et al., IEEE IoT J., vol. 3, n.º 5, pp. 637–646; se usa esa.
- [3] «In-edge caching…» (COMST 2018) y [4] «Cooperative caching and data placement…» (IEEE Access 2017): no pude verificarlos. En arXiv, los autores de [4] tienen «Collaborative Multi-bitrate Video Caching and Processing in Mobile-Edge Computing Networks», que es otro título. Se retiran hasta confirmar en el sitio de la revista.
- [5] Mach y Becvar, COMST 2017: no se alcanzó a verificar en esta sesión. Si se conserva, confirmar el DOI en IEEE Xplore.
