# Programación en Finanzas — FIN443, UAI 2026

Repositorio personal de Diego Martinez: código, pautas y avances semanales.
Los datos originales, los resultados generados y los PDF de clases permanecen fuera del repositorio.

## Contenido

- `desafio2.R`: solución del lector de precios y métricas, con R base.
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

Desafío 2 implementado y verificado con el archivo público y pruebas adicionales. Comparación con la pauta a `rf = 0.03`: diferencia máxima entre métricas igual a cero. El código del Desafío 3 aún no está implementado en este repositorio.

