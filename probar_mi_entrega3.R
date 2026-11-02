# =============================================================================
# Programación en Finanzas (FIN443) - UAI 2026 - Desafío 3
# PRUEBA PÚBLICA: ejecútela antes de entregar (Source en RStudio).
# -----------------------------------------------------------------------------
# Corre su desafio3.R (o .py) en un R nuevo, igual que el profesor, y revisa el
# contrato y dos INVARIANTES (cosas que siempre deben cumplirse). No revisa si
# sus números están bien: eso lo decide usted (y luego los datos ocultos).
# Deje en la misma carpeta: este archivo, su desafio3.R/.py y precios_desafio3.csv.
# =============================================================================
if (requireNamespace("rstudioapi", quietly = TRUE) && rstudioapi::isAvailable()) {
  setwd(dirname(rstudioapi::getSourceEditorContext()$path))
}
ok <- function(cond, msg) { cond <- isTRUE(cond); cat(if (cond) "  [OK]   " else "  [FALLA]", msg, "\n"); invisible(cond) }
script <- c("desafio3.R", "desafio3.py")[file.exists(c("desafio3.R", "desafio3.py"))][1]
if (is.na(script)) stop("No encuentro desafio3.R ni desafio3.py en esta carpeta.")
if (!file.exists("precios_desafio3.csv")) stop("Copie precios_desafio3.csv en esta carpeta.")
out <- file.path(tempdir(), "prueba_desafio3"); unlink(out, recursive = TRUE)
cmd <- if (grepl("\\.R$", script)) file.path(R.home("bin"), "Rscript") else (if (nzchar(Sys.which("python3"))) "python3" else "python")
cat("Ejecutando:", script, "precios_desafio3.csv <carpeta>\n")
t0 <- Sys.time()
st <- system2(cmd, c(shQuote(script), "precios_desafio3.csv", shQuote(out)), stdout = TRUE, stderr = TRUE, timeout = 120)
cat("Tiempo:", round(as.numeric(Sys.time() - t0, units = "secs"), 1), "s\n\n")
if (!is.null(attr(st, "status")) && attr(st, "status") != 0) cat(st, sep = "\n")
leer <- function(f) tryCatch({ x <- read.csv(file.path(out, f), stringsAsFactors = FALSE); names(x) <- tolower(trimws(names(x))); x }, error = function(e) NULL)
p <- leer("pesos.csv"); m <- leer("metricas.csv")
cat("Contrato:\n")
ok(!is.null(p), "se creó pesos.csv")
ok(!is.null(m), "se creó metricas.csv")
if (is.null(p) || is.null(m)) stop("Revise los mensajes de error de arriba.")
act <- names(read.csv2("precios_desafio3.csv", nrows = 1, check.names = FALSE))[-1]
ok(all(c("cartera", "activo", "peso") %in% names(p)), "pesos.csv tiene las columnas cartera, activo, peso")
ok(all(c("cartera", "cagr", "vol", "sharpe", "mdd", "rotacion", "sharpe_neto") %in% names(m)), "metricas.csv tiene las columnas cartera, cagr, vol, sharpe, mdd, rotacion, sharpe_neto")
cp <- c("IS_MINVAR", "IS_MAXSHARPE", "IS_INVVOL", "IS_ERC", "BT1_MINVAR", "BT1_MAXSHARPE", "BT1_INVVOL", "BT1_ERC")
ok(all(sapply(cp, function(k) setequal(trimws(p$activo[p$cartera == k]), act))), paste("pesos.csv tiene un peso por activo para", paste(cp, collapse = ", ")))
cm <- c("IS_MINVAR", "IS_MAXSHARPE", "IS_EW", "IS_INVVOL", "IS_ERC", "BT_MINVAR", "BT_EW", "BT_INVVOL", "BT_ERC")
ok(all(cm %in% trimws(m$cartera)), paste("metricas.csv tiene", paste(cm, collapse = ", ")))
ok(is.numeric(p$peso) && all(sapply(m[c("cagr", "vol", "sharpe", "mdd")], is.numeric)), "todo son números (punto decimal, sin %)")
cat("\nInvariantes:\n")
ok(all(abs(tapply(p$peso, p$cartera, sum) - 1) < 1e-6), "los pesos de cada cartera suman 1")
mv <- m$vol[m$cartera == "IS_MINVAR"]
ok(length(mv) == 1 && all(mv <= m$vol[m$cartera %in% c("IS_MAXSHARPE", "IS_EW", "IS_INVVOL", "IS_ERC")] + 1e-9), "dentro de muestra, la de mínima varianza no tiene más volatilidad que ninguna otra cartera")
ok(all(p$peso[p$cartera %in% c("IS_INVVOL", "BT1_INVVOL", "IS_ERC", "BT1_ERC")] > 0), "los pesos de inversa de la volatilidad y de paridad de riesgo son todos positivos")
ok(all(m$mdd >= 0 & m$mdd <= 1, na.rm = TRUE) && !anyNA(m$mdd), "la caída máxima (mdd) está entre 0 y 1 en todas las carteras (es una fracción positiva)")
bt <- grepl("^BT_", trimws(m$cartera))
ok(!anyNA(m$rotacion[bt]) && !anyNA(m$sharpe_neto[bt]), "las carteras BT_ tienen rotacion y sharpe_neto")
ok(isTRUE(abs(m$rotacion[trimws(m$cartera) == "BT_EW"]) < 1e-9), "la rotación de 1/N es 0 (sus pesos nunca cambian)")
ok(all(m$sharpe_neto[bt] <= m$sharpe[bt] + 1e-9), "el Sharpe neto no es mayor que el Sharpe sin costos")
cat("\nSus métricas:\n"); print(m)
cat("\nSus pesos (en %):\n"); w <- reshape(p, idvar = "activo", timevar = "cartera", direction = "wide"); w[-1] <- round(100 * w[-1], 2); print(w, row.names = FALSE)
