# Programación en Finanzas — FIN443, UAI 2026

Este es mi repositorio de FIN443. Aquí reúno mi código, las pautas del profesor y mis avances semanales.
Repositorio de GitHub: https://github.com/diego19876/FIN-443-Diego-Martinez.
El repositorio reúne las piezas de los desafíos semanales. El lector del Desafío 4 es la base de datos y retornos para los desafíos 5 y 6.
Los datos originales, los resultados generados y los PDF de clases permanecen fuera del repositorio.

## Contenido

- `desafio2.R`: solución del lector de precios y métricas, con R base.
- `desafio3.R`: carteras IS, pesos BT1, backtest mensual y costos, con R base.
- `desafio3_corregido.R`: revisión separada del Desafío 3 con la pauta del profesor.
- `desafio4.py`: lector regional y medición de riesgo para la pieza 3.
- `probar_mi_entrega4.R` y `tests/verificar_desafio4.py`: prueba pública y contraste independiente del Desafío 4.
- `memo_desafio4.md` y `referencias_desafio4.md`: memo fuente y referencias con la decisión que respalda cada artículo.
- `defensa_desafio4.md`: ejemplos de la cartera y guía de defensa.
- `probar_mi_entrega3.R`: prueba pública del profesor para el Desafío 3.
- `tests/verificar_desafio3.py`: contraste independiente con NumPy y pruebas de robustez.
- `informe_desafio3.md`: fuente del informe de dos páginas.
- `RESPUESTAS_DESAFIO3.md`: ocho cifras y texto para el formulario.
- `referencias_desafio3.md`: procedencia y versiones de los tres artículos.
- `probar_mi_entrega.R`: prueba pública de formato proporcionada por el profesor.
- `pauta_desafio2_comentada.R`: pauta comentada del profesor, publicada en la Clase 3.
- `avance_clase_XX.md`: avances de cada clase.
- `BITACORA_IA.md`: uso de IA, prompts reconstruidos, decisiones, verificaciones y pendientes; incluye el prompt general para continuar.
- `AGENTS.md`: instrucciones para mantener la bitácora al trabajar en el repositorio.

Conservo las pautas y pruebas del profesor como referencia y respeto su autoría. Mantengo mis soluciones en archivos separados. Usé OpenAI Codex para elaborar y revisar el código.

## Ejecutar el desafío 2

Requiere R. El cálculo usa únicamente R base; la integración opcional con RStudio utiliza `rstudioapi` si está instalado.
Colocar `precios_desafio2.csv` en la raíz o indicar la ruta de otro archivo compatible:

```sh
Rscript desafio2.R precios_desafio2.csv salida.csv
Rscript desafio2.R precios_desafio2.csv salida_003.csv 0.03
Rscript probar_mi_entrega.R
Rscript pauta_desafio2_comentada.R precios_desafio2.csv pauta_003.csv 0.03
```

La salida incluye `activo,cagr,vol,sharpe`, una fila por activo y `CARTERA_EW`. CAGR y volatilidad se escriben en fracción; Sharpe no se expresa como porcentaje.

El lector acepta los formatos internacional y chileno. Ordena fechas, elimina duplicados, ajusta splits con factores 2 a 5, rellena faltantes con el último precio disponible y conserva los faltantes iniciales.

## Estado

Desafíos 2, 3, 4 y 5 implementados. Bloque 1 de la Clase 6 resuelto; el correo está preparado, sin envío confirmado. El Desafío 3 pasó las 14 comprobaciones públicas; una implementación independiente en NumPy reprodujo pesos y métricas con diferencia máxima menor que 4e-12. Los archivos ocultos del profesor no están disponibles.

## Ejecutar el desafío 3

Colocar el CSV original en la raíz, conservándolo fuera de Git:

```sh
Rscript desafio3.R precios_desafio3.csv salida_desafio3
Rscript desafio3.R precios_desafio3.csv salida_desafio3_rf03 0.03
Rscript probar_mi_entrega3.R
python tests/verificar_desafio3.py precios_desafio3.csv
```

El programa a entregar depende solo de R base. La validación independiente requiere Python y NumPy. El informe se genera con `python scripts/generar_informe_desafio3.py` (ReportLab) a partir de su fuente Markdown, después de ejecutar el programa. Los archivos finales para Webcursos se guardan localmente en `entrega_desafio3/`; los datos, CSV generados y PDF no se publican en GitHub.

## Ejecutar el Desafío 4

Requiere Python 3 con NumPy y pandas. En la carpeta de trabajo, coloca `desafio4.py`, `cartera.csv` (columnas `id,peso`) y los siete CSV del curso:

- `maestro_emisores.csv`
- `precios_SCL.csv`
- `precios_NYC.csv`
- `tipo_cambio.csv`
- `eventos_corporativos.csv`
- `salidas_de_bolsa.csv`
- `parametros_riesgo.csv`

Ejecuta `python3 desafio4.py` sin argumentos. Escribe `riesgo.csv` con 31 métricas, `calidad_datos.csv` con 9 indicadores y `backtest.csv` con 13 columnas. El backtest usa solo el pasado para estimar cada VaR. FHS deja las primeras `ventana` filas vacías hasta contar con suficientes pérdidas estandarizadas.

La entrega empaquetada se probó con 17.305.011 filas en 16,8 segundos en este equipo. Desde la raíz del repo, `python3 tests/verificar_desafio4.py` ejecuta un mercado sintético con resultados calculables a mano y filas invertidas. La prueba pública `Rscript probar_mi_entrega4.R` se ejecuta en la carpeta de trabajo con los CSV. Se compararon las 31 métricas y el backtest con un recálculo en R a partir de las series reconstruidas. La diferencia máxima fue 4,55e-13. Los datos ocultos del profesor no están disponibles.

El memo fuente se convierte a PDF con `python3 scripts/generar_memo_desafio4.py` desde el repo, con ReportLab instalado. El archivo se guarda en `entrega_desafio4/memo_riesgo.pdf`.

## Reutilizar el lector en los desafíos 5 y 6

Desde la carpeta con los archivos de datos, importa `construir_series` desde `desafio4.py`. Acepta un DataFrame con `id,peso` y devuelve fechas ordenadas, retornos de cartera, retornos del índice equiponderado e indicadores de calidad. El quinto elemento contiene escenarios de auditoría si se activa `auditar=True`. Importar el módulo no ejecuta el programa ni genera CSV.

```python
import pandas as pd
from desafio4 import construir_series

cartera = pd.read_csv("cartera.csv", dtype={"id": str})
fechas, retornos_cartera, retornos_mercado, calidad, _ = construir_series(cartera)
```

El lector une los calendarios de ambas bolsas, conserva la versión más alta por fecha y ticker, cruza vigencias por emisor, toma el último tipo de cambio disponible e incorpora splits, dividendos y retornos de salida. Los retornos diarios son simples y están en USD. Las series abarcan todo el calendario y el análisis de riesgo del Desafío 4 filtra por `inicio` después de reconstruir los retornos. Si un desafío posterior requiere otro período o formato, aplica su enunciado sobre las series y conserva estas reglas de origen.

## Ejecutar el Desafío 5

`python3 desafio5.py` se ejecuta sin argumentos en la carpeta de las seis bases del D4, cartera.csv y los nuevos tasas_mercado.csv, bonos_fondo.csv y parametros_D5.csv. Requiere NumPy, pandas y SciPy. El lector propio D4 está integrado para que el ejecutable sea autónomo. No cambia de directorio. Genera las 35 métricas de resultados_D5.csv y los once indicadores de calidad_tasas.csv según el contrato oficial.

El notebook sincronizado, la cartera, el memo, los PDF y el respaldo numérico se mantienen fuera del repositorio. Se ejecutó la prueba pública completa, un contraste independiente en R y casos alternativos. Las cifras adicionales del memo se producen con un auditor separado. Ver avance_clase_05.md y BITACORA_IA.md para alcance, cambios de convenciones respecto del avance de sala y pendientes personales de registro de referencias y video. No se dispone de los datos ocultos D5.


## Verificar el Desafío 5 con otros datos

La prueba integral genera todos los CSV sintéticos, ejecuta el programa en un proceso nuevo y compara las métricas con un lector escalar y un cálculo independiente en R. Conserva entradas, salidas y logs fuera de Git. Requiere NumPy, pandas, SciPy y Rscript.

```sh
python3 tests/verificar_desafio5_integral.py desafio5.py /tmp/fin443_d5_evidencia
```

Las pruebas propias no equivalen a los mercados ocultos del profesor. El registro de referencias y el enlace del video se completaron después de las primeras auditorías; no se ha acreditado el envío final de la tarea. El estado actualizado consta al final de BITACORA_IA.md y avance_clase_05.md.

## Clase 6 — Bloque 1

Colocar fondo_clase6.csv junto al código y ejecutar con NumPy y pandas:

```sh
python3 clase6_bloque1.py
```

El programa estima con los días 1–1000 y prueba con 1001–1500. Calcula MCO dentro y fuera de muestra, ridge con lambda 3000 y MCO con senal_revisada. El promedio y la estandarización se calculan exclusivamente en estimación. Imprime porcentajes y guarda resultados_clase6_bloque1.csv en fracción.

```sh
python3 tests/verificar_clase6_bloque1.py fondo_clase6.csv --evidencia /tmp/fin443_clase6_evidencia
```

El contraste independiente usa R y vuelve a leer cada CSV. Los datos públicos y sintéticos, sus resultados y los adjuntos del correo permanecen fuera de Git. Ver avance_clase_06.md para decisiones y límites. La entrega del bloque requiere enviar el correo con código y prompts; preparar los archivos no confirma su envío.
