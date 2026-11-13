# =============================================================================
# Programación en Finanzas (FIN443) - UAI 2026 - Desafío 3: carteras y backtest
# Nombre y apellido: Diego Martinez
# R base. Pieza 1 reutilizada de desafio2.R, revisada con la pauta comentada.
# Uso: Rscript desafio3.R datos.csv carpeta_salida [rf]
# =============================================================================
if (requireNamespace("rstudioapi", quietly = TRUE) && rstudioapi::isAvailable()) {
  setwd(dirname(rstudioapi::getSourceEditorContext()$path))
}
args    <- commandArgs(trailingOnly = TRUE)
entrada <- if (length(args) >= 1) args[1] else "precios_desafio3.csv"
carpeta <- if (length(args) >= 2) args[2] else "salida"
rf      <- if (length(args) >= 3) as.numeric(args[3]) else 0.05
dir.create(carpeta, showWarnings = FALSE, recursive = TRUE)

# ---- 1. Leer y limpiar (pieza 1: su desafío 2) ------------------------------
leer_precios <- function(archivo) {
  cabecera <- readLines(archivo, n = 1, warn = FALSE, encoding = "UTF-8")
  campos <- function(sep) {
    con <- textConnection(cabecera)
    on.exit(close(con))
    count.fields(con, sep = sep, quote = '"', comment.char = "")
  }
  chileno <- campos(";") > campos(",")
  d <- read.table(archivo, header = TRUE, sep = if (chileno) ";" else ",",
                  dec = if (chileno) "," else ".", na.strings = c("", "NA"),
                  stringsAsFactors = FALSE, check.names = FALSE,
                  comment.char = "", quote = '"', strip.white = TRUE,
                  fileEncoding = "UTF-8-BOM")
  if (ncol(d) < 2 || nrow(d) < 2) stop("Faltan fechas o activos.")
  fechas <- NULL
  for (fmt in c("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y")) {
    f <- as.Date(d[[1]], format = fmt)
    if (!anyNA(f)) { fechas <- f; break }
  }
  if (is.null(fechas)) stop("Formato de fecha no reconocido.")
  d[[1]] <- fechas
  d <- d[order(d[[1]]), , drop = FALSE]
  d <- d[!duplicated(d[[1]]), , drop = FALSE]
  for (j in seq.int(2, ncol(d))) {
    p <- d[[j]]
    if (all(is.na(p))) stop(paste("Activo sin precios:", names(d)[j]))
    if (!is.numeric(p) || any(!is.finite(p[!is.na(p)])) ||
        any(p <= 0, na.rm = TRUE)) stop("Los precios deben ser positivos.")
    disponibles <- which(!is.na(p))
    if (length(disponibles) >= 2) {
      for (i in seq.int(2, length(disponibles))) {
        t <- disponibles[i]
        cociente <- p[t] / p[disponibles[i - 1]]
        ks <- (2:5)[abs(cociente * (2:5) - 1) <= 0.05 + 1e-12]
        if (length(ks)) p[seq_len(t - 1)] <- p[seq_len(t - 1)] / ks[1]
      }
    }
    for (i in seq.int(2, length(p))) if (is.na(p[i])) p[i] <- p[i - 1]
    d[[j]] <- p
  }
  rownames(d) <- NULL
  d
}
if (!is.finite(rf)) stop("rf debe ser una tasa anual numérica.")
datos <- leer_precios(entrada)
activos <- names(datos)[-1]

# ---- 2. Retornos diarios en los días en que TODOS los activos tienen dato ---
# Se calculan retornos ANTES de filtrar casos completos.
P <- as.matrix(datos[, -1, drop = FALSE])
R <- P[-1, , drop = FALSE] / P[-nrow(P), , drop = FALSE] - 1
fechas <- datos[[1]][-1]
completos <- complete.cases(R)
R <- R[completos, , drop = FALSE]
fechas <- fechas[completos]
n <- nrow(R)
N <- ncol(R)
if (n < 253 || any(!is.finite(R))) stop("Se requieren al menos 253 retornos completos.")

# ---- 3. Dentro de muestra ---------------------------------------------------
pesos_erc <- function(Sigma, tolerancia = 1e-11) {
  # Descenso cíclico por coordenadas del objetivo convexo del enunciado.
  # Escalar toda Sigma por una constante no altera los pesos normalizados.
  S <- Sigma / mean(diag(Sigma))
  b <- rep(1 / ncol(S), ncol(S))
  y <- sqrt(b / diag(S))
  for (iteracion in seq_len(10000)) {
    for (i in seq_along(y)) {
      a <- S[i, i]
      c <- sum(S[i, ] * y) - a * y[i]
      raiz <- sqrt(c * c + 4 * a * b[i])
      # Formas equivalentes de la raíz positiva: evitar cancelación numérica.
      y[i] <- if (c >= 0) 2 * b[i] / (c + raiz) else (raiz - c) / (2 * a)
    }
    w <- y / sum(y)
    Sw <- drop(S %*% w)
    cr <- w * Sw / sum(w * Sw)
    if (max(abs(cr - b)) < tolerancia) return(w)
  }
  stop("ERC no alcanzó la precisión requerida.")
}

estimar_pesos <- function(retornos, incluir_tangente = FALSE) {
  Sigma <- cov(retornos) * 252
  if (any(diag(Sigma) <= 0)) stop("Activo con varianza nula en la ventana.")
  unos <- rep(1, ncol(retornos))
  minvar <- drop(solve(Sigma, unos))
  minvar <- minvar / sum(minvar)
  invvol <- 1 / apply(retornos, 2, sd)
  invvol <- invvol / sum(invvol)
  salida <- list(MINVAR = minvar, EW = unos / length(unos),
                 INVVOL = invvol, ERC = pesos_erc(Sigma))
  if (incluir_tangente) {
    exceso <- colMeans(retornos) * 252 - rf
    tangente <- drop(solve(Sigma, exceso))
    if (!is.finite(sum(tangente)) || abs(sum(tangente)) < .Machine$double.eps) {
      stop("La cartera tangente no puede normalizarse.")
    }
    salida$MAXSHARPE <- tangente / sum(tangente)
  }
  salida
}

calcular_metricas <- function(retornos, inicio, fin) {
  anos <- as.numeric(fin - inicio) / 365.25
  riqueza <- c(1, cumprod(1 + retornos))
  vol <- sd(retornos) * sqrt(252)
  c(cagr = tail(riqueza, 1)^(1 / anos) - 1, vol = vol,
    sharpe = (mean(retornos) * 252 - rf) / vol,
    mdd = max(1 - riqueza / cummax(riqueza)))
}

is_pesos <- estimar_pesos(R, incluir_tangente = TRUE)
orden_is <- c("MINVAR", "MAXSHARPE", "EW", "INVVOL", "ERC")
metricas <- do.call(rbind, lapply(orden_is, function(nombre) {
  r <- drop(R %*% is_pesos[[nombre]])
  m <- calcular_metricas(r, fechas[1], fechas[n])
  data.frame(cartera = paste0("IS_", nombre), as.list(m),
             rotacion = NA_real_, sharpe_neto = NA_real_, row.names = NULL)
}))

# ---- 4. Backtest: ventana pasada de 252 filas, pesos desde el día siguiente --
mes <- format(fechas, "%Y-%m")
cierres <- which(!duplicated(mes, fromLast = TRUE))
rebalanceos <- cierres[cierres >= 252 & cierres < n]
if (!length(rebalanceos)) stop("No hay cierre de mes con 252 retornos y días posteriores.")
primer_rebalanceo <- rebalanceos[1]
orden_bt <- c("MINVAR", "EW", "INVVOL", "ERC")
rb <- matrix(NA_real_, n - primer_rebalanceo, length(orden_bt),
             dimnames = list(NULL, orden_bt))
rn <- rb
rotaciones <- matrix(0, length(rebalanceos), length(orden_bt),
                      dimnames = list(NULL, orden_bt))
historial_pesos <- vector("list", length(rebalanceos))
anteriores <- NULL
for (j in seq_along(rebalanceos)) {
  t <- rebalanceos[j]
  ventana <- R[seq.int(t - 251, t), , drop = FALSE]
  objetivos <- estimar_pesos(ventana, incluir_tangente = (j == 1))
  historial_pesos[[j]] <- objetivos
  fin <- if (j < length(rebalanceos)) rebalanceos[j + 1] else n
  dias <- seq.int(t + 1, fin)
  filas_bt <- dias - primer_rebalanceo
  for (nombre in orden_bt) {
    w <- objetivos[[nombre]]
    bruto <- drop(R[dias, , drop = FALSE] %*% w)
    Tj <- if (j == 1) sum(abs(w)) else sum(abs(w - anteriores[[nombre]]))
    neto <- bruto
    neto[1] <- neto[1] - 0.001 * Tj
    rb[filas_bt, nombre] <- bruto
    rn[filas_bt, nombre] <- neto
    rotaciones[j, nombre] <- Tj
  }
  anteriores <- objetivos
}
for (nombre in orden_bt) {
  m <- calcular_metricas(rb[, nombre], fechas[primer_rebalanceo], fechas[n])
  # Si solo hay un rebalanceo, no hay cambios posteriores: rotación 0.
  rot <- if (nrow(rotaciones) > 1) mean(rotaciones[-1, nombre]) else 0
  neto <- rn[, nombre]
  shp_neto <- (mean(neto) * 252 - rf) / (sd(neto) * sqrt(252))
  metricas <- rbind(metricas, data.frame(cartera = paste0("BT_", nombre),
                    as.list(m), rotacion = rot, sharpe_neto = shp_neto,
                    row.names = NULL))
}

# ---- 5. Escribir la salida (no cambie el formato) ---------------------------
orden_pesos <- c("MINVAR", "MAXSHARPE", "INVVOL", "ERC")
pesos <- do.call(rbind, lapply(c("IS_", "BT1_"), function(prefijo) {
  fuente <- if (prefijo == "IS_") is_pesos else historial_pesos[[1]]
  do.call(rbind, lapply(orden_pesos, function(nombre) {
    data.frame(cartera = paste0(prefijo, nombre), activo = activos,
               peso = unname(fuente[[nombre]]), row.names = NULL)
  }))
}))
write.csv(pesos, file.path(carpeta, "pesos.csv"), row.names = FALSE)
write.csv(metricas, file.path(carpeta, "metricas.csv"), row.names = FALSE)
cat("Retornos completos:", n, "| Primer rebalanceo:",
    format(fechas[primer_rebalanceo]), "| Rebalanceos:", length(rebalanceos), "\n")
