Optimización de la infraestructura de laboratorios de cómputo mediante
un servidor de caché y repositorio local (mirror)

Jhamer Anderson Rojas Silva

*Diplomado en Metodología Científica en Ingeniería de Sistemas*

Universidad Nacional José María Arguedas

Andahuaylas, Perú

***Resumen***

**En los laboratorios de la Escuela Profesional de Ingeniería de
Sistemas las prácticas se ejecutan de forma concurrente en estaciones
con hardware limitado, y las 30 estaciones descargan las mismas
dependencias por un único enlace de salida. La observación preliminar
del autor indica unos 6 minutos de preparación por estación y una
saturación cercana al 90 % del enlace, cifras que se validarán en la
línea base. La literatura revisada coincide en que descargar paquetes
pesa en el arranque y en el build, y en que el caché reduce latencia o
duración en centros de datos e integración continua, pero ninguno de los
diez estudios incluidos lo mide en un laboratorio académico con enlace
limitado. Este trabajo mide el efecto de dos intervenciones separables,
un caché bajo demanda y un mirror sincronizado, con 30 estaciones
concurrentes, al menos tres corridas y condiciones controladas, y
declara de antemano los umbrales de reducción. \[Resultados pendientes:
sesión 7.\]**

***Palabras clave: servidor de caché, repositorio local, mirror, tiempo
de preparación de entornos, ancho de banda, laboratorios de cómputo***

<span class="smallcaps">I. Introducción</span>

*A. Contexto y problema*

La cercanía entre los datos y quien los consume es un principio conocido
para reducir latencia y uso del enlace \[1\], \[2\]. En un laboratorio
de cómputo ocurre lo contrario: al comenzar la práctica, 30 estaciones
piden por internet los mismos paquetes, librerías e imágenes. Descargar
paquetes representa el 76 % del tiempo de arranque de contenedores en un
benchmark de 57 aplicaciones \[3\], y la descarga de dependencias es el
19,5 % de la mediana del tiempo de build en 22,2 millones de
compilaciones de CI \[4\].

En la EPIS-UNAJMA el síntoma observado es una preparación de unos 6
minutos por estación con el enlace cerca del 90 % de saturación
(observación preliminar, por validar en OE1). El umbral operativo de
referencia es 30 segundos, declarado antes de medir. El problema no es
la lentitud en abstracto, sino una lentitud acotada y medible en un
momento concreto de la práctica.

*B. Pregunta de investigación*

¿En qué medida un servidor de caché y repositorio local (mirror) reduce
el tiempo p95 de preparación de entornos de desarrollo y el tráfico de
salida frente al acceso directo a internet, en los laboratorios de
cómputo de la EPIS-UNAJMA con 30 estaciones concurrentes?

*C. Objetivos*

*Objetivo general.* Evaluar en qué medida la implementación de un
servidor de caché y repositorio local (mirror) reduce el tiempo p95 de
preparación de entornos y el tráfico de salida frente al acceso directo
a internet, en los laboratorios de la EPIS-UNAJMA.

*OE1.* Medir la línea base de tiempo p95 de preparación, tráfico de
salida y tasa de error con 30 estaciones concurrentes, en al menos tres
corridas.

*OE2.* Implementar el caché bajo demanda (proxy de paquetes y caché de
descargas de imágenes) y medir su efecto frente a la línea base.

*OE3.* Implementar el mirror sincronizado de repositorios y medir su
efecto, solo y combinado con el caché.

*OE4.* Determinar, con pruebas estadísticas, si las reducciones alcanzan
los umbrales de H1a y H1b y cuánto aporta cada intervención.

*D. Hipótesis*

**H1a.** La mejor configuración (caché, mirror o ambos) reduce el tiempo
p95 de preparación por estación en al menos 70 % frente al acceso
directo a internet, con 30 estaciones concurrentes y condiciones
controladas.

**H1b.** La misma configuración reduce el tráfico de salida por sesión
práctica en al menos 90 %. Con caché tibia y 30 estaciones que piden el
mismo conjunto de paquetes, solo una descarga sale a internet: la
reducción teórica es 1 − 1/30 = 96,7 %.

**H0.** Ninguna configuración produce una diferencia significativa en el
tiempo p95 de preparación ni en el tráfico de salida.

Los umbrales quedan declarados antes de medir. Un umbral elegido después
de observar los resultados es un umbral elegido para aprobar, y
compromete la validez de la conclusión. Aviso de coherencia: 70 % sobre
360 s deja el p95 en 108 s; llegar a los 30 s de referencia exigiría
91,7 %.

*E. Variables operacionalizadas*

TABLA I

<span class="smallcaps">Variables del estudio</span>

| **Variable**                                     | **Tipo** | **Medida**               | **Instrumento**                        |
|--------------------------------------------------|----------|--------------------------|----------------------------------------|
| Caché bajo demanda                               | Indep.   | Nominal (con/sin)        | Configuración del proxy y del registro |
| Mirror sincronizado                              | Indep.   | Nominal (con/sin)        | Repositorio local sincronizado         |
| Tiempo de preparación                            | Dep.     | s, mediana y p95         | Script cronometrado por estación       |
| Tráfico de salida                                | Dep.     | GB por sesión; Mbps pico | SNMP o vnstat en el router             |
| Tasa de error                                    | Dep.     | % (razón)                | Registros del script                   |
| Estaciones concurrentes                          | Moder.   | 1, 10, 30                | Carga declarada                        |
| Estado del caché                                 | Control  | Fría / tibia             | Vaciado previo                         |
| Hardware, lista de paquetes, SO, horario, enlace | Control  | Declarados, fijos        | Inventario y lista versionada          |

Las dos primeras filas separan las intervenciones, a diferencia del
planteamiento original, que las agrupaba en una sola variable. La línea
base es el acceso directo a internet, con valores preliminares de 6 min
y 90 % del enlace por validar en OE1.

<span class="smallcaps">II. Estado del arte</span>

De diez estudios incluidos, ninguno evalúa un caché o mirror local de
paquetes en un laboratorio académico, y solo uno \[8\] considera un
enlace limitado, en entorno emulado.

*A. Protocolo de búsqueda*

La búsqueda se realizó el \[fecha\] en IEEE Xplore, Scopus, ACM Digital
Library, Google Scholar y SciELO, con el periodo 2016–2026. Los
criterios se declararon antes de filtrar.

*Inclusión.* Publicado entre 2016 y 2026; en revista o congreso con
revisión por pares; reporta mediciones de tiempo, tráfico o tasa de
aciertos; en inglés, español o portugués; texto completo disponible.
Hasta cuatro de las diez referencias pueden ser preprints, documentación
técnica o textos de contexto, declarados como tales.

*Exclusión.* Nota de blog o documento comercial; no describe cómo midió;
sin acceso al texto completo; duplicado de un estudio ya incluido.

TABLA II

<span class="smallcaps">Registro de búsqueda</span>

| **Base**    | **Cadena**                                      | **Filtros** | **Result.** |
|-------------|-------------------------------------------------|-------------|-------------|
| IEEE Xplore | Cadena de tres conceptos con OR entre sinónimos | 2016–2026   | \[n\]       |
| Scopus      | TITLE-ABS-KEY, misma cadena                     | 2016–2026   | \[n\]       |
| ACM DL      | La misma cadena                                 | 2016–2026   | \[n\]       |
| Scholar     | La misma, un nivel de paréntesis                | desde 2016  | \[n\]       |
| SciELO      | servidor proxy caché ancho de banda             | sin filtro  | \[n\]       |

Cadenas completas en el repositorio. Agregar aquí, como filas, las
búsquedas que no funcionaron: explican por qué la cadena final quedó
como quedó. La búsqueda se complementa con bola de nieve hacia atrás y
hacia adelante desde los estudios más relevantes. Se utilizó una
herramienta de IA generativa para ampliar sinónimos, traducir términos,
armar las cadenas y apoyar la redacción; la búsqueda, la selección de
fuentes y la verificación de cada referencia fueron realizadas por el
autor \[confirmar esto último antes de entregar: abrir el DOI o la
fuente de cada referencia\].

*B. Selección*

TABLA III

<span class="smallcaps">Proceso de selección</span>

| **Etapa**                          | **Estudios** |
|------------------------------------|--------------|
| Identificados en las cinco bases   | \[n\]        |
| Tras eliminar duplicados           | \[n\]        |
| Pasan cribado por título y resumen | \[n\]        |
| Leídos a texto completo            | \[n\]        |
| Incluidos en la revisión           | 10           |

Los descartes por título y resumen se registran con su motivo. Se leyó y
descartó a Weeraddana et al. (FSE 2024) por no medir el tiempo de
descarga.

*C. Síntesis comparativa*

Las dimensiones se derivan de la pregunta: la intervención, la variable
medida, la línea base, los datos y el contexto. Los datos provienen de
resúmenes y extractos; falta la lectura a texto completo.

TABLA IV

<span class="smallcaps">Matriz de literatura</span>

| **Est.** | **Caché o mirror** | **Tiempo** | **Base** | **Reales** | **Lab. o enlace limitado** |
|----------|--------------------|------------|----------|------------|----------------------------|
| \[3\]    | Variante           | Sí         | Sí       | Sí         | No                         |
| \[4\]    | No                 | Parcial    | No       | Sí         | No                         |
| \[5\]    | Sí                 | Sí         | Sí       | Trazas     | No                         |
| \[6\]    | Sí                 | Sí         | Sí       | Sí         | No                         |
| \[7\]    | Sí                 | Sí         | Sí       | Sí         | No                         |
| \[8\]    | Variante           | Sí         | Sí       | No         | Parcial                    |
| \[9\]    | No                 | No         | No       | Sí         | No                         |
| \[10\]   | Sí                 | No         | No       | No         | No                         |

Ninguna fila presenta valor afirmativo en las cinco dimensiones. Los
estudios \[5\]–\[7\] cachean, miden y tienen línea base con datos
reales, pero en centros de datos o integración continua. El estudio
\[8\] es el único con enlace limitado, y lo emula. Los trabajos \[1\] y
\[2\] son conceptuales y no entran en la matriz.

*D. Brecha identificada*

La literatura revisada coincide en que la descarga de paquetes y
dependencias pesa en el arranque y en el build \[3\], \[4\] y en que el
caché reduce latencia o duración \[5\]–\[7\], \[9\]. De los diez
estudios incluidos, ninguno evalúa un caché o mirror local de paquetes
en un laboratorio académico, y el único con enlace limitado lo emula
\[8\]. No se halló evidencia del efecto de cada intervención, y de su
combinación, sobre el tiempo de preparación en un laboratorio real con
línea base declarada. Este trabajo mide ese efecto en la EPIS-UNAJMA,
con umbrales declarados de antemano.

El alcance de esta afirmación es el del protocolo de II.A: cinco bases,
periodo 2016–2026, los criterios listados y las cadenas del repositorio.
No se afirma que no exista tal evidencia, sino que no se halló dentro de
ese alcance.

<span class="smallcaps">III. Propuesta</span>

*A. Modelo conceptual*

La intervención se modela como dos variables independientes separables,
no como una sola: el caché bajo demanda y el mirror sincronizado. Con
dos niveles cada una resultan cuatro combinaciones: línea base, caché,
mirror y ambos. Medir por intervención es lo que permite atribuir una
reducción de 360 s a 40 s a una de ellas, y no a un conjunto.

<img src="media/image2.png" style="width:3.3in;height:2.20651in" />

Fig. 1. Modelo conceptual: dos variables independientes, dos
dependientes y una moderadora.

Cada flecha lleva el signo esperado. La flecha entre ambas
intervenciones lleva signo de interrogación: no se sabe si el mirror
aporta reducción adicional con el caché ya activo, y esa es una de las
preguntas que el experimento responde en OE3 y OE4. La moderadora, el
número de estaciones concurrentes, importa porque el beneficio del caché
depende de cuántas estaciones piden lo mismo \[8\].

*B. Arquitectura que mide las flechas*

La arquitectura propuesta añade un único componente en la LAN y deja
fijo todo lo demás: es lo que permite atribuir el efecto. Cada medición
cuelga de un objetivo: el script cronometrado por estación y el contador
de tráfico del router sirven a OE1 y OE4.

<img src="media/image3.png" style="width:2.9in;height:3.17219in" />

Fig. 2. Arquitectura actual y propuesta. En azul, lo único que cambia.

El nodo debe estar dentro de la LAN: un mirror en la nube no reduce el
uso del enlace de salida de la universidad, que es el cuello de botella.

*C. Trazabilidad con los objetivos*

TABLA V

<span class="smallcaps">Objetivos específicos sobre el modelo</span>

| **Objetivo** | **Dónde está en el modelo**                    |
|--------------|------------------------------------------------|
| OE1          | La línea base, antes de intervenir             |
| OE2          | La flecha del caché bajo demanda               |
| OE3          | La flecha del mirror y la flecha conjunta (?)  |
| OE4          | Cómo se mide cada flecha, no una flecha propia |

Toda flecha del modelo tiene objetivo asignado. El último objetivo es el
método con que se miden las demás.

<span class="smallcaps">Referencias</span>

*Nota: las referencias \[1\]–\[5\], \[7\], \[9\] y \[10\] están
verificadas con autores, medio y año en páginas de la editorial, del
grupo autor o de arXiv. En \[6\] falta confirmar el DOI y el número de
la revista; en \[8\], el medio de publicación. Falta la lectura a texto
completo.*

\[1\] W. Shi, J. Cao, Q. Zhang, Y. Li y L. Xu, «Edge computing: Vision
and challenges», IEEE Internet Things J., vol. 3, n.º 5, pp. 637–646,
oct. 2016. doi: 10.1109/JIOT.2016.2579198

\[2\] N. Abbas, Y. Zhang, A. Taherkordi y T. Skeie, «Mobile edge
computing: A survey», IEEE Internet Things J., vol. 5, n.º 1, pp.
450–465, feb. 2018. doi: 10.1109/JIOT.2017.2750180

\[3\] T. Harter, B. Salmon, R. Liu, A. C. Arpaci-Dusseau y R. H.
Arpaci-Dusseau, «Slacker: Fast distribution with lazy Docker
containers», en Proc. 14th USENIX Conf. File and Storage Technologies
(FAST ’16), Santa Clara, CA, 2016, pp. 181–195.

\[4\] K. Gallaba, M. Lamothe y S. McIntosh, «Lessons from eight years of
operational data from a continuous integration service: An exploratory
case study of CircleCI», en Proc. 44th Int. Conf. Software Engineering
(ICSE ’22), Pittsburgh, PA, 2022. doi: 10.1145/3510003.3510211

\[5\] A. Anwar et al., «Improving Docker registry design based on
production workload analysis», en Proc. 16th USENIX Conf. File and
Storage Technologies (FAST ’18), Oakland, CA, 2018, pp. 265–278.

\[6\] K. Gallaba, J. Ewart, Y. Junqueira y S. McIntosh, «Accelerating
continuous integration by caching environments and inferring
dependencies», IEEE Trans. Softw. Eng., vol. 48, n.º 8, pp. 2040–2052,
2022. — verificar DOI y número.

\[7\] T. A. Ghaleb, D. A. da Costa y Y. Zou, «The promise and reality of
continuous integration caching: An empirical study of Travis CI builds»,
arXiv:2601.19146, ene. 2026 (preprint).

\[8\] S. Becker, F. Schmidt y O. Kao, «EdgePier: P2P-based container
image distribution in edge computing environments», arXiv:2109.12983,
sep. 2021. doi: 10.1109/IPCCC51483.2021.9679447 — verificar medio.

\[9\] N. Zhao et al., «Large-scale analysis of the Docker Hub dataset»,
en Proc. IEEE Int. Conf. Cluster Computing (CLUSTER), Albuquerque, NM,
2019. doi: 10.1109/CLUSTER.2019.8891000

\[10\] Python Packaging Authority, «Package index mirrors and caches»,
Python Packaging User Guide. \[En línea\]. Disponible en:
https://packaging.python.org/en/latest/guides/index-mirrors-and-caches/
(consultado el 7 de nov. de 2026).
