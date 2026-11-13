"""Prueba independiente con un mercado pequeño y cifras calculables a mano.

Desde la raíz: python tests/verificar_desafio4.py
"""
from pathlib import Path
import math
import subprocess
import sys
import tempfile

import numpy as np
import pandas as pd

SCRIPT = Path(__file__).resolve().parents[1] / "desafio4.py"

FUENTES = {
    "maestro_emisores.csv": """id,ticker,bolsa,moneda,desde,hasta
A,NEW,SCL,CLP,2024-01-04,9999-12-31
D,OLD,SCL,CLP,2024-01-08,9999-12-31
B,B,NYC,USD,2024-01-01,9999-12-31
A,OLD,SCL,CLP,2024-01-01,2024-01-03
C,C,NYC,USD,2024-01-01,2024-01-10
C,CS,SCL,CLP,2024-01-11,9999-12-31
""",
    "precios_SCL.csv": """fecha;ticker;cierre;volumen;version
04/01/2024;NEW;600,00;1;2
08/01/2024;NEW;880,00;1;1
02/01/2024;OLD;1000,00;1;1
09/01/2024;OLD;2200,00;1;1
04/01/2024;NEW;50,00;1;1
10/01/2024;OLD;2000,00;1;1
08/01/2024;OLD;2000,00;1;1
11/01/2024;CS;2205,00;1;1
""",
    "precios_NYC.csv": """date,ticker,close,volume,version
2024-01-11,B,12.1,1,1
2024-01-03,B,11,1,1
2024-01-02,C,20,1,1
2024-01-05,B,10,1,1
2024-01-02,B,10,1,1
2024-01-08,B,11,1,1
2024-01-04,C,21,1,1
2024-01-09,B,10.78,1,1
2024-01-10,B,10,1,1
""",
    "tipo_cambio.csv": """fecha;clp_por_usd
08-01-2024;110,00
02-01-2024;100,00
10-01-2024;100,00
""",
    "salidas_de_bolsa.csv": "id;ultimo_dia;evento;retorno_final\nA;2024-01-04;OPA;-0,20\n",
    "eventos_corporativos.csv": "ticker,fecha,tipo,valor\nNEW,2024-01-04,SPLIT,2\nNEW,2024-01-04,DIVIDENDO,100\nOLD,2024-01-09,DIVIDENDO,10\n",
    "cartera.csv": "id,peso\nA,0.5\nB,0.5\n",
    "parametros_riesgo.csv": "alfa,ventana,inicio,lambda,garch_alfa,garch_beta\n0.9,2,2024-01-03,0.8,0.1,0.7\n",
}


def ejecutar(carpeta, invertir=False):
    for nombre, datos in FUENTES.items():
        lineas = datos.splitlines()
        if invertir:
            lineas[1:] = lineas[:0:-1]
        (carpeta / nombre).write_text("\n".join(lineas) + "\n")
    subprocess.run([sys.executable, str(SCRIPT)], cwd=carpeta, check=True)
    return [pd.read_csv(carpeta / nombre) for nombre in ("riesgo.csv", "calidad_datos.csv", "backtest.csv")]


def cuantil(serie, alfa):
    valores = sorted(serie)
    k = (len(valores)-1)*alfa
    i = math.floor(k)
    return valores[i] + (k-i)*(valores[math.ceil(k)]-valores[i])


def main():
    with tempfile.TemporaryDirectory() as t:
        archivos = ejecutar(Path(t))
        for original, invertido in zip(archivos, ejecutar(Path(t), invertir=True)):
            pd.testing.assert_frame_equal(original, invertido)

    datos, calidad, bt = archivos
    q = calidad.set_index("indicador").valor
    assert list(q) == [8, 9, 8, 1, 2, 5, 1, 1, 1]
    m = datos.set_index("metrica").valor
    assert len(m) == 31 and len(bt) == 5
    assert np.isfinite(m).all()
    # Una OPA se contabiliza el 5 aunque Santiago no tenga precios ese día.
    # El cambio OLD→NEW conserva el precio previo del mismo emisor.
    r = np.array([0.05, 0.15, (-0.2 + (10/11-1))/2, 0.05, -0.01, (10/10.78-1)/2, 0.105])
    mercado = np.array([
        0.1, (0.3+0.05)/2, (-0.2+(10/11-1))/2, 0.1,
        (-0.02+(2210/110)/(2000/110)-1)/2,
        ((10/10.78-1)+(2000/100)/(2200/110)-1)/2, (0.21+0.05)/2,
    ])
    np.testing.assert_allclose(-bt.perdida, r[2:])
    np.testing.assert_allclose(m.RET_ACUM, np.prod(1+r)-1)
    np.testing.assert_allclose(m.RET_ACUM_MERCADO, np.prod(1+mercado)-1)
    np.testing.assert_allclose(m.BETA_MERCADO, np.cov(r, mercado)[0, 1]/mercado.var(ddof=1))
    np.testing.assert_allclose(m.VAR_HIST_ACTIVO, cuantil(mercado-r, 0.9))
    np.testing.assert_allclose(m.VAR_HIST, cuantil(-r, 0.9))
    np.testing.assert_allclose(bt.var_hist, [cuantil(-r[i-2:i], 0.9) for i in range(2, len(r))])
    assert bt.var_fhs.iloc[:2].isna().all() and bt.incumpl_fhs.iloc[:2].isna().all()
    sigma0 = (0.15-0.05)**2/2
    z = 1.2815515655446004
    rm3 = .8*sigma0 + .2*r[2]**2
    g3 = .2*sigma0 + .1*r[2]**2 + .7*sigma0
    np.testing.assert_allclose(bt.var_rm.iloc[:2], [z*math.sqrt(sigma0), z*math.sqrt(rm3)])
    np.testing.assert_allclose(bt.var_garch.iloc[:2], [z*math.sqrt(sigma0), z*math.sqrt(g3)])
    fhs = math.sqrt(.8*rm3 + .2*r[3]**2)*cuantil([-r[2]/math.sqrt(sigma0), -r[3]/math.sqrt(rm3)], .9)
    np.testing.assert_allclose(bt.var_fhs.iloc[2], fhs)
    print("OK: mercado alternativo, filas invertidas, retornos y pronósticos calculados a mano")


if __name__ == "__main__":
    main()
