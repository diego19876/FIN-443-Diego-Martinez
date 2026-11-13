# =============================================================================
# Programación en Finanzas (FIN443) - UAI 2026
# PAUTA COMENTADA DEL DESAFÍO 3 (se publica después de corregir, antes de la Clase 4)
# -----------------------------------------------------------------------------
# Este es el programa con el que se corrigió el desafío 3 (archivo público y ocultos).
#
# Cómo usarla:
#   1. Ejecútela con precios_desafio3.csv y compare con SUS pesos.csv y metricas.csv.
#   2. Si difieren, busque en qué PASO se separan (lea los comentarios "TRAMPA").
#   3. Corrija SU programa: no lo reemplace por este. Es la pieza 2 de su prototipo.
#
# Se usa igual que su desafío:   Rscript pauta_desafio3_comentada.R datos.csv carpeta_salida [rf]
# En RStudio: abra el archivo y haga Source (usa precios_desafio3.csv de esta carpeta y
# escribe en la carpeta "salida"). Solo usa R base.
# =============================================================================

if (requireNamespace("rstudioapi", quietly = TRUE) && rstudioapi::isAvailable()) {
  setwd(dirname(rstudioapi::getSourceEditorContext()$path))
}
args    <- commandArgs(trailingOnly = TRUE)
entrada <- if (length(args) >= 1) args[1] else "precios_desafio3.csv"
carpeta <- if (length(args) >= 2) args[2] else "salida"
rf      <- if (length(args) >= 3) as.numeric(args[3]) else 0.05
dir.create(carpeta, showWarnings = FALSE, recursive = TRUE)   # TRAMPA: la carpeta puede no existir

# ---- PIEZA 1 (desafío 2): leer y limpiar. Igual que la pauta del desafío 2 ----
leer_precios <- function(archivo) {
  l1 <- readLines(archivo, n = 1, warn = FALSE, encoding = "UTF-8")
  sep <- if (lengths(regmatches(l1, gregexpr(";", l1))) > lengths(regmatches(l1, gregexpr(",", l1)))) ";" else ","
  dec <- if (sep == ";") "," else "."
  d <- read.table(archivo, sep = sep, dec = dec, header = TRUE, na.strings = c("", "NA"),
                  stringsAsFactors = FALSE, check.names = FALSE, strip.white = TRUE, quote = "\"")
  names(d)[1] <- "Fecha"
  for (fmt in c("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y")) { f <- as.Date(d$Fecha, format = fmt); if (!anyNA(f)) break }
  if (anyNA(f)) stop("Formato de fecha no reconocido")
  d$Fecha <- f
  for (j in 2:ncol(d)) d[[j]] <- as.numeric(d[[j]])
  d <- d[order(d$Fecha), ]
  d <- d[!duplicated(d$Fecha), ]
  rownames(d) <- NULL
  d
}
ajustar_splits <- function(p, tol = 0.05, ks = 2:5) {
  ult <- NA
  for (i in seq_along(p)) {
    if (is.na(p[i])) next
    if (!is.na(ult)) for (k in ks) if (abs(p[i] / ult * k - 1) <= tol) { p[1:(i - 1)] <- p[1:(i - 1)] / k; break }
    ult <- p[i]
  }
  p
}
locf <- function(x) { for (i in seq_along(x)[-1]) if (is.na(x[i])) x[i] <- x[i - 1]; x }

# ---- Matriz de retornos en "casos completos" -----------------------------------
# Markowitz necesita una matriz de covarianzas de TODOS los activos con los MISMOS días.
# Por eso se usan solo los días en que todos tienen retorno.
# TRAMPA: en oculto 2, TECNO empezaba en 2021-03: los días anteriores se descartan para todos.
# TRAMPA: cov(R, use = "pairwise") da otra matriz (y puede no ser invertible). No es lo pedido.
retornos_completos <- function(archivo) {
  d <- leer_precios(archivo)
  act <- names(d)[-1]
  P <- sapply(act, function(a) locf(ajustar_splits(d[[a]])))
  P <- matrix(P, ncol = length(act), dimnames = list(NULL, act))
  R <- P[-1, , drop = FALSE] / P[-nrow(P), , drop = FALSE] - 1
  ok <- complete.cases(R)
  list(R = R[ok, , drop = FALSE], fechas = d$Fecha[-1][ok], activos = act)
}

# ---- PIEZA 2 (desafío 3): carteras -------------------------------------------
# solve(S, b) resuelve S x = b. Es más estable que solve(S) %*% b.
pesos_minvar <- function(R) {
  S <- cov(R) * 252                         # covarianza MUESTRAL anualizada
  x <- solve(S, rep(1, ncol(R)))
  x / sum(x)                                # normalizar: los pesos suman 1
}
pesos_maxsharpe <- function(R, rf) {
  S <- cov(R) * 252
  mu <- colMeans(R) * 252                   # TRAMPA: mu y rf deben estar en la misma unidad (anual)
  x <- solve(S, mu - rf)                    # TRAMPA: sin restar rf se obtiene otra cartera
  x / sum(x)
}
# TRAMPA: la anualización (×252) no cambia los pesos de MinVar, pero en MaxSharpe sí importa
# que mu, Sigma y rf estén en la misma escala.

pesos_invvol <- function(R) {               # inversa de la volatilidad ("paridad de riesgo ingenua")
  x <- 1 / apply(R, 2, sd)                  # TRAMPA: es 1/sigma, no 1/sigma^2 (eso sería otra cartera)
  x / sum(x)                                # no usa mu ni las correlaciones: pesos siempre positivos
}

# Paridad de riesgo (ERC, "equal risk contribution"): cada activo aporta LO MISMO al riesgo.
#   Contribución al riesgo del activo i:  CR_i = w_i * (S w)_i / (w' S w)   (suman 1)
#   ERC pide CR_i = 1/n para todos. No hay fórmula cerrada: se resuelve numéricamente.
#   Truco (Spinu, 2013): minimizar 0,5 y'Sy - (1/n) sum(log y_i) con y > 0 y luego w = y / sum(y).
#   La condición de primer orden es y_i (S y)_i = 1/n: exactamente "igual contribución".
#   Se resuelve un activo a la vez (descenso por coordenadas): cada paso es una ecuación cuadrática.
# TRAMPA: ERC no es la inversa de la volatilidad. Coinciden solo si todas las correlaciones son
#   iguales. Verifique su resultado: calcule las CR_i y compruebe que valen 1/n.
pesos_erc <- function(R, tol = 1e-12, max_iter = 10000) {
  S <- cov(R) * 252; n <- ncol(R)
  y <- 1 / sqrt(diag(S))                    # se parte de la inversa de la volatilidad
  for (it in seq_len(max_iter)) {
    y_old <- y
    for (i in seq_len(n)) {                 # S_ii y_i^2 + b y_i - 1/n = 0, raíz positiva
      b <- sum(S[i, -i] * y[-i])
      y[i] <- (-b + sqrt(b^2 + 4 * S[i, i] / n)) / (2 * S[i, i])
    }
    if (max(abs(y - y_old)) < tol) break
  }
  y / sum(y)
}
contrib_riesgo <- function(w, R) { S <- cov(R); as.vector(w * (S %*% w)) / sum(w * (S %*% w)) }

# Caída máxima (max drawdown): la mayor pérdida desde un máximo previo de la riqueza.
# TRAMPA: la riqueza parte en W0 = 1 (antes del primer retorno). No es (máx - mín) / máx de toda
#   la serie: el mínimo tiene que venir DESPUÉS del máximo.
caida_maxima <- function(rp) {
  W <- c(1, cumprod(1 + rp))
  max(1 - W / cummax(W))                    # fracción positiva (0,15 = cayó 15%)
}
metricas <- function(rp, fechas, rf, fecha_inicio = fechas[1]) {
  anos <- as.numeric(max(fechas) - fecha_inicio) / 365.25
  vol <- sd(rp) * sqrt(252)
  c(cagr = prod(1 + rp)^(1 / anos) - 1, vol = vol, sharpe = (mean(rp) * 252 - rf) / vol,
    mdd = caida_maxima(rp))
}
COSTO <- 0.001   # 0,1% (10 puntos base) por cada unidad transada. TRAMPA: es 0.001, no 0.1

desafio3 <- function(archivo, rf = 0.05, ventana = 252, costo = COSTO) {
  z <- retornos_completos(archivo); R <- z$R; fe <- z$fechas; act <- z$activos; n <- length(act)

  # (a) DENTRO DE MUESTRA: pesos con toda la historia, aplicados a esa misma historia.
  #     Mira el futuro por construcción: sirve como referencia, no como resultado alcanzable.
  w_is <- list(MINVAR = pesos_minvar(R), MAXSHARPE = pesos_maxsharpe(R, rf), EW = rep(1 / n, n),
               INVVOL = pesos_invvol(R), ERC = pesos_erc(R))
  is <- t(sapply(w_is, function(w) metricas(as.vector(R %*% w), fe, rf)))   # EW = 1/N con rebalanceo diario
  cat("Contribuciones al riesgo de IS_ERC (deben ser todas 1/n):", round(contrib_riesgo(w_is$ERC, R), 4), "\n")

  # (b) BACKTEST: rebalanceo el último día con datos de cada mes.
  mes <- format(fe, "%Y-%m")
  fin_mes <- which(c(mes[-1] != mes[-length(mes)], TRUE))   # último día de cada mes (el último día de R también)
  reb <- fin_mes[fin_mes >= ventana &                       # al menos 252 filas hasta t
                 fin_mes < length(fe)]                      # y con días después para invertir
  carteras_bt <- c("MINVAR", "EW", "INVVOL", "ERC")
  regla <- list(MINVAR = pesos_minvar, EW = function(Rv) rep(1 / ncol(Rv), ncol(Rv)),
                INVVOL = pesos_invvol, ERC = pesos_erc)
  r_bt <- setNames(lapply(carteras_bt, function(k) numeric(0)), carteras_bt)
  r_net <- r_bt; giro <- r_bt; w_prev <- list(); f_bt <- as.Date(character(0)); w1 <- NULL
  for (j in seq_along(reb)) {
    t <- reb[j]
    Rv <- R[(t - ventana + 1):t, , drop = FALSE]
    # ^ CLAVE: la ventana TERMINA en t. Si termina después de t (por ejemplo, al final del mes
    #   que se va a invertir) hay look-ahead: el corrector lo detecta con un archivo que tiene
    #   el mismo pasado y otro futuro (sus pesos BT1 no deberían cambiar, y cambian).
    if (j == 1) w1 <- list(MINVAR = pesos_minvar(Rv), MAXSHARPE = pesos_maxsharpe(Rv, rf),
                           INVVOL = pesos_invvol(Rv), ERC = pesos_erc(Rv))   # BT1 = primer rebalanceo
    fin <- if (j < length(reb)) reb[j + 1] else length(fe)
    idx <- (t + 1):fin                                      # desde el día SIGUIENTE a t hasta el próximo rebalanceo
    for (k in carteras_bt) {
      w <- regla[[k]](Rv)
      # Rotación del rebalanceo j: T_j = sum |w_j - w_{j-1}|. En el primero se compra desde caja: sum |w_1|.
      # Simplificación del enunciado: se compara con los pesos OBJETIVO anteriores (se ignora la deriva).
      T_j <- if (j == 1) sum(abs(w)) else sum(abs(w - w_prev[[k]]))
      r <- as.vector(R[idx, , drop = FALSE] %*% w)          # pesos fijos = rebalanceo diario a esos pesos
      rn <- r; rn[1] <- rn[1] - costo * T_j                 # el costo se paga el PRIMER día del período
      r_bt[[k]] <- c(r_bt[[k]], r); r_net[[k]] <- c(r_net[[k]], rn)
      if (j > 1) giro[[k]] <- c(giro[[k]], T_j)             # TRAMPA: la rotación promedio excluye la compra inicial
      w_prev[[k]] <- w
    }
    f_bt <- c(f_bt, fe[idx])
  }
  f0 <- fe[reb[1]]       # TRAMPA: los años del backtest se cuentan desde el primer rebalanceo
  # No hay backtest de máximo Sharpe: con 252 días, mu se estima con tanto error que los pesos
  # saltan entre −1.000% y +850% (vea la Clase 3).
  bt <- t(sapply(carteras_bt, function(k) c(metricas(r_bt[[k]], f_bt, rf, f0),
                                            rotacion = mean(giro[[k]]),
                                            sharpe_neto = metricas(r_net[[k]], f_bt, rf, f0)[["sharpe"]])))
  met <- data.frame(cartera = c(paste0("IS_", rownames(is)), paste0("BT_", rownames(bt))),
                    rbind(cbind(is, rotacion = NA, sharpe_neto = NA), bt), row.names = NULL)
  cp <- c(paste0("IS_", c("MINVAR", "MAXSHARPE", "INVVOL", "ERC")), paste0("BT1_", c("MINVAR", "MAXSHARPE", "INVVOL", "ERC")))
  pes <- data.frame(cartera = rep(cp, each = n), activo = rep(act, length(cp)),
                    peso = c(w_is$MINVAR, w_is$MAXSHARPE, w_is$INVVOL, w_is$ERC,
                             w1$MINVAR, w1$MAXSHARPE, w1$INVVOL, w1$ERC), row.names = NULL)
  cat("Primer rebalanceo:", format(f0), "| n.º de rebalanceos:", length(reb), "\n")
  list(metricas = met, pesos = pes)
}

# ---- Salida en el formato del contrato (fracciones, punto decimal) ------------
r <- desafio3(entrada, rf)
write.csv(r$pesos,    file.path(carpeta, "pesos.csv"),    row.names = FALSE)
write.csv(r$metricas, file.path(carpeta, "metricas.csv"), row.names = FALSE)
print(r$metricas)