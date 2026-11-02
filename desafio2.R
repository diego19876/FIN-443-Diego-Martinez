# =============================================================================
# Programación en Finanzas (FIN443) - UAI 2026 - Desafío 2
# Nombre y apellido: Diego Martinez
# -----------------------------------------------------------------------------
# CÓMO SE USA
#   - Usted lo prueba en RStudio: abra este archivo y haga Source (botón arriba a la
#     derecha). Lee precios_desafio2.csv de esta misma carpeta y crea salida.csv.
#   - El profesor lo ejecutará automáticamente, sin abrirlo, con OTROS archivos:
#         Rscript desafio2.R datos.csv salida.csv [rf]
#     Por eso no cambie las líneas de "args", no pida nada por teclado y no use
#     rutas fijas de su computador (C:/Users/...).
#   - salida.csv debe tener las columnas activo,cagr,vol,sharpe (vea el enunciado).
# =============================================================================

# Si se ejecuta en RStudio, se ubica en la carpeta de este archivo
if (requireNamespace("rstudioapi", quietly = TRUE) && rstudioapi::isAvailable()) {
  setwd(dirname(rstudioapi::getSourceEditorContext()$path))
}

args    <- commandArgs(trailingOnly = TRUE)
entrada <- if (length(args) >= 1) args[1] else "precios_desafio2.csv"   # para probar en RStudio
salida  <- if (length(args) >= 2) args[2] else "salida.csv"
rf      <- if (length(args) >= 3) as.numeric(args[3]) else 0.05

# ---- 1. Leer el archivo -----------------------------------------------------
# Contar campos respeta nombres entre comillas, incluso si contienen comas.
contar_campos <- function(separador) {
  conexion <- textConnection(readLines(entrada, n = 1, warn = FALSE))
  on.exit(close(conexion))
  count.fields(conexion, sep = separador, quote = '"',
               comment.char = "")
}
chileno <- contar_campos(";") > contar_campos(",")
datos <- read.table(
  entrada, header = TRUE, sep = if (chileno) ";" else ",",
  dec = if (chileno) "," else ".", na.strings = c("", "NA"),
  stringsAsFactors = FALSE, check.names = FALSE, comment.char = "",
  quote = '"', strip.white = TRUE, fileEncoding = "UTF-8-BOM"
)
fecha_original <- datos[[1]]
fecha <- NULL
for (formato in c("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y")) {
  candidata <- as.Date(fecha_original, format = formato)
  if (!anyNA(candidata)) {
    fecha <- candidata
    break
  }
}
datos[[1]] <- fecha
if (ncol(datos) < 2 || is.null(fecha) || anyNA(datos[[1]]) || !is.finite(rf)) {
  stop("Revise las fechas, las columnas de precios y la tasa rf.")
}
activos <- names(datos)[-1]

# ---- 2. Limpiar: orden, duplicados, splits, precios faltantes ---------------
datos <- datos[order(datos[[1]]), , drop = FALSE]
datos <- datos[!duplicated(datos[[1]]), , drop = FALSE]
fechas <- datos[[1]]
if (nrow(datos) < 2) stop("Se necesitan al menos dos fechas distintas.")

ajustar_splits <- function(precios) {
  disponibles <- which(!is.na(precios))
  if (length(disponibles) >= 2) {
    for (j in seq.int(2, length(disponibles))) {
      actual <- disponibles[j]
      anterior <- disponibles[j - 1]
      cociente <- precios[actual] / precios[anterior]
      factores <- 2:5
      # La pequeña tolerancia adicional evita errores de coma flotante
      # justo en los límites de 0,95 y 1,05.
      candidatos <- factores[abs(cociente * factores - 1) <= 0.05 + 1e-12]
      if (length(candidatos) > 0) {
        previos <- seq_len(actual - 1)
        precios[previos] <- precios[previos] / candidatos[1]
      }
    }
  }
  precios
}

rellenar <- function(precios) {
  for (i in seq_along(precios)) {
    if (i > 1 && is.na(precios[i])) precios[i] <- precios[i - 1]
  }
  precios
}

for (j in seq.int(2, ncol(datos))) {
  precios <- datos[[j]]
  if (!is.numeric(precios) || any(!is.finite(precios[!is.na(precios)])) ||
      any(precios <= 0, na.rm = TRUE)) {
    stop(paste("Precios inválidos en", names(datos)[j]))
  }
  datos[[j]] <- rellenar(ajustar_splits(precios))
}

# ---- 3. Calcular métricas por activo y de la cartera equiponderada ---------
P <- as.matrix(datos[, -1, drop = FALSE])
n <- nrow(P)
r <- P[-1, , drop = FALSE] / P[-n, , drop = FALSE] - 1

metricas_activo <- function(j) {
  disponibles <- which(!is.na(P[, j]))
  if (length(disponibles) < 2) {
    stop(paste("Datos insuficientes para calcular métricas de", activos[j]))
  }
  inicio <- disponibles[1]
  fin <- tail(disponibles, 1)
  anos <- as.numeric(fechas[fin] - fechas[inicio]) / 365.25
  retornos <- r[, j]
  retornos <- retornos[!is.na(retornos)]
  volatilidad <- sd(retornos) * sqrt(252)
  c(cagr = (P[fin, j] / P[inicio, j])^(1 / anos) - 1,
    vol = volatilidad,
    sharpe = (mean(retornos) * 252 - rf) / volatilidad)
}

metricas <- t(vapply(seq_along(activos), metricas_activo, numeric(3)))
resultado <- data.frame(activo = activos, cagr = metricas[, "cagr"],
                        vol = metricas[, "vol"], sharpe = metricas[, "sharpe"],
                        row.names = NULL, check.names = FALSE)

# Un activo que recién empieza no tiene retorno en su primer día.
# Los días sin ningún retorno disponible se excluyen del cálculo estadístico.
rp <- rowMeans(r, na.rm = TRUE)
rp <- rp[!is.na(rp)]
anos_cartera <- as.numeric(fechas[n] - fechas[1]) / 365.25
vol_cartera <- sd(rp) * sqrt(252)
resultado <- rbind(resultado, data.frame(
  activo = "CARTERA_EW",
  cagr = prod(1 + rp)^(1 / anos_cartera) - 1,
  vol = vol_cartera,
  sharpe = (mean(rp) * 252 - rf) / vol_cartera
))

# ---- 4. Escribir la salida (no cambie el formato) ---------------------------
# Fracciones, sin redondear: write.csv usa comas y punto decimal.
write.csv(resultado, salida, row.names = FALSE)
