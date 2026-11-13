# Bitácora de uso de IA — FIN443

Autor: Diego Martinez. Herramienta utilizada: OpenAI Codex.

En esta bitácora registro cómo uso IA para desarrollar, revisar y explicar el código del ramo. Incorporo los avances de cada clase. Los prompts que aparecen a continuación son reconstrucciones resumidas de las solicitudes de la conversación, no transcripciones literales.

## Contexto del proyecto

Empecé con un diagnóstico de precios y continué con un lector de datos y métricas financieras reproducible en R. La siguiente etapa del curso incorpora carteras y backtesting. El objetivo es poder ejecutar el código con archivos nuevos, verificar las cifras y explicar las decisiones, sin depender de rutas de un computador específico.

Conservo por separado mis soluciones, las pruebas y las pautas del profesor. Para validar un resultado, pido comprobaciones de datos, transformaciones, fórmulas y formato de entrega. Uso Codex para generar propuestas y ejecutar verificaciones.

## Clase 1 — Diagnóstico de precios

**Solicitud a la IA.** Le pedí a Codex que ejecutara y explicara la pauta del diagnóstico con los precios aportados, comparando el caso correcto con las trampas de split sin ajustar, fechas sin ordenar y eliminación de filas con NA.

**Trabajo realizado.** Codex ejecutó R base sobre el archivo compartido. Se compararon CAGR, volatilidad, Sharpe, correlación y métricas de la cartera. Se explicó que el split de RETAIL debía corregirse antes de calcular retornos.

**Evidencia.** El resultado correcto de la cartera fue CAGR 3,63 % y volatilidad 17,96 %. No ajustar el split cambió el CAGR de RETAIL de 3,16 % a -18,15 %.

## Clase 2 — Construcción y validación de desafio2.R

**Prompts principales reconstruidos.**

1. Completar la plantilla en R respetando el enunciado, los argumentos de terminal y el formato de salida.
2. Revisar específicamente los errores advertidos por el profesor en splits, fechas, faltantes, Sharpe y unidades.
3. Ejecutar el programa con los datos aportados y comprobar los resultados con un cálculo independiente.
4. Ejecutar exactamente la prueba pública del profesor.

**Trabajo realizado con IA.** Con ayuda de Codex incorporé detección del formato, orden y deduplicación, ajuste automático de splits 2:1 a 5:1 con margen de ±5 %, relleno por último precio disponible, métricas por activo y cartera equiponderada diaria. Se mantuvieron los faltantes anteriores al primer precio de cada activo.

**Verificación.** Se detectaron 3 duplicados y los splits de TECNO y BANCA. Los retornos de esos eventos pasaron de -66,53 % a +0,42 % y de -51,81 % a -3,62 %. Se rellenaron 8 faltantes de PUERTO y se conservaron 325 faltantes iniciales de SOLAR. El cálculo independiente en Python coincidió con R con diferencia inferior a 6e-15. Invertir las filas, añadir duplicados idénticos y convertir al formato chileno mantuvo los resultados. La prueba pública del profesor pasó sus siete comprobaciones.

**Resultados con rf = 0,05.** CAGR TECNO: 5,20 %; CAGR BANCA: -0,49 %; CAGR SOLAR: -3,67 %; volatilidad PUERTO: 24,49 %; CAGR CARTERA_EW: -3,65 %; Sharpe CARTERA_EW: -0,358.

**Corrección de una afirmación de la IA.** Inicialmente se habían ejecutado verificaciones equivalentes al test público, pero no su código exacto. Se aclaró esa diferencia y luego se ejecutó la prueba del profesor literalmente. Se distingue este test de formato de la validación de los cálculos.

## Clase 3 — Comparación con la pauta y preparación del siguiente desafío

**Prompts principales reconstruidos.** Ejecutar la pauta comentada con los mismos datos y rf = 0,03; comparar el programa propio con la pauta; identificar una diferencia real, proponer y aplicar la corrección; seleccionar referencias para el informe del Desafío 3.

**Verificación y cambio.** Ambos programas produjeron exactamente las mismas métricas del archivo público con rf = 0,03. El Sharpe de CARTERA_EW fue -0,252510271473252, redondeado a -0,253. Se amplió la conversión de fechas del código propio para probar `%d-%m-%Y`, `%Y-%m-%d` y `%d/%m/%Y`, siguiendo la pauta. La prueba pública volvió a pasar después de ese cambio.

**Límites de la comparación.** La coincidencia está demostrada con el archivo público. No implica que ambas implementaciones sean idénticas para todos los casos posibles. El programa propio incluye validaciones y diferencias de implementación adicionales, por ejemplo el manejo de días sin retornos disponibles y una tolerancia numérica en el umbral del split.

**Bibliografía preliminar.** Se propusieron Jagannathan y Ma (2003), Tu y Zhou (2011) y Kirby y Ostdiek (2012). La selección no equivale a una revisión final de los tres PDF ni a verificar su indexación individual en Google Scholar. Antes de incorporarlos al informe se debe revisar cada texto, confirmar los metadatos de la versión citada y vincularlo con una afirmación concreta.

**Pendiente.** Implementar y validar el Desafío 3; preparar el informe y revisar sus referencias. No hay resultados del Desafío 3 todavía.

## Prompt general para continuar el trabajo

> Actúa como colaborador de programación para FIN443, UAI 2026. Lee README.md, esta bitácora, los avances semanales y el código actual antes de proponer cambios. Sigue el enunciado vigente que te comparta y conserva los argumentos y formatos exigidos por el profesor. Explica qué cambias y por qué. No inventes datos, referencias, pruebas ejecutadas ni resultados. Conserva los datos originales y las pautas del profesor; modifica la solución propia. Verifica las transformaciones y los cálculos con pruebas pertinentes, y distingue el test de formato de la validación numérica. En backtests, usa únicamente información disponible antes de cada decisión. Registra en BITACORA_IA.md la solicitud, la ayuda de IA, las decisiones, los cambios, las comprobaciones realmente ejecutadas y sus límites; actualiza avance_clase_XX.md y los pendientes. Si falta información esencial, indícala. Mantén fuera del repositorio los datos, resultados CSV y PDF de clases conforme a la configuración actual.

## Cómo registrar las clases siguientes

### Actualización del 02-11-2026 — Repositorio y bibliografía

Pedí renombrar el repositorio a `FIN-443-Diego-Martinez` y desarrollar el Desafío 3 en el repositorio del curso. Esta instrucción reemplaza la preferencia anterior de usar dos repositorios. Se conservan el código, las pautas y el historial existentes.

Después de revisar las instrucciones de la Clase 3, se completó AGENTS.md con la pregunta operativa, los datos, retornos simples, anualización con sqrt(252), rf anual, fórmulas, contrato de archivos y prohibición de inventar datos o referencias. Esta ampliación se realizó después del código del Desafío 2; queda registrada para especificar el trabajo futuro antes de generar el Desafío 3. Se confirmó mediante la conexión de GitHub que el repositorio figura como público.

Tras comparar la bibliografía de compañeros, se seleccionaron otros tres artículos: DeMiguel, Garlappi, Nogales y Uppal (2009), “A generalized approach to portfolio optimization”; Chaves, Hsu, Li y Shakernia (2012), “Efficient algorithms for computing risk parity portfolio weights”; y Ledoit y Wolf (2003), “Improved estimation of the covariance matrix of stock returns with an application to portfolio selection”. Se verificaron los metadatos en fuentes académicas y se revisaron los resúmenes y textos disponibles. Finalmente se buscaron los tres títulos exactos en Google Scholar mediante Chrome y se confirmó que los tres aparecen, con sus autores y años. Esto confirma su indexación; no equivale a reproducir todos sus experimentos. Pendiente: reunir los PDF y respaldar con ellos afirmaciones concretas del informe.

Agregar una entrada por clase, sin reemplazar las anteriores: contexto y mi solicitud; prompts resumidos o textuales identificados; contribución de la IA; decisiones y cambios en archivos; pruebas y resultados observados; errores encontrados y correcciones; pendientes. Si un programa cambia, indicar qué se modificó. No declarar una revisión o defensa humana que no conste en la conversación.

## Desafío 3 implementado — 02-11-2026

**Solicitud.** Compartí el enunciado completo, las plantillas R y Python, los precios y la prueba pública para desarrollar el desafío en este mismo repositorio. Se mantuvo R como lenguaje de entrega.

**Contribución de la IA.** Codex leyó el contrato e implementó `desafio3.R`, reutilizando el lector del Desafío 2 revisado con la pauta. Se calcularon las cinco carteras IS, los cuatro juegos de pesos BT1 y cuatro estrategias BT. MinVar y la tangente permiten cortos según las fórmulas del enunciado. ERC se resolvió por descenso cíclico de coordenadas sobre el objetivo convexo. Se prepararon un informe de dos páginas y respuestas para el formulario.

**Decisiones verificables.** Los retornos se calcularon antes de filtrar casos completos. Los cierres de mes se identificaron sobre las fechas de R; la ventana incluye el cierre y los pesos empiezan a operar al día siguiente. No se rebalancea el último día de R. Los costos incluyen la compra inicial desde caja y se descuentan del primer retorno del período. La rotación se calcula respecto de pesos objetivo, sin deriva y sin dividir por dos. El cálculo de MDD incluye W0 = 1. El CSV mantiene fracciones y no redondea los resultados.

**Hallazgos.** Archivo público: 1.305 filas, 1.303 fechas únicas, dos duplicados, cinco faltantes de ELECTRICA y un split 2:1 de RETAIL del 08-04-2024. Matriz final: 1.302 retornos completos. Primer rebalanceo: 31-12-2021, 48 rebalanceos. Se generaron 40 filas en pesos.csv y nueve en metricas.csv.

**Pruebas ejecutadas.** La prueba pública exacta del profesor pasó sus 14 comprobaciones. El contraste independiente en `tests/verificar_desafio3.py` utilizó NumPy y un algoritmo Newton para ERC distinto del R; se reprodujeron todos los pesos y métricas del archivo público tanto con rf = 0,05 como con 0,03, con diferencia máxima menor que 4e-12. Se verificaron transformación al formato internacional, inversión de filas, duplicados adicionales y nombres con espacios y tildes. Se probó otro conjunto simulado de tres activos con inicio tardío, faltantes y dos splits del mismo activo. Al truncar el archivo al 05-01-2022, los pesos BT1 no cambiaron: no dependen del futuro eliminado. No se han ejecutado los archivos ocultos del profesor.

**Resultados para el formulario.** Peso ELECTRICA IS_MINVAR: 50,45 %; Sharpe IS_MAXSHARPE: 1,029; CAGR BT_MINVAR: 14,51 %; Sharpe BT_EW: 0,877; Sharpe BT_INVVOL: 0,866; Sharpe BT_ERC: 0,860; caída máxima BT_MINVAR: 14,64 %; Sharpe neto BT_MINVAR: 0,663.

**Interpretación y límites.** Ninguna de las cuatro estrategias con BT pierde Sharpe frente a su IS en este archivo. El informe lo explica sin forzar la idea de que BT siempre empeora: los períodos difieren y también cambia la estimación. No se usa shrinkage ni restricciones adicionales para alterar las fórmulas exigidas. Se documenta la decisión condicional de elegir ERC para un cliente que prioriza balancear riesgo, distinguiéndola de EW como mejor Sharpe neto observado.

**Referencias y PDF.** Se consiguieron copias de los tres artículos previamente verificados en Scholar. Ledoit y Wolf es la versión publicada; Chaves y DeMiguel son versiones de trabajo del mismo artículo, con fechas julio de 2012 y septiembre de 2008. Se identifican esas versiones en el informe y en `referencias_desafio3.md`. Se revisaron sus resúmenes y pasajes pertinentes. Los sitios originales bloquearon varias descargas; se recurrió a copias universitarias y a las versiones archivadas que enlaza Google Scholar. No se reconstruyeron ni inventaron los artículos. Los PDF permanecen como adjuntos locales, fuera del repositorio público.

**Entrega y pendientes.** El código y documentos fuente se incorporan al mismo repositorio FIN-443-Diego-Martinez. La carpeta local `entrega_desafio3/` reúne el script, el informe y los tres PDF. En ese momento me quedaba ingresar mi RUT y el código de sesión, revisar el informe y completar la entrega.

### Auditoría reforzada del backtest — 02-11-2026

Le pedí a Codex que revisara el cumplimiento del enunciado y las trampas advertidas, especialmente mirar el futuro, y redactara las respuestas y prompts para el formulario. Se releyó el enunciado, se inspeccionó el código y se repitieron la prueba pública y la validación independiente, sin fallas ni cambios en cifras. Se añadió `tests/verificar_lookahead3.R`: trunca los datos después de cada uno de los 48 rebalanceos y compara todos los pesos y retornos brutos y netos anteriores. Las diferencias máximas fueron exactamente 0. También altera todos los precios posteriores al 30-11-2023 y verifica que los 24 rebalanceos previos y sus retornos realizados no cambien. Se comprueba que los costos aparezcan únicamente en el primer retorno del período, incluida la compra inicial desde caja, y que la rotación EW posterior sea 0. Todas las comprobaciones pasaron. No fue necesario modificar `desafio3.R`; se actualizó el texto del formulario en RESPUESTAS_DESAFIO3.md. Límite: evidencia sobre estos datos y pruebas; los archivos ocultos no están disponibles.

## Revisión acumulativa del Desafío 3 con la pauta — 13-11-2026

Le pedí a Codex que contrastara mi código con la pauta de la semana anterior y mejorara la pieza para que pudiera seguir usándola. Se conservó la pauta original en `pauta_desafio3_comentada.R` y se ejecutaron ambos scripts sobre el CSV público con tasas anuales de 5 % y 3 %. Antes de editar, la diferencia máxima fue 3,34e-12 en pesos y 1,89e-12 en métricas. El contraste confirmó los casos completos, los 48 rebalanceos desde el 31-12-2021, los costos y las métricas.

Se separó la lectura de los precios del cálculo de los retornos. El código propio detecta splits entre observaciones y aplica el factor al cociente del día en que aparece el nuevo precio. Es equivalente a reescalar los niveles anteriores y evita recorrer todo el historial por cada split. Se añadió una validación de fechas distintas tras quitar duplicados. Los CSV de la versión anterior y la nueva tuvieron diferencia numérica cero con ambas tasas. Pasaron las 14 comprobaciones públicas, el contraste independiente con NumPy, la prueba sintética con inicio tardío, faltantes y dos splits, y las pruebas de prefijos y costos de los 48 rebalanceos. Los datos ocultos siguen sin estar disponibles.

La entrega original de la semana anterior permanece en `desafio3.R`. La revisión propia con la pauta se conserva en `desafio3_corregido.R` y usa los mismos argumentos. Esta revisión sirve como base para el trabajo acumulativo.

## Desafío 4 — 13-11-2026

Compartí el enunciado, las fuentes públicas, las plantillas y la prueba de contrato. Se recuperaron del CSV asignado mis 20 posiciones y se implementó el lector regional y el cálculo de riesgo en Python. Se conserva el calendario unión, el orden de versiones y la vigencia de ticker. El índice equipondera retornos observados y eventos de salida. Se usaron ventanas estrictamente anteriores para los cinco VaR.

**Comprobaciones.** Ejecución directa con 17.305.011 filas en 19 s. Los cortes de la serie en 800 y 1.500 días reprodujeron exactamente el prefijo del backtest. Se cuantificaron cuatro escenarios aislados de limpieza y se compararon cinco modelos sobre fechas comunes. Se preparó memo y una referencia verificada.

**Webcursos.** Le pedí a Codex que revisara las 95 discusiones del foro. No apareció el DOI de Giacomini y White (2006), cuya versión publicada se verificó. La referencia aún debe registrarse en el foro. Quedan cuatro referencias y los datos ocultos no están disponibles.

La prueba del profesor copiada de la plantilla pasó todos los controles, incluida la ejecución con alfa 0,95. Los controles públicos no certifican los valores esperados en archivos ocultos.

### Revisión contra la rúbrica del Desafío 4

Le pedí a Codex que corrigiera y revisara mi entrega completa. Se añadió la continuidad de precios por emisor cuando cambia de bolsa y se ejecutó una prueba independiente con otro mercado pequeño y sus filas invertidas. Se verificaron a mano las cifras del cambio de ticker y del split y se amplió el memo a dos páginas con estos ejemplos, la comparación por pérdida cuantílica asimétrica y los límites de la recomendación. Se inspeccionó el PDF renderizado.

Se cotejaron los cinco DOI, sus PDF y las páginas que respaldan las decisiones. Los cuartiles Q1 provienen de la tabla de WoS/JCR 2024 por categoría. En 101 discusiones de Webcursos figuraba mi publicación de Giacomini y White, con la cita en el asunto. Los otros cuatro DOI no figuraban en la revisión. Se dejaron cinco textos listos para copiar. Me quedaba ajustar el primer asunto al DOI y registrar los otros cuatro. Los archivos oficiales ocultos siguen sin estar disponibles.

En la revisión final, el script pasó todos los controles de la prueba pública en la ejecución principal (18 s). El bloque de alfa 0,95 de la prueba no pudo copiar 541 MB por falta de espacio. Se reprodujo ese bloque con el mismo código del ZIP, una copia pequeña de los parámetros y enlaces a los datos originales. El VaR histórico bajó de 2,179 % a 1,357 % y el retorno acumulado y beta quedaron idénticos. El ZIP contiene los nueve archivos de la tarea y pasó su prueba de integridad.

### Verificación detallada de las reglas del Desafío 4

Se cotejó el script del ZIP con las ocho reglas de datos y las nueve de riesgo. Se ejecutó la prueba independiente del mercado pequeño, con el orden de filas invertido. Incluye vigencia de tickers, corrección de precios, FX anterior, feriados, retorno terminal y promedio equiponderado de emisores con retorno. Sobre las series públicas de la cartera y el mercado reconstruidas desde los CSV, se recalcularon las 31 métricas y todas las columnas del backtest en R base, con cuantil tipo 7 y p-valores de chi cuadrado. La diferencia máxima en métricas fue 4,55e-13. Este contraste valida la capa de riesgo a partir de las series reconstruidas. El caso pequeño con retornos calculados a mano aporta la comprobación independiente de la capa de datos.

Se verificó el contrato exacto desde el ZIP en una carpeta limpia, con los siete CSV y la cartera de 20 filas, sin argumentos. La ejecución tardó 16,8 s. Se cotejaron el orden de las 31 métricas, los 9 indicadores y las 13 columnas del backtest. Los 250 primeros pares FHS quedaron vacíos, los 2.481 restantes completos, y los incumplimientos coincidieron con la comparación estricta pérdida > VaR y con el resumen. Los tres CSV coincidieron byte por byte con los de la carpeta local y no se necesitó modificar el código.

### Autoevaluación con la rúbrica del Desafío 4

Se revisaron los nueve archivos del ZIP y la evidencia de las pruebas pública, independiente en R y con un mercado sintético. El memo satisface el límite de dos páginas y cuantifica cuatro omisiones, con una recomendación de VaR histórico sustentada por cobertura y estabilidad. Se revisaron las 102 discusiones del foro. Solo Giacomini y White figuraba en mi cuenta, con la cita completa como asunto. Queda pendiente usar el DOI como asunto y registrar las otras cuatro referencias. El punto máximo también depende de los datos ocultos y de la defensa individual.

### Continuidad del Desafío 4 en GitHub

Pedí incorporar al repositorio el código y la documentación del Desafío 4 como base de los desafíos 5 y 6. Se documentó la importación de construir_series, el calendario, la moneda y el corte de muestra. Se cotejó el código con el ZIP de entrega, se repitió la prueba del mercado alternativo y se generó el memo desde una carpeta limpia. La entrega individual y los archivos de datos permanecen locales. Los contratos de los próximos desafíos se definirán según sus propios enunciados.

### Entrega y revisión de la bitácora del Desafío 4

Pedí a Codex que adjuntara los nueve archivos por separado en una sola entrega. Webcursos confirmó el estado «Enviado para calificar». También pedí redactar mi documentación en primera persona e identificar las verificaciones que ejecutó Codex.
