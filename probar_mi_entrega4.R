# =============================================================================
# Desafío 4 - Prueba de su entrega (NO le dice si sus cifras son correctas)
# Póngalo en la carpeta con su desafio4.R (o .py), los 7 archivos de datos y su cartera.csv, y haga Source.
# Revisa el contrato y propiedades que cualquier solución correcta cumple.
# =============================================================================
if (requireNamespace("rstudioapi", quietly = TRUE) && rstudioapi::isAvailable())
  setwd(dirname(rstudioapi::getSourceEditorContext()$path))
M <- c("VAR_HIST", "ES_HIST", "VAR_NORMAL", "ES_NORMAL", "VAR_RM_SIGUIENTE", "VAR_GARCH_SIGUIENTE", "VAR_FHS_SIGUIENTE",
       "N_DIAS", "RET_ACUM", "BT_N_OBS", "BT_INCUMPL_HIST", "BT_INCUMPL_NORMAL", "BT_INCUMPL_RM", "BT_INCUMPL_GARCH",
       "KUPIEC_LR", "KUPIEC_PVALOR", "CHRIST_LR_IND", "CHRIST_PVALOR_IND", "CHRIST_LR_CC", "CHRIST_PVALOR_CC",
       "KUPIEC_PVALOR_RM", "CHRIST_PVALOR_CC_RM", "KUPIEC_PVALOR_GARCH", "CHRIST_PVALOR_CC_GARCH",
       "BT_N_OBS_FHS", "BT_INCUMPL_FHS", "KUPIEC_PVALOR_FHS", "ES_BT_Z2",
       "RET_ACUM_MERCADO", "BETA_MERCADO", "VAR_HIST_ACTIVO")
Q <- c("FILAS_SCL", "FILAS_NYC", "DIAS_FONDO", "PARES_DUPLICADOS", "EMISORES_CON_CAMBIO_TICKER",
       "DIAS_FONDO_SIN_TC", "FILAS_POST_SALIDA", "SPLITS_CARTERA", "DIVIDENDOS_CARTERA")
DATOS <- c("maestro_emisores.csv", "precios_SCL.csv", "precios_NYC.csv", "tipo_cambio.csv", "eventos_corporativos.csv",
           "salidas_de_bolsa.csv", "parametros_riesgo.csv", "cartera.csv")
prog <- intersect(c("desafio4.R", "desafio4.py"), list.files())[1]
if (is.na(prog)) stop("No encuentro desafio4.R ni desafio4.py en esta carpeta.")
for (f in DATOS) if (!file.exists(f)) stop("Falta ", f, " en esta carpeta.")
cart <- read.csv("cartera.csv", colClasses = c("character", "numeric"))
ok <- function(cond, txt) cat(if (isTRUE(cond)) "  OK   " else "  FALLA", txt, "\n")
ok(nrow(cart) == 20 && abs(sum(cart$peso) - 1) < 1e-6, "cartera.csv tiene 20 emisores y los pesos suman 1")
if (file.exists("carteras_D4.csv")) { cc <- read.csv("carteras_D4.csv", colClasses = c("character", "character", "numeric"))
  r <- unique(cc$rut[cc$id %in% cart$id]); r <- r[sapply(r, function(x) setequal(cc$id[cc$rut == x], cart$id))]
  ok(length(r) == 1, paste("cartera.csv es la cartera de un RUT de carteras_D4.csv", if (length(r) == 1) paste0("(", r, ")") else "")) }
correr <- function(dir) {
  old <- setwd(dir); on.exit(setwd(old)); unlink(c("riesgo.csv", "backtest.csv", "calidad_datos.csv"))
  cmd <- if (prog == "desafio4.py") { p <- Sys.which(c("python3", "python")); p[nzchar(p)][1] } else file.path(R.home("bin"), "Rscript")
  t0 <- Sys.time(); system2(cmd, prog); seg <- as.numeric(difftime(Sys.time(), t0, units = "secs"))
  lee <- function(a) if (file.exists(a)) read.csv(a) else NULL
  list(r = lee("riesgo.csv"), b = lee("backtest.csv"), q = lee("calidad_datos.csv"), seg = seg)
}
cat("\nEjecutando", prog, "...\n"); x <- correr(".")
cat(sprintf("Tardó %.0f segundos (límite del contrato: 1800 = 30 min; la corrección corta a los 2700).\n", x$seg))
ok(!is.null(x$r), "escribe riesgo.csv"); ok(!is.null(x$q), "escribe calidad_datos.csv"); ok(!is.null(x$b), "escribe backtest.csv")
if (is.null(x$r)) stop("Sin riesgo.csv no se puede seguir.")
ok(identical(names(x$r), c("metrica", "valor")) && identical(as.character(x$r$metrica), M), "riesgo.csv: columnas metrica,valor y las 31 métricas en orden")
if (!is.null(x$q)) ok(identical(as.character(x$q[[1]]), Q), "calidad_datos.csv: los 9 indicadores en orden")
v <- setNames(suppressWarnings(as.numeric(x$r$valor)), x$r$metrica)
ok(!anyNA(v), "todos los valores son numéricos (punto decimal)")
ok(v["ES_HIST"] >= v["VAR_HIST"] && v["ES_NORMAL"] >= v["VAR_NORMAL"], "ES >= VaR")
ok(v["VAR_HIST"] > 0 && v["VAR_HIST"] < 0.5, "VaR como pérdida positiva en fracción")
ok(v["BETA_MERCADO"] > 0 && v["BETA_MERCADO"] < 3 && v["VAR_HIST_ACTIVO"] > 0, "beta razonable y VaR activo positivo")
ok(all(v[grep("PVALOR", names(v))] >= 0 & v[grep("PVALOR", names(v))] <= 1), "p-valores entre 0 y 1")
ok(abs(v["CHRIST_LR_CC"] - v["KUPIEC_LR"] - v["CHRIST_LR_IND"]) < 1e-8, "LR_cc = LR de Kupiec + LR de independencia")
p <- read.csv("parametros_riesgo.csv", colClasses = c(inicio = "character"))
ok(v["BT_N_OBS"] == v["N_DIAS"] - p$ventana && v["BT_N_OBS_FHS"] == v["N_DIAS"] - 2 * p$ventana, "BT_N_OBS = N_DIAS - ventana y BT_N_OBS_FHS = N_DIAS - 2 x ventana")
if (!is.null(x$b)) {
  ok(nrow(x$b) == v["BT_N_OBS"], "backtest.csv tiene BT_N_OBS filas")
  ok(all(c("incumpl_hist", "incumpl_rm", "incumpl_garch", "incumpl_fhs") %in% names(x$b)) &&
     sum(x$b$incumpl_garch) == v["BT_INCUMPL_GARCH"] && sum(x$b$incumpl_fhs, na.rm = TRUE) == v["BT_INCUMPL_FHS"],
     "los incumplimientos de backtest.csv suman lo que reporta riesgo.csv")
}
if (!is.null(x$q)) { q <- setNames(x$q[[2]], x$q[[1]])
  ok(q["FILAS_SCL"] == length(readLines("precios_SCL.csv")) - 1 && q["FILAS_NYC"] == length(readLines("precios_NYC.csv")) - 1,
     "FILAS_SCL y FILAS_NYC = filas de datos de cada archivo")
  ok(q["DIAS_FONDO"] == v["N_DIAS"] + sum(unique(c(format(as.Date(read.table("precios_SCL.csv", sep = ";", header = TRUE, colClasses = "character")$fecha, "%d/%m/%Y")),
     read.csv("precios_NYC.csv", colClasses = "character")$date)) < p$inicio), "DIAS_FONDO = N_DIAS + días antes de 'inicio'") }
cat("\nAhora con alfa = 0,95 (en una copia)...\n")
tmp <- tempfile(); dir.create(tmp); for (f in c(prog, DATOS)) file.copy(f, tmp)
p$alfa <- 0.95; write.csv(p, file.path(tmp, "parametros_riesgo.csv"), row.names = FALSE)
y <- correr(tmp)$r
if (!is.null(y)) { w <- setNames(as.numeric(y$valor), y$metrica)
  ok(w["VAR_HIST"] < v["VAR_HIST"], "con alfa 0,95 el VaR histórico baja")
  ok(w["RET_ACUM"] == v["RET_ACUM"] && w["BETA_MERCADO"] == v["BETA_MERCADO"], "RET_ACUM y BETA_MERCADO no dependen de alfa") } else ok(FALSE, "corre con alfa 0,95")
cat("\nRecuerde: pasar estas pruebas NO significa que sus cifras estén bien.\n")