# Clase 4 · Desafío 4


Se implementó la pieza de riesgo regional y se extrajo la cartera asignada. El lector procesa más de 17 millones de filas, cruza vigencias y convierte los retornos a USD antes de medir el riesgo. El memo cuantifica cuatro decisiones de limpieza y compara cinco modelos en fechas comunes. El VaR histórico es la propuesta provisional por estabilidad, con advertencia sobre el Z2 positivo. Se verificó la primera referencia frente al foro, aún quedan cuatro y su registro.

Se revisó la entrega contra la rúbrica. Se corrigió la continuidad de series en cambios de bolsa. Pasó una prueba independiente con un mercado alternativo, filas invertidas y cálculos a mano. El memo de dos páginas incluye cuatro contrafactuales, ejemplos de la cartera y la comparación de cinco modelos. Se completaron los cinco PDF y la tabla de referencias. En Webcursos quedó pendiente ajustar el asunto de la referencia ya publicada y registrar las otras cuatro.

Se contrastaron las 31 métricas y todas las columnas del backtest de la cartera asignada con un recálculo en R base sobre las series reconstruidas. La diferencia máxima fue 4,55e-13. Se repitió la prueba con el mercado alternativo y sus filas invertidas.

Se verificó el contrato de la versión empaquetada en una carpeta limpia: 31 métricas, 9 indicadores y 2.731 filas de backtest con FHS vacío en las primeras 250. La ejecución con los datos públicos tomó 16,8 s.

Autoevaluación del Desafío 4: se revisaron los nueve archivos del ZIP, el memo y las referencias. La última revisión del foro mostró una cita bajo la cuenta de Diego, con el asunto por ajustar, y cuatro referencias por registrar. Los datos ocultos y el desempeño en la defensa siguen pendientes de evaluación.

Quedó documentado cómo ejecutar el Desafío 4 y reutilizar construir_series como base de los desafíos 5 y 6. Se comprobó el script contra el archivo de entrega y se repitió la prueba con el mercado alternativo.
