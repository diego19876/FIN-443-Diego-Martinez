# Clase 2 — Desafío 2

Se completó `desafio2.R` usando R base y los argumentos de la plantilla. Se probaron ambos formatos de CSV, fechas en distinto orden, duplicados idénticos, múltiples splits, nombres con tildes y espacios, activos de inicio tardío y tasa libre de riesgo configurable.

Con el archivo público se detectaron 3 duplicados, el split 3:1 de TECNO del 14-08-2023 y el split 2:1 de BANCA del 03-03-2025. Se rellenaron los 8 faltantes de PUERTO y se conservaron los 325 faltantes iniciales de SOLAR.

Resultados con rf = 0,05:

| Métrica | Valor para formulario |
| --- | ---: |
| CAGR TECNO (%) | 5,20 |
| CAGR BANCA (%) | -0,49 |
| CAGR SOLAR (%) | -3,67 |
| Volatilidad PUERTO (%) | 24,49 |
| CAGR CARTERA_EW (%) | -3,65 |
| Sharpe CARTERA_EW | -0,358 |

La prueba pública de formato pasó sus siete comprobaciones. Un cálculo independiente en Python coincidió con R con diferencia máxima inferior a 6e-15. También se verificó que invertir filas, añadir duplicados idénticos o convertir al formato chileno no cambiaba los resultados.

