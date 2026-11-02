# Programación en Finanzas — FIN443, UAI 2026

Repositorio personal de Diego Martinez: código, pautas y avances semanales.
Repositorio de GitHub: https://github.com/diego19876/FIN-443-Diego-Martinez.
El Desafío 3 se desarrollará en este mismo repositorio, junto con los avances del curso.
Los datos originales, los resultados generados y los PDF de clases permanecen fuera del repositorio.

## Contenido

- `desafio2.R`: solución del lector de precios y métricas, con R base.
- `desafio3.R`: carteras IS, pesos BT1, backtest mensual y costos, con R base.
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

Las pautas y pruebas del profesor se conservan como referencia, con su autoría. La solución propia se mantiene por separado. Se utilizó OpenAI Codex para elaborar y revisar el código.

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

Desafíos 2 y 3 implementados. El Desafío 3 pasó las 14 comprobaciones públicas; una implementación independiente en NumPy reprodujo pesos y métricas con diferencia máxima menor que 4e-12. Los archivos ocultos del profesor no están disponibles.

## Ejecutar el desafío 3

Colocar el CSV original en la raíz, conservándolo fuera de Git:

```sh
Rscript desafio3.R precios_desafio3.csv salida_desafio3
Rscript desafio3.R precios_desafio3.csv salida_desafio3_rf03 0.03
Rscript probar_mi_entrega3.R
python tests/verificar_desafio3.py precios_desafio3.csv
```

El programa a entregar depende solo de R base. La validación independiente requiere Python y NumPy. El informe se genera con `python scripts/generar_informe_desafio3.py` (ReportLab) a partir de su fuente Markdown, después de ejecutar el programa. Los archivos finales para Webcursos se guardan localmente en `entrega_desafio3/`; los datos, CSV generados y PDF no se publican en GitHub.

