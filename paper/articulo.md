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
un caché bajo demanda y un mirror sincronizado, con 30 estaciones concurrentes, cinco sesiones por configuración como objetivo (tres como mínimo) y condiciones controladas, y
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

Esto es el gap tecnológico: un problema de ingeniería que se cierra
construyendo. La brecha de investigación, lo que la literatura no midió,
se establece en II.D. El trabajo se ubica en el cruce de dos frentes:
Cloud (distribución de imágenes y paquetes) y DevOps (preparación de
entornos). La métrica principal es el p95 del tiempo de preparación,
junto con el tráfico de salida.

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
salida y tasa de error con 30 estaciones concurrentes, en cinco sesiones como objetivo y tres como mínimo.

*OE2.* Implementar el caché bajo demanda (proxy de paquetes y caché de
descargas de imágenes) y medir su efecto frente a la línea base.

*OE3.* Implementar el mirror sincronizado de repositorios y medir su
efecto, solo y combinado con el caché.

*OE4.* Determinar, con una prueba no paramétrica a nivel de sesión en N = 30, si las reducciones alcanzan
los umbrales de H1a y H1b y cuánto aporta cada intervención.

*D. Hipótesis*

**H1a.** La mejor configuración (caché, mirror o ambos) reduce el tiempo
p95 de preparación por estación en al menos 90 % frente al acceso
directo a internet, con 30 estaciones concurrentes y condiciones
controladas.

**H1b.** La misma configuración reduce el tráfico de salida por sesión
práctica en al menos 90 %. Con el caché frío al inicio de la sesión y 30 estaciones que piden el mismo conjunto de paquetes, solo una descarga sale a internet, siempre que el proxy retenga las peticiones concurrentes del mismo paquete hasta completar la primera: la reducción teórica es 1 − 1/30 = 96,7 %.

**H0.** Ninguna configuración produce una diferencia significativa en el
tiempo p95 de preparación ni en el tráfico de salida.

Los umbrales quedan declarados antes de medir. Un umbral elegido después
de observar los resultados es un umbral elegido para aprobar, y
compromete la validez de la conclusión. Coherencia con el umbral
operativo: 90 % sobre una línea base de 360 s deja el p95 en 36 s, cerca
de los 30 s de referencia, que se mantienen como meta operativa y no
como parte de la hipótesis.

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
| Estado del caché                                 | Control  | Fría al inicio             | Vaciado antes de cada sesión medida                         |
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
autor.

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
descarga. De las diez referencias, siete están indexadas: \[3\]–\[5\] y
\[9\] figuran como documentos en Scopus, y \[1\], \[2\] y \[6\] se
publicaron en revistas Q1 de Scimago en su año de publicación (2016,
2018 y 2022). \[7\] es un preprint, \[10\] es documentación técnica y
\[8\] no se confirmó en Scopus.

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
dos niveles cada una resultan cuatro configuraciones: línea base, caché,
mirror y ambos. Medir por intervención es lo que permite atribuir una
reducción de 360 s a 40 s a una de ellas, y no a un conjunto. La Fig. 1
muestra el modelo.

<img src="media/image2.png" style="width:3.3in;height:1.98366in" />

Fig. 1. Modelo conceptual: dos variables independientes, dos
dependientes, una moderadora y los controles fijos.

Cada flecha lleva el signo esperado. La flecha entre ambas
intervenciones lleva signo de interrogación: no se sabe si el mirror
aporta reducción adicional con el caché ya activo, y esa es una de las
preguntas que el experimento responde en OE3 y OE4. La moderadora, el
número de estaciones concurrentes, importa porque el beneficio del caché
depende de cuántas estaciones piden lo mismo \[8\]. Las variables de
control (caja gris) se mantienen fijas entre configuraciones.

*B. Trazabilidad con los objetivos*

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

*C. Arquitectura propuesta*

Se adopta un nodo único en la LAN del laboratorio porque el diagnóstico
preliminar localiza el cuello de botella en el enlace de salida
compartido (cerca del 90 % de saturación, por validar en OE1) y no en
las estaciones. Se evaluaron además un mirror alojado en la nube y un
caché distribuido entre las estaciones, descartados por los criterios de
la Tabla VI. La decisión mantiene fijos el hardware, la lista de
paquetes y el enlace, lo que permite atribuir las variaciones del tiempo
y del tráfico a las dos intervenciones. El registro completo de la
decisión (ADR-001) está en el repositorio.

<img src="media/image3.png" style="width:3in;height:2.32424in" />

Fig. 2. Vista de despliegue, actual y propuesta. Azul: lo que se
interviene; ámbar: dónde se mide; línea punteada: frontera del sistema.

La Fig. 2 responde tres preguntas: qué se cambia (el nodo en azul),
dónde se mide (en cada estación y en el router, en ámbar) y qué queda
fijo (el enlace, las estaciones y los repositorios oficiales, fuera de
la frontera y declarados). El nodo debe estar dentro de la LAN: un
mirror en la nube no reduce el uso del enlace de salida, que es el
cuello de botella.

<img src="media/image4.png" style="width:3in;height:2.70336in" />

Fig. 3. Vista de componentes del nodo en la LAN.

La Fig. 3 muestra dónde vive la lógica que se cambia: un enrutador envía
los repositorios espejados al mirror y el resto al proxy de caché, que
consulta a los repositorios oficiales solo si no tiene el paquete. El
mirror se sincroniza fuera de la sesión de medición.

TABLA VI

<span class="smallcaps">Decisión de arquitectura</span>

| **Criterio**                     | **A. Nodo en la LAN**              | **B. Mirror en la nube**                         | **C. Caché entre estaciones**                  |
|----------------------------------|------------------------------------|--------------------------------------------------|------------------------------------------------|
| Control del entorno              | Total: hardware propio             | Parcial: red y proveedor ajenos                  | Total, pero depende de estaciones encendidas   |
| ¿Aísla caché y mirror?           | Sí, se activan por separado        | Solo el mirror                                   | Solo el caché                                  |
| Efecto sobre el enlace de salida | Solo salen fallos y sincronización | No alivia: la descarga sigue saliendo del campus | Reduce repeticiones, con coordinación compleja |
| Esfuerzo de montaje              | Medio: un servidor                 | Bajo, con costo por uso                          | Alto: software en 30 estaciones                |
| Veredicto                        | Elegida                            | Descartada: no alivia el enlace                  | Descartada: no permite medir el mirror         |

Los valores de esfuerzo son una estimación cualitativa del autor. La
alternativa C se apoya en la línea de \[8\].

*D. Diseño experimental*

TABLA VII

<span class="smallcaps">Diseño experimental</span>

| **Elemento**       | **Definición**                                                                                                                              |
|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| Diseño             | Cuasi-experimental en un laboratorio: cuatro configuraciones medidas en las mismas condiciones                                              |
| Independientes     | Caché bajo demanda y mirror sincronizado (con / sin)                                                                                        |
| Dependientes       | Tiempo de preparación (s), medido en la estación; tráfico de salida (GB por sesión), medido en el router; tasa de error (%), medida secundaria sin hipótesis                                    |
| Moderadora         | Estaciones concurrentes N = 1, 10, 30                                                                                                       |
| Control            | Hardware, lista de paquetes versionada, SO y versiones, horario, enlace, caché vaciado al inicio                                            |
| Unidad de análisis | Una estación en una sesión de preparación                                                                                                   |
| Muestra            | Por configuración: N = 30, cinco sesiones como objetivo y tres como mínimo (150 o 90 observaciones por estación); N = 10, tres sesiones (30); N = 1, cinco sesiones (5). Total: 52 sesiones. Las hipótesis se contrastan solo en N = 30; N = 1 y N = 10 son descriptivos |
| Estadísticos       | Mediana, p95 y dispersión, por sesión y agrupados; prueba no paramétrica entre configuraciones con la sesión como unidad. Con cinco sesiones por configuración el contraste es posible; con tres, el resultado se reporta como descriptivo                                                                 |
| Criterio de éxito  | p95 y tráfico reducidos en al menos 90 % (H1a, H1b)                                                                                         |

Las configuraciones se miden en orden aleatorio y, cuando es posible, el
mismo día, para que la hora no se confunda con el tratamiento.

*E. Instrumentación y protocolo*

El tiempo se toma en cada estación con un script y reloj monotónico,
desde el inicio de la preparación hasta que el entorno queda listo. No
se mide en el nodo: este no ve el tiempo de instalación local. El
tráfico de salida se toma con un contador en el router, y los aciertos y fallos del proxy se registran, en orden de llegada, como medida auxiliar que describe la transición del caché de frío a tibio dentro de la sesión. Toda sesión medida parte de caché frío. El mirror se sincroniza fuera de la sesión y su tráfico de sincronización se reporta aparte. Cada sesión sigue seis pasos: (1) reconstruir el entorno desde la lista versionada y verificar que solo está activa la configuración a medir; (2) hacer una sesión previa de calentamiento, que se descarta y se anota; (3) vaciar el caché; (4) medir; (5) guardar los datos en crudo, un CSV por sesión con fecha y versión de la lista; (6) calcular los percentiles al final, desde el CSV.

<span class="smallcaps">IV. Amenazas a la validez</span>

TABLA VIII

<span class="smallcaps">Amenazas y mitigaciones</span>

| **Amenaza**                     | **Efecto en el número**                                           | **Mitigación**                                                            |
|---------------------------------|-------------------------------------------------------------------|---------------------------------------------------------------------------|
| Tráfico ajeno en el enlace      | Otros usuarios del campus inflan los tiempos de una configuración | Mismo horario, tráfico base sin carga registrado y repetición en otro día |
| Estado del caché                | Un caché ya poblado favorece a una configuración                  | Vaciarlo antes de cada sesión medida, también después del calentamiento, y declararlo                                |
| Cambios en repositorios         | Un paquete se actualiza entre configuraciones                     | Lista de paquetes con versiones fijas                                     |
| Observaciones no independientes | Las estaciones de una sesión comparten el enlace                  | Tomar la sesión como unidad de la prueba y reportar el p95 por sesión además del agrupado                                |
| Un solo laboratorio             | El resultado no generaliza a otro hardware                        | Declararlo como límite del estudio                                        |

Declarar estas amenazas no debilita el trabajo: indica qué se controló y
qué queda como límite.

<span class="smallcaps">Referencias</span>

*Nota: las referencias \[1\]–\[6\], \[8\] y \[9\] se verificaron contra
el texto del propio artículo (autores, medio, año y, cuando existe,
DOI); el volumen y el número de \[6\] provienen de la página del grupo
autor. \[7\] y \[10\] se comprobaron en arXiv y en la página web,
respectivamente; \[9\] se confirmó en la ficha de IEEE Xplore (documento
8891000). La indexación se comprobó en Scopus (\[3\]–\[5\], \[9\]) y
Scimago (\[1\], \[2\], \[6\]). Falta la lectura a texto completo.*

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
2022. doi: 10.1109/TSE.2020.3048335

\[7\] T. A. Ghaleb, D. A. da Costa y Y. Zou, «The promise and reality of
continuous integration caching: An empirical study of Travis CI builds»,
arXiv:2601.19146, ene. 2026 (preprint).

\[8\] S. Becker, F. Schmidt y O. Kao, «EdgePier: P2P-based container
image distribution in edge computing environments», en Proc. IEEE Int.
Performance, Computing, and Communications Conf. (IPCCC), 2021. doi:
10.1109/IPCCC51483.2021.9679447

\[9\] N. Zhao et al., «Large-scale analysis of the Docker Hub dataset»,
en Proc. IEEE Int. Conf. Cluster Computing (CLUSTER), Albuquerque, NM,
2019. doi: 10.1109/CLUSTER.2019.8891000

\[10\] Python Packaging Authority, «Package index mirrors and caches»,
Python Packaging User Guide. \[En línea\]. Disponible en:
https://packaging.python.org/en/latest/guides/index-mirrors-and-caches/
(consultado el 7 de nov. de 2026).
