# Instrucciones para trabajar en FIN443

Lee README.md, BITACORA_IA.md y los avances antes de modificar el código.

Repositorio principal: `diego19876/FIN-443-Diego-Martinez`. El Desafío 3 se implementará aquí. Esta decisión reemplaza la solicitud anterior de crear un repositorio separado.

## Contexto, pregunta y datos

Este es mi trabajo personal para FIN443, UAI 2026. La pregunta operativa del Desafío 2 es cómo obtener métricas correctas a partir de precios con formatos, fechas, faltantes y splits distintos. La siguiente etapa compara carteras y su desempeño dentro y fuera de muestra. La pregunta específica del proyecto grupal todavía no ha sido proporcionada: no inventarla.

Los archivos de entrada contienen una fecha en la primera columna y precios diarios por activo en las restantes. Los nombres y el número de activos pueden cambiar. Los CSV originales permanecen locales y sin modificaciones. Los archivos públicos son `precios_desafio2.csv` y `precios_desafio3.csv`. El enunciado completo y las plantillas del Desafío 3 fueron recibidos el 02-11-2026 y utilizados en la implementación.

## Convenciones financieras

- Retornos simples diarios: `r_t = P_t / P_(t-1) - 1`.
- CAGR: `(P_T / P_0)^(1 / años) - 1`, con días calendario entre las fechas relevantes divididos por `365.25`. Para un activo con inicio tardío, usar su primer precio disponible.
- Volatilidad anualizada: desviación estándar muestral de retornos diarios multiplicada por `sqrt(252)`.
- `rf` es una tasa anual expresada en fracción, configurable mediante argumentos; valor predeterminado del Desafío 2: `0.05`.
- Sharpe: `(mean(r) * 252 - rf) / vol_anual`. No sustituir la media anualizada por el CAGR.
- CARTERA_EW del Desafío 2: promedio de retornos disponibles por día y CAGR compuesto de la cartera, con el período completo del archivo.
- En CSV guardar CAGR y volatilidad en fracción, con punto decimal. Convertir a porcentaje y redondear solo al reportar cifras cuando lo pida el formulario.

## Contrato de archivos

Desafío 2: `Rscript desafio2.R datos.csv salida.csv [rf]`. Salida separada por comas, columnas `activo,cagr,vol,sharpe`, una fila por activo y una fila `CARTERA_EW`. Ordenar, eliminar fechas repetidas, ajustar splits según el enunciado y luego rellenar faltantes con el último precio disponible, conservando los faltantes iniciales. Sin preguntas por teclado ni rutas fijas.

Desafío 3: `Rscript desafio3.R datos.csv carpeta_salida [rf]`. Genera `pesos.csv` (`cartera,activo,peso`) y `metricas.csv` (`cartera,cagr,vol,sharpe,mdd,rotacion,sharpe_neto`). Se calculan retornos antes de filtrar casos completos. MinVar y máximo Sharpe permiten cortos. ERC debe igualar contribuciones a 1/N con precisión mínima de seis decimales. Se estima al último día de R de cada mes con las 252 filas hasta ese día incluido; no se rebalancea el último día de R. Se aplican los pesos desde el día siguiente hasta el próximo cierre incluido. Costos: 0,001 por suma absoluta de cambios de pesos objetivo, con compra inicial desde caja; se restan del primer retorno del período. Rotación promedio excluye la compra inicial. MDD incluye riqueza inicial de 1. Los CSV mantienen las ocho carteras de pesos y nueve de métricas del enunciado; las métricas IS no tienen rotación ni Sharpe neto.

Desafío 4 y continuidad: `python3 desafio4.py` se ejecuta sin argumentos en la carpeta con los siete CSV del curso y `cartera.csv`. Produce 31 métricas, 9 indicadores de calidad y el backtest de VaR. Para los desafíos 5 y 6, comenzar por `construir_series` del Desafío 4 y comprobar el enunciado de cada pieza antes de cambiar el contrato. Su calendario es la unión de las bolsas y sus retornos simples están en USD. El corte de la muestra se aplica después de construir la serie. Usar la documentación del README y mantener los datos y entregables personales fuera del repositorio.

## Reglas de trabajo y bitácora

Este AGENTS.md es la fuente única de instrucciones para Codex en el repositorio. Si se incorporan otras IA, mantener el mismo contenido en sus archivos de instrucciones, sin convenciones contradictorias. Registrar cuándo se añadieron estas instrucciones: no atribuir retroactivamente su versión actual a la especificación previa al código.

- En cada tarea de clase completada en este repositorio, actualiza BITACORA_IA.md y avance_clase_XX.md. Registra los pedidos, contribución de IA, cambios, evidencia de verificación, límites y pendientes.
- No inventes resultados, datos, referencias, pruebas ejecutadas ni decisiones que tomé. Identifica los prompts reconstruidos como resúmenes.
- Toda cifra del análisis incluida en un memo o resumen, también en tablas y gráficos, debe estar validada antes de publicarla por el script reproducible de la entrega (R, Python u otro lenguaje). Ejecuta el script con los insumos correspondientes y coteja cada valor con su salida, incluidas las unidades y el redondeo. Registra para cada cifra el archivo y las líneas de código que la calculan, junto con la salida donde se verifica. Nunca inventes, estimes manualmente ni agregues cifras que el script no calcula o valida. Si hace falta un cálculo para el informe, incorpóralo primero al script y ejecútalo antes de reportar la cifra.
- Conserva argumentos de terminal y contratos de archivos del enunciado vigente. Usa rutas relativas. No cambies rf a un valor fijo.
- Mantén la autoría de pautas y pruebas del profesor. Corrige nuestra solución, sin reemplazarla por la pauta.
- No modifiques los datos originales. No subas datos, resultados CSV ni PDF de clases al repositorio.
- Documenta el uso de la pauta al realizar correcciones. Distingue formato correcto de cálculos correctos y validación pública de validación con otros datos.
- En backtests, evita información futura y documenta el momento en que se estiman y aplican los pesos.
- No subas credenciales, tokens ni información personal sensible.


## Registro del prompt redactado con ayuda de IA — 19-11-2026

El usuario declaró que escribió los requisitos originales y pidió a una IA ordenarlos como un prompt claro. El texto siguiente conserva esa redacción asistida. Su incorporación fue solicitada expresamente el 19-11-2026. Este registro no acredita la ejecución ni la finalización del Desafío 5. La actualización operativa final indicada en la sección 8 corresponde al cierre de los entregables y su auditoría.

<details>
<summary>Prompt completo del Desafío 5</summary>

# Desafío 5 — Desarrollo integral, validación y auditoría para obtener el puntaje máximo

Necesito que desarrolles íntegramente el **Desafío 5**, siguiendo estrictamente las instrucciones de `AGENTS.md`, el enunciado oficial, la rúbrica, mis archivos y los aprendizajes de las evaluaciones anteriores.

**El objetivo es alcanzar el puntaje máximo (2/2), sin incumplir ninguna condición que pueda provocar una calificación de 0.** No quiero solamente una solución que funcione: necesito una entrega reproducible, rigurosa, completamente trazable y preparada para una evaluación automática con datos desconocidos.

## 1. Revisión inicial de archivos y antecedentes

Antes de desarrollar cualquier solución:

1. Lee completamente `AGENTS.md` y todas las instrucciones del Desafío 5.
2. Identifica todos los archivos disponibles, incluidos:
   - Mi cartera individual.
   - Las bases de datos públicas y adicionales del desafío.
   - Las curvas, mercados, bonos y archivos del proveedor.
   - Los trabajos de los desafíos anteriores.
   - El Excel con el feedback de las evaluaciones anteriores.
   - Los documentos que contienen los DOI y referencias utilizados previamente.
3. Mi RUT es **[RUT omitido en versión pública]**. Úsalo para identificar correctamente mi cartera, mis resultados y mi feedback.
4. Confirma explícitamente si tienes acceso a todos los archivos necesarios. Si falta alguno, identifícalo y explica su importancia. No inventes ni sustituyas información personal faltante.
5. Analiza detalladamente el feedback previo, identifica cada error y determina cómo evitar que vuelva a ocurrir.

Antes de programar, construye una lista de verificación con todos los requisitos de la entrega y los criterios de evaluación.

## 2. Desarrollo del código en formato Jupyter Notebook

Quiero que resuelvas el Desafío 5 en un archivo **`.ipynb`**, con código Python completo, ordenado, ejecutable y explicado.

El notebook debe:

- Cumplir estrictamente el contrato técnico del desafío y las instrucciones de `AGENTS.md`.
- Utilizar mi cartera real, sin modificarla arbitrariamente ni reemplazarla por una cartera de ejemplo.
- Generar exactamente las **35 métricas de `resultados_D5.csv` y los 11 indicadores de `calidad_tasas.csv`**, respetando nombres, orden, estructura, tipos y demás condiciones exigidas.
- Ejecutarse desde la carpeta de trabajo correspondiente, sin rutas absolutas ni dependencias de mi computador.
- No utilizar `os.chdir()`.
- Funcionar sin interacción manual, sin abrir el notebook y sin depender de celdas ejecutadas previamente.
- Mantener compatibilidad con el mecanismo de evaluación automática. Si el contrato exige un archivo `.py`, genera también ese archivo, sincronizado con el notebook.
- Manejar correctamente casos límite, archivos defectuosos, otras fechas de valoración, curvas, mercados, bonos y parámetros desconocidos.
- Evitar valores fijos que solamente funcionen con mis datos actuales.
- Implementar correctamente las simulaciones Monte Carlo y comprobar `MC_PUT` respecto de Black–Scholes, considerando la tolerancia de cuatro errores estándar.
- Incorporar validaciones automáticas, pruebas de consistencia y controles de calidad.

No confundas que el programa se ejecute correctamente con que sus resultados sean correctos. Debes comprobar ambas cosas por separado.

## 3. Trazabilidad obligatoria de cada dato

Este es uno de los requisitos más importantes.

**Toda cifra utilizada para formular una conclusión debe estar respaldada por un cálculo identificable en el código.**

Necesito que:

1. Verifiques cada número generado por el programa.
2. Identifiques su origen: archivo, columna, variable, transformación, fórmula y resultado.
3. Indiques las líneas exactas del código que producen o justifican cada cifra.
4. Distingas entre datos de entrada, parámetros, cálculos, resultados e interpretaciones.
5. Compruebes que ninguna cifra del análisis se haya introducido manualmente sin respaldo.
6. Verifiques las unidades, monedas, porcentajes, fechas, convenciones financieras y redondeos.
7. Si una cifra proviene de una fuente académica externa, identifiques también la fuente correspondiente.

Genera una **matriz de trazabilidad** con las siguientes columnas:

| Dato o indicador | Valor | Archivo y origen | Fórmula o transformación | Línea(s) de código | Uso en el análisis | Validación |
|---|---|---|---|---|---|---|

La numeración debe corresponder a la versión final de los archivos entregados, no a una versión intermedia.

Para el notebook, identifica la celda y las líneas correspondientes. Para el archivo `.py`, utiliza números de línea exactos.

## 4. Generación del resto de los entregables

Una vez terminado y validado el código, genera todos los demás entregables exigidos por el enunciado oficial y `AGENTS.md`.

No omitas entregables ni des por supuesto que alguno es opcional.

### Memo: máxima prioridad

Quiero un memo académico y técnicamente riguroso, redactado de manera natural, clara y profesional.

Debe incluir, conforme al enunciado:

- Bitácora cuantificada.
- Análisis financiero basado en los resultados reales.
- Análisis de tasas, curvas y riesgos correspondientes.
- Comparaciones e interpretaciones relevantes.
- Recomendación final argumentada, respaldada por evidencia cuantitativa.
- Referencias académicas verificadas.

**Después de redactar el memo completo, realiza una segunda auditoría, exclusivamente dedicada a comprobar todas sus cifras.**

Revisa número por número, incluyendo porcentajes, montos, tasas, diferencias, variaciones, resultados intermedios, métricas, indicadores y cifras utilizadas en las conclusiones.

Para cada número debes:

1. Encontrar su origen exacto.
2. Identificar las líneas del código que permiten reproducirlo, o la fuente documental si corresponde a un dato externo.
3. Recalcularlo y compararlo con el texto.
4. Verificar el redondeo y la interpretación.
5. Corregir cualquier inconsistencia.
6. Confirmar que la conclusión formulada está justificada por la evidencia y no exagera los resultados.

No debe quedar ninguna cifra sin explicación verificable.

Entrega también una tabla de auditoría del memo que permita comprobar cada dato numérico y su respaldo.

## 5. Referencias académicas: cumplimiento estricto

Debes cumplir íntegramente la regla de referencias publicada el **16 de noviembre**.

Las referencias se registran en el foro **“Citas APA desafío 5”**, indicando:

- DOI como asunto.
- Cita bibliográfica APA.
- Revista académica.
- Cuartil WoS.
- Nombre del estudiante.
- RUT: [RUT omitido en versión pública].

### Condiciones obligatorias

1. Necesito **8 referencias académicas** válidas, relevantes para el Desafío 5.
2. No puedes repetir ninguna referencia utilizada en mis desafíos 3 y 4 ni las incluidas en los documentos donde aparecen los DOI ya utilizados.
3. Debes comprobar que cada artículo existe realmente y que el DOI corresponde exactamente al artículo citado.
4. Verifica individualmente el título, primer autor, año de publicación y nombre de la revista, contrastándolos con Crossref.
5. Verifica el cuartil WoS mediante una fuente apropiada y especifica el año del cuartil.
6. Cada referencia debe contar con su **PDF completo, real y descargable legalmente**. No aceptes como sustituto un resumen, una página de aterrizaje, una vista previa o un enlace que no permita obtener el PDF.
7. Comprueba que la cita textual utilizada aparece literalmente en la página señalada del PDF.
8. Identifica la página exacta, considerando la diferencia entre la numeración impresa del artículo y la página del archivo PDF.
9. Verifica que la referencia y su cita textual sean pertinentes al argumento para el cual se utilizan.
10. Prepara las ocho referencias en el formato exacto requerido para registrarlas en el foro.

### Regla de exclusividad

El primer estudiante que registra un artículo se queda con él. Quien utiliza un artículo ya registrado puede obtener como máximo 1 punto, y lo que no está registrado por el propio estudiante no cuenta.

Por lo tanto:

- Comprueba la disponibilidad de las referencias en el foro si tienes acceso a él.
- Nunca afirmes que una referencia está libre, registrada o reservada sin haberlo comprobado.
- No confundas una referencia nueva para mí con una referencia aún disponible para registrar.
- No publiques ni registres nada en mi nombre sin mi autorización.
- Si no puedes consultar el foro, identifica expresamente esta limitación y prepara referencias alternativas.

**Una referencia con DOI inexistente, metadatos inconsistentes o cita textual incorrecta puede provocar una calificación de 0.** Por esta razón, no incluyas referencias cuya validación no hayas podido completar.

Genera una matriz de verificación que incluya DOI, metadatos Crossref, cuartil, enlace al PDF, página, cita textual exacta, pertinencia temática, ausencia de duplicación previa y estado de registro.

## 6. Evaluación estricta según la rúbrica oficial

La evaluación del desafío establece:

**2 puntos:** Cumple el contrato; las cifras son correctas con datos propios y ocultos; el memo tiene bitácora cuantificada, recomendación argumentada y análisis de tasas; incluye ocho referencias verificadas, registradas primero por el estudiante, con sus PDF y citas textuales; y el video cumple todas las reglas.

**1 punto:** El programa corre y cumple el contrato, pero presenta cifras incorrectas, falla alguna prueba oculta o existen entregables incompletos, o utiliza una referencia previamente registrada por otro estudiante.

**0 puntos:** No se entrega código; el programa no funciona fuera del computador del estudiante; se utiliza una cartera incorrecta; alguna referencia no coincide con Crossref o su PDF; o el estudiante no puede explicar la entrega durante la defensa.

Evalúa el trabajo como lo haría un corrector especialmente exigente.

No quiero una revisión superficial ni una aprobación basada solamente en que los archivos existen.

### Pruebas exigidas

- Ejecución desde cero en un entorno limpio.
- Ejecución no interactiva.
- Comprobación exacta de las 35 métricas y los 11 indicadores.
- Verificación independiente de cálculos y fórmulas.
- Pruebas con fechas, mercados, curvas, parámetros y bonos alternativos.
- Pruebas con archivos incompletos, inconsistentes y otros casos límite.
- Validación de Monte Carlo y su error estándar.
- Validación de cartera y RUT.
- Auditoría del memo, línea por línea y cifra por cifra.
- Verificación de las ocho referencias.
- Revisión de las instrucciones y reglas del video.
- Revisión de todos los requisitos de formato y entrega.
- Preparación para defender y explicar los cálculos, decisiones y conclusiones.

Utiliza el feedback de mis desafíos anteriores para detectar posibles patrones de errores y comprobar específicamente que no se repiten.

Si no tienes acceso a las pruebas ocultas oficiales, crea pruebas alternativas representativas. No afirmes que superaste pruebas ocultas que no has ejecutado.

## 7. Informe final de auditoría

Una vez finalizados todos los entregables, quiero un informe con:

1. Lista de los archivos generados.
2. Verificación de cumplimiento de cada requisito oficial.
3. Resultados de las pruebas ejecutadas.
4. Matriz de trazabilidad código–resultados.
5. Matriz de auditoría numérica del memo.
6. Matriz de verificación de referencias académicas.
7. Riesgos de descuento de puntaje.
8. Errores detectados y correcciones implementadas.
9. Requisitos pendientes de verificación o de intervención personal.
10. Evaluación estricta del puntaje que probablemente obtendría.

Distingue entre **verificado, corregido, pendiente y no verificable**.

No declares que todo está correcto si existen pruebas pendientes, referencias sin registrar, archivos faltantes o tareas que no puedes realizar.

## 8. Actualización final de AGENTS.md

**Solamente después de completar los entregables y la auditoría**, actualiza `AGENTS.md` para incorporar permanentemente los nuevos requisitos y procedimientos de trabajo que he solicitado.

Quiero que, en los próximos desafíos, se apliquen automáticamente los siguientes estándares:

- Revisión inicial de instrucciones, rúbricas y feedback anterior.
- Confirmación de archivos y cartera correcta.
- Desarrollo reproducible y compatible con evaluación automática.
- Validación independiente de cada cálculo.
- Trazabilidad completa entre código, resultados y conclusiones.
- Auditoría de todos los números utilizados en informes y memos.
- Verificación rigurosa de DOI, Crossref, PDF y citas textuales.
- Revisión de duplicaciones y restricciones académicas.
- Pruebas con datos alternativos y casos límite.
- Evaluación estricta antes de entregar.
- Identificación expresa de cualquier elemento no verificado.

Conserva las instrucciones anteriores que sigan siendo válidas y evita contradicciones o duplicaciones.

Los requisitos particulares del Desafío 5 deben quedar identificados como tales; los procedimientos generales de calidad deben aplicarse a los desafíos futuros.

## 9. Orden obligatorio de trabajo

Sigue esta secuencia:

1. Revisar todos los archivos, instrucciones y feedback.
2. Confirmar que dispones de mi cartera y las bases necesarias.
3. Construir la lista de cumplimiento.
4. Desarrollar el notebook y el programa ejecutable requerido.
5. Ejecutar pruebas y corregir los errores.
6. Verificar las 35 métricas y los 11 indicadores.
7. Construir la matriz de trazabilidad.
8. Investigar y validar las ocho referencias académicas.
9. Redactar el memo y generar los demás entregables.
10. Auditar individualmente todas las cifras del memo.
11. Evaluar estrictamente el trabajo completo.
12. Corregir los incumplimientos detectados y repetir las pruebas afectadas.
13. Actualizar `AGENTS.md`.
14. Entregar los archivos definitivos junto con el informe de auditoría.

## 10. Criterio final de aceptación

**No consideres finalizada la entrega por el simple hecho de haber generado los archivos.**

La entrega estará lista para mi revisión cuando:

- El código funcione de manera autónoma y reproducible.
- Todas las métricas e indicadores hayan sido comprobados.
- Cada cifra del memo sea trazable y correcta.
- Las ocho referencias hayan superado todas las validaciones que puedas efectuar.
- No existan incumplimientos conocidos que puedan causar una calificación de 0.
- Los entregables estén completos y sean coherentes entre sí.
- Se hayan documentado todas las verificaciones pendientes que dependen de mi intervención.
- `AGENTS.md` refleje las nuevas exigencias generales de calidad.

**Prioriza la exactitud y la evidencia sobre la velocidad. No inventes cifras, fuentes, citas, resultados de pruebas ni confirmaciones de cumplimiento.**

Quiero que el trabajo sea defendible: debo ser capaz de explicar de dónde proviene cada número, cómo se calculó, por qué se utilizó cada referencia y cómo se llegó a cada conclusión.

El objetivo es maximizar la probabilidad de obtener **2/2**, respetando íntegramente las reglas académicas y técnicas.

</details>

## Procedimiento permanente de revisión — incorporado el 19-11-2026; ampliado el 23-11-2026

Este procedimiento se incorporó después de preparar y auditar los entregables técnicos del D5 y se amplió a petición del usuario con el modo de trabajo aplicado posteriormente. Las fechas de incorporación son históricas, no requisitos atribuidos retroactivamente al profesor. El prompt asistido anterior se conserva íntegro con su procedencia. El estado de foro, video y envío se consulta en la bitácora más reciente; una lista antigua de pendientes no debe presentarse como estado actual.

- Antes de implementar, leer el enunciado vigente, la rúbrica y el feedback del estudiante identificado por su RUT; inventariar insumos y cotejar su cartera contra la asignación oficial. Crear una lista de cumplimiento y señalar faltantes concretos.
- Respetar nombres exactos de archivos, contratos, unidades y restricciones. No alterar la cartera o imponer restricciones ajenas al mandato para mejorar artificialmente el resultado. Conservar datos originales y registrar las ambigüedades.
- Separar tres verificaciones: contrato de salida, exactitud del cálculo mediante otro método y comportamiento con otros insumos. Cronometrar la ejecución. Las pruebas públicas no sustituyen las ocultas; informar qué capa valida cada contraste.
- Incluir una prueba integral del ejecutable completo, como proceso nuevo y desde una carpeta con todos los insumos sintéticos requeridos por el contrato. Contrastar las salidas con un cálculo de referencia independiente que reconstruya también las series desde esos insumos; no presentar pruebas aisladas de funciones como sustituto de esa ejecución integral. Variar fechas, parámetros, curvas y bonos, desordenar filas y alterar exclusivamente datos posteriores al corte para comprobar ausencia de información futura. Usar casos con valores conocidos, comprobar todas las métricas y conteos y conservar entradas, salidas, logs, versiones del entorno, tolerancias y hash del ejecutable probado fuera de los datos personales. Distinguir un error de dependencias del entorno de un error de la solución. No modificar la cartera real con las carteras sintéticas.
- Cuando se solicite notebook, entregar además el ejecutable exigido y comprobar su sincronización y ejecución desde cero. Guardar las tablas visibles. Si el entorno obliga a usar IPython sin servidor Jupyter, documentarlo con precisión.
- Aplicar la regla numérica anterior también a cada celda de tablas y cada cifra de guiones, resúmenes y conclusiones. Incorporar al auditor reproducible los cálculos adicionales del memo. Congelar el código antes de numerar sus líneas; registrar celda, rango final, fórmula, unidad, salida, escala y redondeo. Repetir la auditoría después de redactar y revisar visualmente el PDF; los identificadores documentales se distinguen de los resultados financieros.
- Para referencias, verificar DOI, título, primer autor, año y revista en Crossref; descargar el PDF completo legalmente; cotejar la frase literal y ambas paginaciones; comprobar pertinencia y el límite de palabras vigente. Documentar cuartil WoS con categoría, año y fuente, sin confundirlo con SJR ni presentar un año histórico como el último disponible.
- Comparar referencias con las utilizadas anteriormente y con las exclusiones recibidas. El registro previo no demuestra disponibilidad actual: revisar el foro si es accesible y no afirmar exclusividad sin evidencia. Preparar una alternativa cuando no se pueda comprobar la disponibilidad. No publicar en nombre del estudiante sin autorización.
- Antes de entregar, emitir un informe estricto con estados verificado, corregido, pendiente y no verificable, resultados reales de pruebas, riesgos y tareas personales. No prometer puntaje máximo ni fabricar enlaces, registros, videos o evidencia de pruebas. Mantener autoría de pautas y transparencia del uso de IA.

### Contrato particular del Desafío 5

`python3 desafio5.py`, sin argumentos ni cambio de directorio, con las seis bases del D4, la cartera propia y los tres CSV nuevos. Programa autónomo; 35 métricas en resultados_D5.csv y 11 indicadores en calidad_tasas.csv, con nombres, orden y fracciones del enunciado. Si se solicita un notebook adicional, debe coincidir con el ejecutable; la carpeta final respeta la preferencia posterior del usuario de entregar solo el .py. Las cifras adicionales del memo se obtienen con un auditor separado para no cambiar el contrato.

La entrega exige memo_D5.pdf de hasta dos páginas, referencias_D5.csv con ocho filas y ocho PDF, más video_D5.txt con enlace real al video personal de hasta tres minutos. Registro prioritario de referencias en el foro y rostro/voz propios son requisitos del estudiante; no se sustituyen por textos preparados. La primera auditoría D5 tenía pendientes el foro y el video; ambos se resolvieron después, según la bitácora. No se dispone de las pruebas ocultas ni se debe afirmar un envío sin confirmación del sistema.


## Preparación y cierre de la entrega — incorporado el 23-11-2026

Estas reglas complementan el procedimiento anterior y se aplican a próximos desafíos. Los nombres y cantidades de archivos, límites de extensión y condiciones de video se toman del enunciado vigente; no trasladar automáticamente los del D5.

### Código, informes y defensa

- Mantener un único programa oficial identificable y respetar la preferencia de formato más reciente del usuario. Un notebook o un auditor son complementarios cuando se solicitan; nunca sustituyen al ejecutable que corrige el profesor. Un cambio posterior de código exige actualizar los rangos afectados y repetir las comprobaciones correspondientes.
- En la matriz de trazabilidad dar un rango principal concreto por dato, incluyendo cada cifra de una tabla, y distinguirlo de la línea que exporta el resultado. No usar explicaciones genéricas como «ver implementación» ni rangos de versiones anteriores. Registrar origen, fórmula, unidad, escala y redondeo; separar resultados calculados de identificadores documentales y datos externos.
- Preparar una guía de defensa que permita explicar el origen de las cifras, las reglas de limpieza, los supuestos y sus límites. Redactar el guion del video con lenguaje natural y simple para un inversionista no técnico, de acuerdo con la pauta. Respaldar sus números con las mismas salidas y auditoría del memo; no añadir cifras de memoria ni exagerar lo demostrado por los modelos o backtests.

### Artículos y registro de referencias

- Conservar las URL efectivamente utilizadas para descargar los PDF en la matriz documental. Si el CSV oficial tiene un esquema fijo, mantenerlo intacto y crear una copia ampliada con enlaces en el respaldo, sin agregar columnas incompatibles a la entrega oficial.
- Identificar los PDF por número de referencia y título de la investigación, cuando se pida, conservando la asociación exacta con el CSV. Comprobar que cada archivo exista, no esté vacío, se abra y permita leer todas sus páginas; verificar título, DOI y cita textual en la página indicada. Al renombrar, comprobar que el contenido no cambie y actualizar las asociaciones del respaldo.
- Cuando el usuario autorice expresamente el registro, buscar cada DOI antes de publicar y registrar cada artículo por separado en el foro correcto, con el DOI como asunto y los campos exigidos. Verificar la publicación y autoría efectivas y conservar su enlace. No dar por completado el registro por haber preparado o enviado un formulario sin ver su confirmación. La autorización de registrar referencias no equivale a autorización de enviar la tarea académica.

### Video, enlace y archivos definitivos

- El video personal debe ser una grabación real del estudiante con su rostro y voz cuando así lo exija el profesor. No sustituirla por voz sintética ni avatar. Si solo existe un guion, pedir la grabación; no afirmar que ya existe un video.
- Si se solicita convertirlo a MP4, conservar el original y su contenido; comprobar que el archivo resultante se pueda leer, conserve video y audio y cumpla el límite de duración. No recortar contenido ni acelerar el habla sin autorización. Distinguir comprobar formato, pistas y duración de revisar íntegramente lo que se dice en el video.
- Crear el TXT de entrega únicamente con un enlace real facilitado o publicado con autorización. Comprobar que corresponda al video y que los permisos permitan al profesor acceder. No confundir un enlace descargable de esta conversación con un video publicado en la plataforma exigida. No inventar enlaces ni cambiar permisos sin autorización aplicable.
- Mantener una carpeta `entrega desafioN` únicamente con los archivos exigidos. Cotejar su contenido con la lista oficial; distinguir archivos que se adjuntan de salidas que el corrector genera al ejecutar el programa. Mover los respaldos a una carpeta hermana, sin eliminarlos. Dejar allí JSON de integridad, logs, pruebas, datos sintéticos, documentos de avance, auditorías y versiones ampliadas no exigidas.
- Si se publica un ZIP o un enlace de descarga, comprobar qué versión contiene y advertir cuando un cambio en la carpeta local no esté incorporado al paquete anterior. No afirmar que un archivo o nombre nuevo ya está en un ZIP que no se regeneró y verificó.
- Al cerrar, distinguir «archivos preparados y verificados», «referencias registradas», «video accesible» y «tarea enviada». El envío requiere la confirmación efectiva de Webcursos. Enumerar los pendientes reales de ese momento, sin repetir pendientes históricos resueltos ni prometer puntaje máximo. Mantener separados los requisitos escritos del profesor y las recomendaciones propias; no inventar prohibiciones de formato o de lectura del guion.


Nota de publicación: se omitieron identificadores personales y enlaces privados. El registro local completo se conserva.
