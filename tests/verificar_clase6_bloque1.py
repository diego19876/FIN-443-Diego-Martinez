"""Contraste integral con R y CSV sintéticos; no altera los datos originales."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile

import numpy as np
import pandas as pd

PROGRAMA = Path(__file__).resolve().parents[1] / "clase6_bloque1.py"
REFERENCIA_R = r'''
d <- read.csv(commandArgs(TRUE)[1])
x <- as.matrix(d[sprintf("x%02d", 1:10)])
y <- d$retorno; a <- 1:1000; t <- 1001:1500
m <- mean(y[a]); den <- sum((y[t]-m)^2)
f <- lm(retorno ~ ., data=d[a,c("retorno",sprintf("x%02d",1:10))])
p <- predict(f, newdata=d)
u <- 1-sum((y[a]-p[a])^2)/sum((y[a]-m)^2)
v <- 1-sum((y[t]-p[t])^2)/den
z <- scale(x[a,], center=TRUE, scale=TRUE)
zt <- sweep(sweep(x[t,],2,attr(z,"scaled:center")),2,attr(z,"scaled:scale"),"/")
b <- solve(crossprod(z)+3000*diag(10),crossprod(z,y[a]-m))
w <- 1-sum((y[t]-as.vector(m+zt%*%b))^2)/den
g <- lm(retorno ~ .,data=d[a,c("retorno",sprintf("x%02d",1:10),"senal_revisada")])
q <- 1-sum((y[t]-predict(g,newdata=d[t,]))^2)/den
write.table(data.frame(valor=c(u,v,w,q)),commandArgs(TRUE)[2],sep=",",row.names=FALSE)
'''


def comprobar(datos, carpeta):
    carpeta.mkdir()
    entrada = carpeta / "fondo_clase6.csv"
    datos.to_csv(entrada, index=False, float_format="%.17g")
    subprocess.run([sys.executable, str(PROGRAMA)], cwd=carpeta,
                   check=True, capture_output=True, text=True)
    r = carpeta / "referencia.R"
    r.write_text(REFERENCIA_R)
    subprocess.run(["Rscript", str(r), str(entrada), str(carpeta / "R.csv")],
                   check=True, capture_output=True, text=True)
    obtenido = pd.read_csv(carpeta / "resultados_clase6_bloque1.csv").valor_fraccion.to_numpy()
    esperado = pd.read_csv(carpeta / "R.csv").valor.to_numpy()
    np.testing.assert_allclose(obtenido, esperado, atol=1e-11, rtol=1e-11)
    return obtenido, float(np.max(np.abs(obtenido-esperado)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("datos")
    parser.add_argument("--evidencia", help="Carpeta nueva donde conservar CSV y contraste R")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="clase6_integral_") as temporal:
        raiz = Path(temporal)
        original = pd.read_csv(args.datos)
        publico, error = comprobar(original, raiz / "publico")
        print(f"OK público: cuatro métricas contra R; diferencia máxima={error:.3g}")
        for semilla in (17, 98):
            rng = np.random.default_rng(semilla)
            x = rng.normal(size=(1500,10)) * np.arange(1,11) + np.arange(10)
            y = 0.002 + x[:,0]*0.005 + rng.normal(0,0.01,1500)
            sintetico = pd.DataFrame(x, columns=[f"x{i:02d}" for i in range(1,11)])
            sintetico.insert(0,"retorno",y)
            sintetico.insert(0,"fecha",pd.bdate_range("2010-01-01",periods=1500).strftime("%Y-%m-%d"))
            sintetico["senal_revisada"] = 50*y + rng.normal(0,0.1,1500)
            _, error = comprobar(sintetico, raiz / f"sintetico_{semilla}")
            print(f"OK sintético {semilla}: ejecutable completo contra R; diferencia máxima={error:.3g}")
        alterado = original.copy()
        alterado["senal_revisada"] *= 100
        otros, _ = comprobar(alterado, raiz / "revisada_otra_escala")
        np.testing.assert_allclose(otros, publico, atol=1e-11, rtol=1e-11)
        print("OK cambiar escala de señal revisada: MCO invariante y modelos limpios sin cambios")
        if args.evidencia:
            shutil.copytree(raiz, args.evidencia)
    print("SHA256 programa:", hashlib.sha256(PROGRAMA.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
