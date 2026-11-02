# Instrucciones para trabajar en FIN443

Lee README.md, BITACORA_IA.md y los avances antes de modificar el código.

Repositorio principal: `diego19876/FIN-443-Diego-Martinez`. El Desafío 3 se implementará aquí. Esta decisión reemplaza la solicitud anterior de crear un repositorio separado.

## Contexto, pregunta y datos

Trabajo personal de Diego Martinez para FIN443, UAI 2026. La pregunta operativa del Desafío 2 es cómo obtener métricas correctas a partir de precios con formatos, fechas, faltantes y splits distintos. La siguiente etapa compara carteras y su desempeño dentro y fuera de muestra. La pregunta específica del proyecto grupal todavía no ha sido proporcionada: no inventarla.

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

## Reglas de trabajo y bitácora

Este AGENTS.md es la fuente única de instrucciones para Codex en el repositorio. Si se incorporan otras IA, mantener el mismo contenido en sus archivos de instrucciones, sin convenciones contradictorias. Registrar cuándo se añadieron estas instrucciones: no atribuir retroactivamente su versión actual a la especificación previa al código.

- En cada tarea de clase completada en este repositorio, actualiza BITACORA_IA.md y avance_clase_XX.md. Registra los pedidos, contribución de IA, cambios, evidencia de verificación, límites y pendientes.
- No inventes resultados, datos, referencias, pruebas ejecutadas ni decisiones del alumno. Identifica los prompts reconstruidos como resúmenes.
- Conserva argumentos de terminal y contratos de archivos del enunciado vigente. Usa rutas relativas. No cambies rf a un valor fijo.
- Mantén la autoría de pautas y pruebas del profesor. Corrige nuestra solución, sin reemplazarla por la pauta.
- No modifiques los datos originales. No subas datos, resultados CSV ni PDF de clases al repositorio.
- Documenta el uso de la pauta al realizar correcciones. Distingue formato correcto de cálculos correctos y validación pública de validación con otros datos.
- En backtests, evita información futura y documenta el momento en que se estiman y aplican los pesos.
- No subas credenciales, tokens ni información personal sensible.

