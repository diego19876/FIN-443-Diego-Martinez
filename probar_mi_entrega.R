# Prueba pública de formato proporcionada por el profesor.
if (requireNamespace("rstudioapi", quietly = TRUE) && rstudioapi::isAvailable()) {
  setwd(dirname(rstudioapi::getSourceEditorContext()$path))
}
ok <- function(cond, msg) { cat(if (cond) "  [OK]   " else "  [FALLA]", msg, "\n"); invisible(cond) }

script <- c("desafio2.R", "desafio2.py")[file.exists(c("desafio2.R", "desafio2.py"))][1]
if (is.na(script)) stop("No encuentro desafio2.R ni desafio2.py en esta carpeta.")
datos <- "precios_desafio2.csv"
if (!file.exists(datos)) stop("Copie precios_desafio2.csv en esta carpeta.")
out <- tempfile(fileext = ".csv")
cmd <- if (grepl("\\.R$", script)) file.path(R.home("bin"), "Rscript") else (if (nzchar(Sys.which("python3"))) "python3" else "python")
cat("Ejecutando:", cmd, script, datos, "salida.csv\n")
t0 <- Sys.time()
st <- system2(cmd, c(shQuote(script), shQuote(datos), shQuote(out)), stdout = TRUE, stderr = TRUE, timeout = 120)
cat("Tiempo:", round(as.numeric(Sys.time() - t0, units = "secs"), 1), "s\n\n")
if (!is.null(attr(st, "status")) && attr(st, "status") != 0) cat(st, sep = "\n")

cat("Revisión del contrato:\n")
if (!ok(file.exists(out), "el script creó el archivo de salida")) stop("Revise los mensajes de error de arriba.")
s <- tryCatch(read.csv(out, stringsAsFactors = FALSE), error = function(e) NULL)
ok(!is.null(s), "la salida se lee como CSV separado por comas")
names(s) <- tolower(trimws(names(s)))
ok(all(c("activo", "cagr", "vol", "sharpe") %in% names(s)), "tiene las columnas activo, cagr, vol, sharpe")
p <- read.csv(datos, nrows = 1, check.names = FALSE); act <- names(p)[-1]
ok(all(c(act, "CARTERA_EW") %in% trimws(s$activo)), paste("tiene una fila por activo y CARTERA_EW:", paste(c(act, "CARTERA_EW"), collapse = ", ")))
ok(all(sapply(s[c("cagr", "vol", "sharpe")], is.numeric)), "las métricas son números (punto decimal, sin %)")
ok(all(s$vol > 0 & s$vol < 3, na.rm = TRUE), "cagr y vol están en fracción (0.0462), no en porcentaje (4.62)")
ok(!anyNA(s[c("cagr", "vol", "sharpe")]), "no hay valores faltantes")
cat("\nSu salida:\n"); print(s)
