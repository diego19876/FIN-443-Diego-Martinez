# Desafío 3: carteras óptimas y un backtest sin mirar el futuro

Diego Martinez · FIN443 · UAI 2026 · 2 de noviembre de 2026

## Datos, método y resultados

Se usó precios_desafio3.csv con cinco activos y rf anual de 5 %. La limpieza eliminó dos fechas duplicadas, ajustó el split 2:1 de RETAIL del 08-04-2024 y rellenó cinco faltantes de ELECTRICA con el último precio disponible. Quedaron 1.302 retornos simples completos. El análisis dentro de muestra (IS) usa del 05-01-2021 al 31-12-2025. El backtest (BT) estima con 252 observaciones hasta cada cierre de mes, aplica los pesos desde el día siguiente y mantiene pesos objetivo diarios dentro del período. El primer rebalanceo fue el 31-12-2021; hubo 48 y no se rebalanceó en el último día del archivo.

Los porcentajes siguientes están redondeados a dos decimales; los Sharpe, a tres. La rotación es el promedio de la suma absoluta de cambios de pesos, sin dividir por dos y sin incluir la compra inicial. CAGR, volatilidad y caída máxima se calculan sin costos. El Sharpe neto incluye 0,1 % por unidad transada, incluida la compra inicial desde caja.

| Cartera | CAGR % | Vol. % | Sharpe | Caída máx. % | Rotación % | Sharpe neto |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| IS_MINVAR | 14,20 | 13,45 | 0,648 | 14,75 | - | - |
| IS_MAXSHARPE | 29,12 | 21,34 | 1,029 | 33,80 | - | - |
| IS_EW | 15,84 | 16,11 | 0,651 | 18,32 | - | - |
| IS_INVVOL | 15,70 | 15,11 | 0,676 | 16,30 | - | - |
| IS_ERC | 15,39 | 14,87 | 0,667 | 15,76 | - | - |
| BT_MINVAR | 14,51 | 13,43 | 0,670 | 14,64 | 6,96 | 0,663 |
| BT_EW | 20,23 | 16,08 | 0,877 | 14,40 | 0,00 | 0,876 |
| BT_INVVOL | 19,10 | 15,04 | 0,866 | 14,48 | 1,21 | 0,864 |
| BT_ERC | 18,81 | 14,83 | 0,860 | 14,27 | 1,59 | 0,858 |

## Dentro y fuera de muestra

IS estima pesos con toda la historia y los aplica a esos mismos retornos; BT solo estima con el pasado y cambia los pesos mensualmente. Además, las muestras de evaluación son distintas: BT empieza en 2022, luego de acumular la ventana de entrenamiento. En estos datos ninguna de las cuatro estrategias con BT pierde Sharpe respecto de su IS. No sería correcto afirmar que el backtest siempre empeora el resultado ni atribuir las diferencias exclusivamente al error de estimación. MinVar es la que menos mejora: pasa de 0,648 a 0,670; EW pasa de 0,651 a 0,877. MinVar queda más rezagada frente a EW en BT.

La sensibilidad de los pesos a la estimación sigue siendo relevante: MinVar tiene la mayor rotación mensual (6,96 %) y asigna 50,45 % a ELECTRICA en IS. DeMiguel et al. (2009) estudian restricciones sobre las normas de los pesos para mejorar el desempeño fuera de muestra ante error de estimación. Esto motiva revisar la concentración y estabilidad de nuestra solución, aunque aquí se mantienen las fórmulas sin restricciones exigidas por el enunciado. Ledoit y Wolf (2003) muestran que mejorar la estimación de covarianzas puede reducir la varianza fuera de muestra en los datos que analizan. Su trabajo respalda que la covarianza muestral es una fuente de incertidumbre; no implica que nuestro cálculo haya utilizado shrinkage, ni prueba que aplicarlo mejoraría este archivo.

## Riesgo, costos y elección de cartera

Máximo Sharpe logra 1,029 en IS, pero con una caída máxima de 33,80 % y posiciones cortas. En el primer rebalanceo su cartera tangente asigna 178,35 % a ELECTRICA y -106,26 % a COBRE: normalizar la suma a uno no evita un gran apalancamiento. El ejercicio no pide su BT porque estimar retornos esperados en ventanas cortas hace particularmente inestables esos pesos; el Sharpe optimizado en la misma muestra no demuestra rendimiento futuro.

INVVOL y ERC no son equivalentes: la primera usa volatilidades individuales y ERC incorpora también covarianzas para igualar los aportes al riesgo. Chaves et al. (2012) explican esta diferencia y métodos numéricos para ERC. Es consistente con nuestros pesos distintos y con que BT_ERC tenga menor volatilidad (14,83 %) y caída máxima (14,27 %) que BT_INVVOL (15,04 % y 14,48 %). El artículo respalda la distinción de construcción, no una superioridad universal de ERC.

Los costos reducen el Sharpe de todas las estrategias BT, pero no cambian su orden: EW, INVVOL, ERC y MinVar. La mayor reducción es la de MinVar, de 0,670 a 0,663; EW conserva un costo inicial aunque su rotación posterior sea cero. Para un cliente que priorice balancear riesgos y operar sin cortos elegiría ERC: combina menor volatilidad que EW con una caída máxima ligeramente menor y rotación moderada. Si el objetivo fuera únicamente el mejor Sharpe neto observado en esta muestra, elegiría EW (0,876). Esta decisión es condicional al objetivo del cliente y debe contrastarse en otros períodos antes de una recomendación real.

## Verificación

El programa pasó las 14 comprobaciones públicas. Un cálculo independiente en NumPy, usando Newton para ERC en lugar del descenso por coordenadas de R, reprodujo pesos y métricas con diferencia máxima inferior a 4e-12. Se probaron otro formato, orden inverso, duplicados, tildes, otra rf, tres activos y un caso simulado con inicio tardío y dos splits. Los pesos BT1 no cambiaron al truncar el archivo al 05-01-2022, conservando algunos días después del primer rebalanceo. Estas pruebas aportan evidencia de reproducibilidad y ausencia de anticipación en BT1; no equivalen a ejecutar los archivos ocultos del profesor.

## Referencias

Chaves, D., Hsu, J., Li, F., & Shakernia, O. (2012). Efficient algorithms for computing risk parity portfolio weights. *The Journal of Investing, 21*(3), 150-163. https://doi.org/10.3905/joi.2012.21.3.150

DeMiguel, V., Garlappi, L., Nogales, F. J., & Uppal, R. (2009). A generalized approach to portfolio optimization: Improving performance by constraining portfolio norms. *Management Science, 55*(5), 798-812. https://doi.org/10.1287/mnsc.1080.0986

Ledoit, O., & Wolf, M. (2003). Improved estimation of the covariance matrix of stock returns with an application to portfolio selection. *Journal of Empirical Finance, 10*(5), 603-621. https://doi.org/10.1016/S0927-5398(03)00007-0

Los PDF adjuntos de Chaves y DeMiguel son versiones de trabajo del mismo artículo (julio de 2012 y septiembre de 2008, respectivamente); las referencias anteriores identifican las publicaciones definitivas. Ledoit y Wolf corresponde a la versión publicada.
