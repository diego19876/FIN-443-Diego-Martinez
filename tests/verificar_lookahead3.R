# Prueba de causalidad del programa real, en todos los rebalanceos públicos.
# Rscript tests/verificar_lookahead3.R precios_desafio3.csv
args_prueba <- commandArgs(trailingOnly = TRUE)
archivo <- normalizePath(if (length(args_prueba)) args_prueba[1] else "precios_desafio3.csv")
script <- normalizePath("desafio3.R")
temporal <- tempfile("fin443-causalidad-")
dir.create(temporal)
ejecutar <- function(entrada, etiqueta) {
  e <- new.env(parent = globalenv())
  e$commandArgs <- function(trailingOnly = FALSE) c(entrada, file.path(temporal, etiqueta), "0.05")
  invisible(capture.output(sys.source(script, envir = e)))
  e
}
total <- ejecutar(archivo, "total")
raw <- read.csv2(archivo, check.names = FALSE, stringsAsFactors = FALSE)
raw[[1]] <- as.Date(raw[[1]], "%d-%m-%Y")
mayor_pesos <- 0
mayor_retornos <- 0
for (j in seq_along(total$rebalanceos)) {
  t <- total$rebalanceos[j]
  # Conservar al menos un retorno posterior al rebalanceo bajo examen.
  corte <- total$fechas[min(t + 3, total$n)]
  d <- raw[raw[[1]] <= corte, , drop = FALSE]
  d[[1]] <- format(d[[1]], "%d-%m-%Y")
  entrada_corta <- file.path(temporal, "prefijo.csv")
  write.table(d, entrada_corta, sep = ";", dec = ",", row.names = FALSE, na = "")
  corto <- ejecutar(entrada_corta, "prefijo")
  fechas_objetivo <- total$fechas[total$rebalanceos[seq_len(j)]]
  fechas_cortas <- corto$fechas[corto$rebalanceos]
  stopifnot(identical(fechas_cortas, fechas_objetivo))
  for (k in seq_len(j)) for (nombre in total$orden_bt) {
    delta <- max(abs(total$historial_pesos[[k]][[nombre]] - corto$historial_pesos[[k]][[nombre]]))
    mayor_pesos <- max(mayor_pesos, delta)
    stopifnot(delta < 1e-9)
  }
  dias_bt <- seq_len(nrow(corto$rb))
  delta <- max(abs(total$rb[dias_bt, , drop = FALSE] - corto$rb),
               abs(total$rn[dias_bt, , drop = FALSE] - corto$rn))
  mayor_retornos <- max(mayor_retornos, delta)
  stopifnot(delta < 1e-9)
}
cat("OK: prefijos en", length(total$rebalanceos), "rebalanceos; diferencias máximas de pesos:",
    mayor_pesos, "; retornos brutos/netos:", mayor_retornos, "\n")

# Perturbar toda la historia futura y verificar que no cambie la ya realizada.
t <- total$rebalanceos[24]
fecha_corte <- total$fechas[t]
alterado <- raw
futuro <- which(alterado[[1]] > fecha_corte)
for (col in seq.int(2, ncol(alterado))) {
  alterado[futuro, col] <- alterado[futuro, col] *
    exp(seq(0.1, 0.8, length.out = length(futuro)) * col / ncol(alterado))
}
alterado[[1]] <- format(alterado[[1]], "%d-%m-%Y")
entrada_alterada <- file.path(temporal, "futuro_alterado.csv")
write.table(alterado, entrada_alterada, sep = ";", dec = ",", row.names = FALSE, na = "")
otro <- ejecutar(entrada_alterada, "futuro_alterado")
for (k in seq_len(24)) for (nombre in total$orden_bt) {
  stopifnot(max(abs(total$historial_pesos[[k]][[nombre]] - otro$historial_pesos[[k]][[nombre]])) < 1e-9)
}
filas <- seq_len(t - total$primer_rebalanceo)
stopifnot(max(abs(total$rb[filas, ] - otro$rb[filas, ])) < 1e-9,
          max(abs(total$rn[filas, ] - otro$rn[filas, ])) < 1e-9)
cat("OK: alterar precios posteriores al", format(fecha_corte),
    "no modifica los 24 rebalanceos previos ni sus retornos realizados.\n")

# Costos en el primer retorno de cada período, incluida compra inicial.
for (j in seq_along(total$rebalanceos)) {
  inicio <- total$rebalanceos[j] + 1 - total$primer_rebalanceo
  stopifnot(max(abs(total$rb[inicio, ] - total$rn[inicio, ] -
                   0.001 * total$rotaciones[j, ])) < 1e-12)
}
inicios <- total$rebalanceos + 1 - total$primer_rebalanceo
resto <- setdiff(seq_len(nrow(total$rb)), inicios)
stopifnot(max(abs(total$rb[resto, ] - total$rn[resto, ])) < 1e-12,
          all(total$rotaciones[-1, "EW"] == 0))
cat("OK: costos solo al primer día del período; compra inicial incluida y rotación EW posterior 0.\n")
