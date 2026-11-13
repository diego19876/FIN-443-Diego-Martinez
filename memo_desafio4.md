# Riesgo diario de la cartera regional

**Para el Comité de Riesgo · Diego Martinez · FIN443**

**Decisión propuesta.** Propongo usar provisionalmente el VaR histórico al 99 % con 250 días para el límite diario. Es el modelo con menor cambio absoluto diario medio entre los cinco en las 2.481 fechas comparables. Su cobertura no se rechaza al 5 % y se puede explicar con las pérdidas observadas. El último límite para el día siguiente es 1,537 %. La calibración de la severidad es una tarea aparte.

## Bitácora de datos

Leí 10.389.384 filas de Santiago y 6.915.627 de Nueva York. Inspeccioné encabezados y formatos y uní ambos calendarios, que suman 3.762 días. Conté 68.945 filas repetidas por fecha y ticker y conservé la versión mayor. Crucé las fechas con los intervalos del maestro. Hay 400 emisores que cambiaron de ticker. Busqué huecos en el cruce cambiario: 154 días del fondo carecen de cotización de FX y usan la última anterior. Identifiqué 17.375 pares posteriores a una salida y los descarté. La cartera tiene 1 split y 491 dividendos en el archivo de eventos, antes de restringir la muestra.

| Regla omitida por separado | Días de cartera afectados | Retorno acumulado | VaR histórico |
|---|---:|---:|---:|
| Ninguna · base | — | 425,03 % | 2,179 % |
| Ajuste por split | 1 | 408,34 % | 2,179 % |
| Dividendos | 46 | 334,35 % | 2,179 % |
| Conversión a USD | 2.858 | 537,76 % | 2,307 % |
| Reglas de salida de bolsa | 130 | 446,04 % | 2,152 % |

Los días afectados cuentan cambios de retorno superiores a 1e-12. Ignorar las salidas significa conservar filas posteriores y omitir el retorno final. Calcular sin conversión mezcla retornos locales y en USD y aquí solo sirve como contraste. En la muestra, el índice equiponderado de todos los emisores acumuló 453,21 %. La cartera tuvo beta 0,948 y VaR activo de 1,039 %.

Convertí los retornos a una unidad común, como la comparación en dólares de Jorion y Goetzmann (1999, p. 959). Conservé la historia previa a la salida para evitar seleccionar solo supervivientes, un problema documentado por Brown et al. (1992, p. 553).

En mi cartera, EMI4368 pasa de WKWZ a CTOF entre el 15 y el 16 de julio de 2019. El retorno de −2,08 % compara los cierres 45,4380 y 44,4940 USD del mismo emisor. JFAS tuvo un split 3:1 el 9 de septiembre de 2020. Comparar 243,6510 × 3 con 739,2590 USD da −1,12 %, frente a −67,04 % si se ignora el split.

<!-- PAGINA -->

## Comparación de pronósticos

| Modelo | Incumplimientos / 2.481 | p Kupiec | p Christoffersen CC | Cambio diario medio del VaR (pb) |
|---|---:|---:|---:|---:|
| Histórico | 32 | 0,165 | 0,280 | 0,33 |
| Normal | 34 | 0,079 | 0,169 | 0,67 |
| RiskMetrics | 36 | 0,034 | 0,063 | 6,57 |
| GARCH | 30 | 0,311 | 0,405 | 8,66 |
| FHS | 33 | 0,116 | 0,221 | 7,33 |

Como contraste, usé la pérdida cuantílica asimétrica de Gneiting (2011, p. 754, ec. 24). El normal obtuvo 2,777 pb y el histórico 2,781 pb, los dos menores. La diferencia es de 0,004 pb y no evalué su significancia. Se esperan 24,81 incumplimientos en esas fechas. GARCH se acerca más al objetivo y es mi principal alternativa si la volatilidad cambia con rapidez. El VaR histórico es más estable en esta muestra, aunque esa estabilidad también implica lentitud ante un cambio de régimen. Con ayuda de Codex, comprobé que recortar la serie en dos fechas mantenía idénticos los pronósticos anteriores al corte.

Sobre el tramo completo de 2.731 pronósticos históricos hubo 33 incumplimientos, con p de Kupiec de 0,289 y p de cobertura condicional de 0,410. El VaR histórico de muestra es 2,179 % y su ES es 2,817 %. El Z2 de 0,296 apunta a subestimación de la severidad de cola en el backtest histórico. Es una medida del ES y no un p-valor del VaR.

Antes de adoptar el límite, revisaría los peores episodios, la calibración en períodos tranquilos y volátiles y la sensibilidad a la ventana. Las cifras provienen de datos simulados y de una sola cartera. Comparé pronósticos fuera de muestra en fechas comunes y revisaría su calibración por régimen, siguiendo la motivación de Giacomini y White (2006, p. 1545). Si se reevalúan RiskMetrics y GARCH, usaría QLIKE con un proxy de varianza, pues el ruido puede distorsionar la comparación de volatilidades (Patton, 2011, pp. 247 y 250).
