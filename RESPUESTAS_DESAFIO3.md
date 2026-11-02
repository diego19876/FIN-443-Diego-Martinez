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

Con ayuda de IA contrasté el programa con el enunciado y ejecuté la prueba pública: las 14 comprobaciones resultaron OK. Verifiqué la limpieza, las fórmulas, los pesos y las unidades. El primer rebalanceo fue el 31-12-2021 y hubo 48, usando ventanas de 252 retornos hasta el cierre incluido y aplicando los pesos desde el día siguiente. Para detectar look-ahead, truncé la historia después de cada rebalanceo: los pesos y retornos brutos y netos anteriores quedaron idénticos. También alteré todos los precios posteriores al 30-11-2023 y los 24 rebalanceos previos no cambiaron. Un cálculo independiente en Python reprodujo todas las métricas y pesos con diferencias inferiores a 4e-12. Comprobé contribuciones ERC iguales a 1/N, MDD con riqueza inicial de uno, compra inicial desde caja, costos en el primer retorno de cada período y rotación de EW posterior igual a cero. También probé otro formato, orden de filas, duplicados, nombres con tildes, otra rf y activos con inicio tardío. No encontré errores que requirieran modificar el programa; estas pruebas no sustituyen los archivos ocultos del profesor.

## Prompts principales

Reconstrucción resumida del pedido de esta conversación y del procedimiento de trabajo:

1. Completar la plantilla del Desafío 3 en R a partir del enunciado y de nuestro lector de precios corregido. Mantener argumentos y contratos; implementar las carteras IS, los pesos BT1 y el backtest mensual con ventana de 252 retornos.
2. Revisar las trampas del backtest: casos completos después de calcular retornos, fecha del primer rebalanceo, ventana hasta el cierre incluido, aplicación desde el día siguiente, costos en el primer retorno y rotación desde el segundo rebalanceo.
3. Ejecutar exactamente la prueba pública y contrastar los cálculos con una implementación independiente. Probar que los pesos BT1 no cambien cuando se eliminan datos futuros.
4. Preparar un informe de una o dos páginas con los resultados reales, diferencias IS-BT, riesgo, rotación, costos y elección condicional de cartera; relacionar tres referencias reales y adjuntar sus PDF.

5. Revisa que todo cumpla con el enunciado del Desafío 3 y que no estemos cayendo en las trampas del profesor, especialmente mirar el futuro. Trunca la historia después de cada rebalanceo y altera los precios futuros; comprueba que los pesos y retornos anteriores no cambien. Verifica además ventanas, aplicación de pesos, rotación y costos, e informa cualquier incumplimiento.

## Archivos que se entregan en Webcursos

`entrega_desafio3/desafio3.R`, `entrega_desafio3/informe_desafio3.pdf`, `entrega_desafio3/DeMiguel_2009.pdf`, `entrega_desafio3/Chaves_2012.pdf` y `entrega_desafio3/Ledoit_Wolf_2003.pdf`.

Los archivos del formulario y Webcursos no se han enviado automáticamente. El RUT y el código de sesión los ingresa Diego.
