# Bitácora de uso de IA — FIN443

Autor: Diego Martinez. Herramienta utilizada: OpenAI Codex.

Esta bitácora registra cómo se ha usado IA para desarrollar, revisar y explicar el código del ramo. Se actualiza con los avances de cada clase. Los prompts que aparecen a continuación son reconstrucciones resumidas de las solicitudes de la conversación, no transcripciones literales.

## Contexto del proyecto

El trabajo comenzó con un diagnóstico de precios y continúa con un lector de datos y métricas financieras reproducible en R. La siguiente etapa del curso incorpora carteras y backtesting. El objetivo es poder ejecutar el código con archivos nuevos, verificar las cifras y explicar las decisiones, sin depender de rutas de un computador específico.

Se conservan por separado la solución propia, las pruebas y las pautas del profesor. No se considera validado un resultado solo porque el programa se ejecuta: se comprueban datos, transformaciones, fórmulas y formato de entrega. La IA genera propuestas y ayuda a verificar; Diego revisa y entrega el trabajo.

## Clase 1 — Diagnóstico de precios

**Solicitud a la IA.** Ejecutar y entender la pauta del diagnóstico con los precios aportados, comparando el caso correcto con las trampas de split sin ajustar, fechas sin ordenar y eliminación de filas con NA.

**Trabajo realizado.** Se ejecutó R base sobre el archivo compartido. Se compararon CAGR, volatilidad, Sharpe, correlación y métricas de la cartera. Se explicó que el split de RETAIL debía corregirse antes de calcular retornos.

**Evidencia.** El resultado correcto de la cartera fue CAGR 3,63 % y volatilidad 17,96 %. No ajustar el split cambió el CAGR de RETAIL de 3,16 % a -18,15 %.

## Clase 2 — Construcción y validación de desafio2.R

**Prompts principales reconstruidos.**

1. Completar la plantilla en R respetando el enunciado, los argumentos de terminal y el formato de salida.
2. Revisar específicamente los errores advertidos por el profesor en splits, fechas, faltantes, Sharpe y unidades.
3. Ejecutar el programa con los datos aportados y comprobar los resultados con un cálculo independiente.
4. Ejecutar exactamente la prueba pública del profesor.

**Trabajo realizado con IA.** Se implementaron detección del formato, orden y deduplicación, ajuste automático de splits 2:1 a 5:1 con margen de ±5 %, relleno por último precio disponible, métricas por activo y cartera equiponderada diaria. Se mantuvieron los faltantes anteriores al primer precio de cada activo.

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

> Actúa como colaborador de programación para FIN443, UAI 2026. Lee README.md, esta bitácora, los avances semanales y el código actual antes de proponer cambios. Sigue el enunciado vigente que aporte Diego y conserva los argumentos y formatos exigidos por el profesor. Explica qué cambias y por qué. No inventes datos, referencias, pruebas ejecutadas ni resultados. Conserva los datos originales y las pautas del profesor; modifica la solución propia. Verifica las transformaciones y los cálculos con pruebas pertinentes, y distingue el test de formato de la validación numérica. En backtests, usa únicamente información disponible antes de cada decisión. Registra en BITACORA_IA.md la solicitud, la ayuda de IA, las decisiones, los cambios, las comprobaciones realmente ejecutadas y sus límites; actualiza avance_clase_XX.md y los pendientes. Si falta información esencial, indícala. Mantén fuera del repositorio los datos, resultados CSV y PDF de clases conforme a la configuración actual.

## Cómo registrar las clases siguientes

Agregar una entrada por clase, sin reemplazar las anteriores: contexto y pedido de Diego; prompts resumidos o textuales identificados; contribución de la IA; decisiones y cambios en archivos; pruebas y resultados observados; errores encontrados y correcciones; pendientes. Si un programa cambia, indicar qué se modificó. No declarar una revisión o defensa humana que no conste en la conversación.

