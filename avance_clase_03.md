# Clase 3 — Comparación con la pauta

Organización acordada: desarrollar el Desafío 3 dentro de `diego19876/FIN-443-Diego-Martinez`, el mismo repositorio del curso. No se creará un repositorio independiente para este desafío.

Se ejecutó la pauta comentada del profesor y la solución propia con `precios_desafio2.csv` y rf = 0,03. La diferencia máxima entre todas las métricas fue 0. El Sharpe de CARTERA_EW fue -0,252510271473252, equivalente a -0,253 con tres decimales.

Se amplió el lector propio para probar las fechas en formatos `%d-%m-%Y`, `%Y-%m-%d` y `%d/%m/%Y`, siguiendo la pauta. Después del cambio, el programa volvió a pasar la prueba pública.

La detección del separador usa `count.fields` en la solución propia y conteo de caracteres en la pauta. Ambos procedimientos reconocen el archivo público.

## Desafío 3 implementado

Se completó `desafio3.R` con R base. La prueba pública exacta pasó las 14 comprobaciones y los cálculos se contrastaron con NumPy, usando un segundo algoritmo para ERC. Diferencia máxima: menor que 4e-12. También se probaron formato internacional, inversión de fechas, duplicados, tildes, otra rf y datos simulados de tres activos con inicio tardío y múltiples splits.

El primer rebalanceo fue el 31-12-2021 y hubo 48. Truncar después de esa fecha, dejando días hasta el 05-01-2022, no cambió los pesos BT1. Se verificaron costos iniciales, pesos objetivo constantes por período y MDD con riqueza inicial igual a uno.

| Cifra | Valor |
| --- | ---: |
| ELECTRICA en IS_MINVAR (%) | 50,45 |
| Sharpe IS_MAXSHARPE | 1,029 |
| CAGR BT_MINVAR (%) | 14,51 |
| Sharpe BT_EW | 0,877 |
| Sharpe BT_INVVOL | 0,866 |
| Sharpe BT_ERC | 0,860 |
| MDD BT_MINVAR (%) | 14,64 |
| Sharpe neto BT_MINVAR | 0,663 |

Se preparó un informe de dos páginas con referencias citadas en contexto. Los tres PDF están disponibles localmente; las versiones de trabajo de DeMiguel y Chaves están identificadas como tales. Las respuestas del formulario están en RESPUESTAS_DESAFIO3.md. Pendiente humano: revisar el informe y entregar en formulario y Webcursos. Los archivos ocultos del profesor no están disponibles.

