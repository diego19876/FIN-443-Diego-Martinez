# Clase 6 — Bloque 1, 23-11-2026

**Pedido literal:** «resuelve el bloque 1 siguiendo estrictamente el material de clases y agents.md».

Codex leyó la consigna de la lámina 17 de Clase 6(1).pdf (página PDF 20) y usó fondo_clase6.csv sin modificar el original. Implementó clase6_bloque1.py, con estimación en los primeros mil días y prueba en los quinientos siguientes; MCO con intercepto, ridge con lambda 3000 y estandarización muestral exclusivamente de estimación, y MCO agregando la señal revisada. Conservó el promedio de estimación como referencia fuera de muestra. No optimizó lambda mirando la prueba.

Los resultados y sus rangos finales se encuentran en respaldo_clase6_bloque1/trazabilidad.csv. El correo se generó desde la salida del programa con el formato requerido. La explicación de por qué descartar la señal revisada procede del material de clase; el CSV no aporta fechas de publicación.

Se ejecutó el programa completo con datos públicos y dos CSV sintéticos. Un R independiente recalculó todos los resultados desde cada CSV; las diferencias y el hash probado constan en pruebas.log. También se verificó invariancia ante un cambio de escala de la señal revisada. Entradas, salidas y referencia R se conservaron en el respaldo. La descarga inicial falló por TLS con el Python del sistema y funcionó con Anaconda; no fue un error del cálculo.

Se prepararon código, correo y prompts, además del ZIP comprobado. El correo no se envió. La notación «3,000» se interpretó como 3000 y quedó explícita; la consigna no especifica ddof y se eligió la desviación muestral, compatible con R scale. No se resolvieron los otros bloques ni se modificaron las entregas anteriores.


## Actualización de GitHub solicitada — 23-11-2026

El usuario pidió publicar el avance del Desafío 5 y del Bloque 1, y recibir la redacción del correo. Se preparó la actualización de código, pruebas reproducibles, README, instrucciones y registros, conservando los cambios remotos previos y excluyendo datos, entregas personales, PDF y resultados. La versión pública de los registros omite RUT y enlaces personales; el registro local completo se conserva. La confirmación de publicación se informa en la respuesta final después de verificar el commit remoto. El correo académico no se envía con esta acción.
