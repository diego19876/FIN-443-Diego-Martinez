"""Clase 6, Bloque 1: ejecutar junto a fondo_clase6.csv con NumPy y pandas.

Fuente: Clase 6, láminas 9, 11 y 17 (páginas PDF 10, 13 y 20).
La consigna fija lambda = 3,000: se usa 3000, sin optimizarlo en la prueba.
Desviación muestral (ddof=1); intercepto sin penalización.
Se usan x01–x10 como vienen en el ejercicio, sin añadir rezagos ajenos a él.
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def resolver(archivo="fondo_clase6.csv"):
    datos = pd.read_csv(archivo)
    senales = [f"x{i:02d}" for i in range(1, 11)]
    requeridas = ["fecha", "retorno", *senales, "senal_revisada"]
    if not set(requeridas).issubset(datos.columns) or len(datos) != 1500:
        raise ValueError("Se requieren las columnas de clase y exactamente 1500 días.")
    fechas = pd.to_datetime(datos["fecha"], format="%Y-%m-%d", errors="raise")
    if not fechas.is_unique or not fechas.is_monotonic_increasing:
        raise ValueError("Las fechas deben ser únicas y estar en orden ascendente.")
    if not np.isfinite(datos[requeridas[1:]].to_numpy(dtype=float)).all():
        raise ValueError("Hay datos numéricos faltantes o no finitos; no se eliminan días.")
    X = datos[senales].to_numpy(dtype=float)
    y = datos["retorno"].to_numpy(dtype=float)
    X_est, X_pru = X[:1000], X[1000:1500]
    y_est, y_pru = y[:1000], y[1000:1500]
    promedio = y_est.mean()
    sst_est = np.sum((y_est - promedio) ** 2)
    sst_pru = np.sum((y_pru - promedio) ** 2)
    if min(sst_est, sst_pru) <= 0:
        raise ValueError("El R² no está definido: el error del promedio es cero.")

    # MCO con intercepto: los coeficientes solo ven los días de estimación.
    A_est = np.column_stack((np.ones(len(y_est)), X_est))
    A_pru = np.column_stack((np.ones(len(y_pru)), X_pru))
    beta = np.linalg.lstsq(A_est, y_est, rcond=None)[0]
    r2_mco_dentro = 1 - np.sum((y_est - A_est @ beta) ** 2) / sst_est
    r2_mco_fuera = 1 - np.sum((y_pru - A_pru @ beta) ** 2) / sst_pru

    # Ridge: media y desviación exclusivamente de los primeros 1000 días.
    media = X_est.mean(axis=0)
    desviacion = X_est.std(axis=0, ddof=1)
    if np.any(desviacion == 0):
        raise ValueError("Una señal es constante: no se puede estandarizar.")
    Z_est = (X_est - media) / desviacion
    Z_pru = (X_pru - media) / desviacion
    lam = 3000.0
    b = np.linalg.solve(Z_est.T @ Z_est + lam * np.eye(len(senales)),
                        Z_est.T @ (y_est - promedio))
    pred_ridge = promedio + Z_pru @ b
    r2_ridge_fuera = 1 - np.sum((y_pru - pred_ridge) ** 2) / sst_pru

    # Experimento solicitado: la señal revisada se agrega, no sustituye las diez.
    revisada = datos["senal_revisada"].to_numpy(dtype=float)
    B_est = np.column_stack((A_est, revisada[:1000]))
    B_pru = np.column_stack((A_pru, revisada[1000:1500]))
    beta_revisada = np.linalg.lstsq(B_est, y_est, rcond=None)[0]
    r2_revisada_fuera = 1 - np.sum((y_pru - B_pru @ beta_revisada) ** 2) / sst_pru
    return {
        "MCO_R2_DENTRO": r2_mco_dentro,
        "MCO_R2_FUERA": r2_mco_fuera,
        "RIDGE_R2_FUERA": r2_ridge_fuera,
        "MCO_REVISADA_R2_FUERA": r2_revisada_fuera,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archivo", nargs="?", default="fondo_clase6.csv")
    args = parser.parse_args()
    resultados = resolver(args.archivo)
    for nombre, valor in resultados.items():
        print(f"{nombre}: {100 * valor:.3f}%")
    pd.DataFrame(resultados.items(), columns=["metrica", "valor_fraccion"]).to_csv(
        "resultados_clase6_bloque1.csv", index=False, float_format="%.17g")


if __name__ == "__main__":
    main()
