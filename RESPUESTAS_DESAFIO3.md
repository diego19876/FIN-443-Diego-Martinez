# Desafío 3 — Respuestas para el formulario

Diego Martinez. Lenguaje: R. Herramienta de IA: OpenAI Codex.

Archivo público `precios_desafio3.csv`; rf = 0,05. Copiar los valores con coma decimal, sin el símbolo de porcentaje. Los pesos, CAGR y caída máxima se expresan en %; los Sharpe no se multiplican por 100.

| Campo | Valor |
| --- | ---: |
| Peso de ELECTRICA en IS_MINVAR (%) | 50,45 |
| Sharpe IS_MAXSHARPE | 1,029 |
| CAGR BT_MINVAR (%) | 14,51 |
| Sharpe BT_EW | 0,877 |
| Sharpe BT_INVVOL | 0,866 |
| Sharpe BT_ERC | 0,860 |
| Caída máxima BT_MINVAR (%) | 14,64 |
| Sharpe neto BT_MINVAR | 0,663 |

## Qué se verificó y cómo

Con ayuda de IA se ejecutó exactamente la prueba pública del profesor: las 14 comprobaciones resultaron OK. Se revisaron dos duplicados, el split 2:1 de RETAIL y cinco faltantes de ELECTRICA. El primer rebalanceo fue el 31-12-2021, con una ventana de 252 retornos; hubo 48 rebalanceos. Se verificó que los pesos se aplicaran desde el día siguiente y que truncar los datos al 05-01-2022 no cambiara los pesos BT1. Un cálculo independiente en NumPy, con otro algoritmo para ERC, reprodujo todas las métricas y pesos con diferencia máxima menor que 4e-12. Se comprobaron sumas de pesos iguales a uno, contribuciones ERC iguales a 1/N, rotación de EW nula y costo inicial desde caja. También se probaron formato internacional, fechas invertidas, duplicados, nombres con tildes y espacios, rf = 0,03 y datos simulados con otro número de activos, inicio tardío y varios splits.

## Prompts principales

Reconstrucción resumida del pedido de esta conversación y del procedimiento de trabajo:

1. Completar la plantilla del Desafío 3 en R a partir del enunciado y de nuestro lector de precios corregido. Mantener argumentos y contratos; implementar las carteras IS, los pesos BT1 y el backtest mensual con ventana de 252 retornos.
2. Revisar las trampas del backtest: casos completos después de calcular retornos, fecha del primer rebalanceo, ventana hasta el cierre incluido, aplicación desde el día siguiente, costos en el primer retorno y rotación desde el segundo rebalanceo.
3. Ejecutar exactamente la prueba pública y contrastar los cálculos con una implementación independiente. Probar que los pesos BT1 no cambien cuando se eliminan datos futuros.
4. Preparar un informe de una o dos páginas con los resultados reales, diferencias IS-BT, riesgo, rotación, costos y elección condicional de cartera; relacionar tres referencias reales y adjuntar sus PDF.

## Archivos que se entregan en Webcursos

`entrega_desafio3/desafio3.R`, `entrega_desafio3/informe_desafio3.pdf`, `entrega_desafio3/DeMiguel_2009.pdf`, `entrega_desafio3/Chaves_2012.pdf` y `entrega_desafio3/Ledoit_Wolf_2003.pdf`.

Los archivos del formulario y Webcursos no se han enviado automáticamente. El RUT y el código de sesión los ingresa Diego.
