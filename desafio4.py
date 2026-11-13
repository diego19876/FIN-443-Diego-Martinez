"""FIN443 · Desafío 4. Ejecutar en la carpeta con los datos y cartera.csv."""
from math import erfc, exp, log, pi, sqrt
from statistics import NormalDist

import numpy as np
import pandas as pd


def dias(columna, formato="%Y-%m-%d"):
    return pd.to_datetime(columna, format=formato).to_numpy(dtype="datetime64[D]").astype("int32")


def mapa_vigente(ticker, fecha, maestro):
    """Resolver intervalos inclusivos, incluso si se reutiliza un ticker."""
    maestro = maestro.sort_values(["ticker", "desde"])
    claves = maestro["ticker"].unique()
    indice = pd.Index(claves).get_indexer(ticker)
    id_emisor = np.full(len(fecha), -1, dtype="int32")
    for _, tramo in maestro.groupby(maestro.groupby("ticker").cumcount()):
        tabla = tramo.set_index("ticker").reindex(claves)
        idx = np.maximum(indice, 0)
        valido = (indice >= 0) & (fecha >= tabla.desde.to_numpy()[idx]) & (fecha <= tabla.hasta.to_numpy()[idx])
        if np.any(id_emisor[valido] >= 0):
            raise ValueError("Hay vigencias de ticker superpuestas")
        id_emisor[valido] = tabla.codigo.fillna(-1).to_numpy(dtype="int32")[idx[valido]]
    if np.any(id_emisor < 0):
        raise ValueError("Hay precios o eventos sin ticker vigente en el maestro")
    return id_emisor


def precios(archivo, bolsa, maestro, ultimo, pesos):
    scl = bolsa == "SCL"
    fecha, precio = ("fecha", "cierre") if scl else ("date", "close")
    p = pd.read_csv(archivo, sep=";" if scl else ",", decimal="," if scl else ".",
                    usecols=[fecha, "ticker", precio, "version"],
                    dtype={fecha: "category", "ticker": "category", "version": "int32"})
    n = len(p)
    calendario = dias(p[fecha].cat.categories, "%d/%m/%Y" if scl else "%Y-%m-%d")
    p[fecha] = calendario[p[fecha].cat.codes]
    # Ordenar por versión antes de elegir un registro por fecha y ticker.
    p = p.sort_values("version", kind="stable").drop_duplicates([fecha, "ticker"], keep="last")
    duplicados = n - len(p)
    id_emisor = mapa_vigente(p.ticker, p[fecha].to_numpy(), maestro[maestro.bolsa == bolsa])
    p = pd.DataFrame({"dia": p[fecha].to_numpy(), "id": id_emisor,
                      "precio": p[precio].to_numpy(), "scl": scl})
    post = p.dia.to_numpy() > ultimo[id_emisor]
    tardias = int(post.sum())
    # Guardar únicamente las filas necesarias para medir el efecto de ignorar las salidas.
    cartera_bruta = p.loc[pesos[id_emisor] != 0].copy()
    return p.loc[~post], cartera_bruta, calendario, (n, duplicados, tardias)


def retornos(p, calendario, tc, eventos, usar_splits=True, usar_div=True, usar_tc=True):
    p = p.sort_values(["id", "dia"], ignore_index=True)
    fecha = np.searchsorted(calendario, p.dia)
    ids = p.id.to_numpy()
    cierre = p.precio.to_numpy()
    x = np.where(p.scl, tc[fecha], 1) if usar_tc else np.ones(len(p))
    # Los eventos se aplican en la fecha de la fila actual y por emisor vigente.
    clave = ids.astype("int64") * len(calendario) + fecha
    fila = pd.Index(clave)
    actual = cierre / x
    numerador = actual.copy()
    if usar_splits:
        posiciones = fila.get_indexer(eventos["SPLIT"].index)
        hay = posiciones >= 0
        numerador[posiciones[hay]] *= eventos["SPLIT"].to_numpy()[hay]
    if usar_div:
        posiciones = fila.get_indexer(eventos["DIVIDENDO"].index)
        hay = posiciones >= 0
        numerador[posiciones[hay]] += eventos["DIVIDENDO"].to_numpy()[hay] / x[posiciones[hay]]
    seguidas = ids[1:] == ids[:-1]
    r = np.full(len(p), np.nan)
    r[1:] = np.where(seguidas, numerador[1:] / actual[:-1] - 1, np.nan)
    return fecha, ids, r


def construir_series(cart, auditar=False):
    m = pd.read_csv("maestro_emisores.csv", dtype=str)
    emisores = pd.Index(m.id.unique())
    m["codigo"] = emisores.get_indexer(m.id)
    m["desde"], m["hasta"] = dias(m.desde), dias(m.hasta.replace("9999-12-31", "2262-04-11"))
    posiciones = emisores.get_indexer(cart.id)
    if np.any(posiciones < 0) or not cart.id.is_unique or not np.isclose(cart.peso.sum(), 1):
        raise ValueError("Cartera debe tener emisores conocidos y únicos y pesos que sumen 1")
    pesos = np.zeros(len(emisores))
    pesos[posiciones] = cart.peso
    s = pd.read_csv("salidas_de_bolsa.csv", sep=";", decimal=",", dtype={"id": str})
    s = s.loc[s.id.isin(emisores)]
    sal_ids, sal_dias = emisores.get_indexer(s.id), dias(s.ultimo_dia)
    ultimo = np.full(len(emisores), np.iinfo("int32").max, dtype="int32")
    ultimo[sal_ids] = sal_dias
    scl, scl_cart, dias_scl, c_scl = precios("precios_SCL.csv", "SCL", m, ultimo, pesos)
    nyc, nyc_cart, dias_nyc, c_nyc = precios("precios_NYC.csv", "NYC", m, ultimo, pesos)
    calendario = np.union1d(dias_scl, dias_nyc)
    fx = pd.read_csv("tipo_cambio.csv", sep=";", decimal=",")
    tc_original = pd.Series(fx.clp_por_usd.to_numpy(), index=dias(fx.fecha, "%d-%m-%Y")).sort_index()
    tc = tc_original.reindex(calendario, method="ffill").to_numpy()
    if np.any(~np.isfinite(tc[np.searchsorted(calendario, dias_scl)])):
        raise ValueError("Falta un tipo de cambio anterior o igual al primer precio de Santiago")
    e = pd.read_csv("eventos_corporativos.csv", dtype={"ticker": str})
    e["dia"] = dias(e.fecha)
    e["id"] = mapa_vigente(e.ticker, e.dia.to_numpy(), m)
    en_calendario = e.dia.isin(calendario)
    e["clave"] = e.id.astype("int64") * len(calendario) + np.searchsorted(calendario, e.dia)
    eventos = {tipo: e.loc[en_calendario & (e.tipo == tipo)].groupby("clave").valor.agg(func)
               for tipo, func in [("SPLIT", "prod"), ("DIVIDENDO", "sum")]}
    fecha_salida = np.searchsorted(calendario, sal_dias, side="right")
    entra = fecha_salida < len(calendario)
    fs, si, rs = fecha_salida[entra], sal_ids[entra], s.retorno_final.to_numpy()[entra]
    n = len(calendario)
    mercado, cuenta, cartera = np.zeros(n), np.zeros(n), np.zeros(n)
    # Si un emisor cambia de bolsa, ordenar sus cotizaciones como una sola serie.
    compartidos = np.intersect1d(scl.id.unique(), nyc.id.unique())
    paneles = (scl, nyc)
    if compartidos.size:
        en_scl, en_nyc = scl.id.isin(compartidos), nyc.id.isin(compartidos)
        cruces = pd.concat([scl.loc[en_scl], nyc.loc[en_nyc]], ignore_index=True)
        if cruces.duplicated(["id", "dia"]).any():
            raise ValueError("Un emisor tiene dos cotizaciones vigentes en el mismo día")
        paneles = (scl.loc[~en_scl], nyc.loc[~en_nyc], cruces)
    for p in paneles:
        f, ids, r = retornos(p, calendario, tc, eventos)
        ok = np.isfinite(r)
        mercado += np.bincount(f[ok], weights=r[ok], minlength=n)
        cuenta += np.bincount(f[ok], minlength=n)
        ap = ok & (pesos[ids] != 0)
        cartera += np.bincount(f[ap], weights=r[ap] * pesos[ids[ap]], minlength=n)
    np.add.at(mercado, fs, rs)
    np.add.at(cuenta, fs, 1)
    np.add.at(cartera, fs, pesos[si] * rs)
    mercado = np.divide(mercado, cuenta, out=np.zeros(n), where=cuenta != 0)
    e_cart = e.loc[e.id.isin(posiciones)]
    calidad = dict(FILAS_SCL=c_scl[0], FILAS_NYC=c_nyc[0], DIAS_FONDO=n,
                   PARES_DUPLICADOS=c_scl[1] + c_nyc[1],
                   EMISORES_CON_CAMBIO_TICKER=int((m.groupby("id").ticker.nunique() > 1).sum()),
                   DIAS_FONDO_SIN_TC=int((~np.isin(calendario, tc_original.index)).sum()),
                   FILAS_POST_SALIDA=c_scl[2] + c_nyc[2],
                   SPLITS_CARTERA=int((e_cart.tipo == "SPLIT").sum()),
                   DIVIDENDOS_CARTERA=int((e_cart.tipo == "DIVIDENDO").sum()))
    escenarios = {}
    if auditar:
        p = pd.concat([scl_cart, nyc_cart], ignore_index=True)
        limpio = p.loc[p.dia.to_numpy() <= ultimo[p.id.to_numpy()]]
        for nombre, base, opciones in (
            ("sin_splits", limpio, {"usar_splits": False}),
            ("sin_dividendos", limpio, {"usar_div": False}),
            ("sin_conversion_usd", limpio, {"usar_tc": False}),
            ("sin_reglas_de_salida", p, {}),
        ):
            f, ids, r = retornos(base, calendario, tc, eventos, **opciones)
            ok = np.isfinite(r)
            alt = np.bincount(f[ok], weights=r[ok] * pesos[ids[ok]], minlength=n)
            if nombre != "sin_reglas_de_salida":
                np.add.at(alt, fs, pesos[si] * rs)
            escenarios[nombre] = alt
    return calendario.astype("datetime64[D]"), cartera, mercado, calidad, escenarios


def log_verosimilitud(exitos, total, p):
    return ((exitos * log(p) if exitos else 0)
            + ((total - exitos) * log(1 - p) if total > exitos else 0))


def cobertura(inc, prob):
    n = len(inc)
    k = int(inc.sum())
    lr = max(0, 2 * (log_verosimilitud(k, n, k/n) - log_verosimilitud(k, n, prob)))
    n00, n01, n10, n11 = np.bincount(2 * inc[:-1] + inc[1:], minlength=4)
    def ajustado(k, n):
        return log_verosimilitud(k, n, k/n) if n else 0
    ind = max(0, 2 * (ajustado(n01, n00+n01) + ajustado(n11, n10+n11)
                      - ajustado(n01+n11, n-1)))
    cc = lr + ind
    return lr, erfc(sqrt(lr/2)), ind, erfc(sqrt(ind/2)), cc, exp(-cc/2)


def riesgo(fechas, r, mercado, par):
    alfa, v = float(par.alfa), int(par.ventana)
    n = len(r)
    if v < 2 or n < 2*v:
        raise ValueError("Se requieren al menos dos ventanas para el pronóstico FHS")
    l = -r
    z = NormalDist().inv_cdf(alfa)
    q = np.quantile(l, alfa)
    sigma = r.std(ddof=1)
    ventanas = np.lib.stride_tricks.sliding_window_view(l, v)[:-1]
    hist = np.quantile(ventanas, alfa, axis=1)
    es = np.array([w[w >= h].mean() for w, h in zip(ventanas, hist)])
    normal = ventanas.mean(axis=1) + z * ventanas.std(axis=1, ddof=1)
    inicial = r[:v].var(ddof=1)
    rm = np.empty(n-v+1)
    garch = np.empty_like(rm)
    rm[0] = garch[0] = inicial
    lam, a, b = float(par["lambda"]), float(par.garch_alfa), float(par.garch_beta)
    omega = (1-a-b)*inicial
    for j, cuadrado in enumerate(r[v:]**2, 1):
        rm[j] = lam*rm[j-1] + (1-lam)*cuadrado
        garch[j] = omega + a*cuadrado + b*garch[j-1]
    srm, sg = np.sqrt(rm), np.sqrt(garch)
    est = np.divide(l[v:], srm[:-1], out=np.zeros(n-v), where=srm[:-1]>0)
    qf = np.quantile(np.lib.stride_tricks.sliding_window_view(est, v), alfa, axis=1)
    fhs = srm[v:] * qf
    pred = dict(hist=hist, normal=normal, rm=z*srm[:-1], garch=z*sg[:-1],
                fhs=np.r_[np.full(v, np.nan), fhs[:-1]])
    bt = pd.DataFrame({"fecha": fechas[v:], "perdida": l[v:],
                       "var_hist": hist, "es_hist": es})
    inc = {}
    for k, valor in pred.items():
        bt[f"var_{k}"] = valor
        inc[k] = (l[v:] > valor).astype(int)
    for k, valor in inc.items():
        bt[f"incumpl_{k}"] = (pd.Series(valor).mask(np.isnan(pred[k])).astype("Int64")
                              if k == "fhs" else valor)
    h, rm_test, g_test = (cobertura(inc[k], 1-alfa) for k in ("hist", "rm", "garch"))
    viola = inc["hist"].astype(bool)
    z2 = (l[v:][viola]/es[viola]).sum() / (len(es)*(1-alfa)) - 1
    var_m = np.var(mercado, ddof=1)
    m = dict(VAR_HIST=q, ES_HIST=l[l>=q].mean(), VAR_NORMAL=l.mean()+sigma*z,
             ES_NORMAL=l.mean()+sigma*exp(-z*z/2)/sqrt(2*pi)/(1-alfa),
             VAR_RM_SIGUIENTE=z*srm[-1], VAR_GARCH_SIGUIENTE=z*sg[-1], VAR_FHS_SIGUIENTE=fhs[-1],
             N_DIAS=n, RET_ACUM=np.prod(1+r)-1, BT_N_OBS=n-v)
    for k in ("hist", "normal", "rm", "garch"):
        m[f"BT_INCUMPL_{k.upper()}"] = int(inc[k].sum())
    m.update(zip(("KUPIEC_LR","KUPIEC_PVALOR","CHRIST_LR_IND","CHRIST_PVALOR_IND",
                  "CHRIST_LR_CC","CHRIST_PVALOR_CC"), h))
    m.update(KUPIEC_PVALOR_RM=rm_test[1], CHRIST_PVALOR_CC_RM=rm_test[5],
             KUPIEC_PVALOR_GARCH=g_test[1], CHRIST_PVALOR_CC_GARCH=g_test[5],
             BT_N_OBS_FHS=n-2*v, BT_INCUMPL_FHS=int(inc["fhs"].sum()),
             KUPIEC_PVALOR_FHS=cobertura(inc["fhs"][v:], 1-alfa)[1] if n>2*v else 1,
             ES_BT_Z2=z2, RET_ACUM_MERCADO=np.prod(1+mercado)-1,
             BETA_MERCADO=np.cov(r, mercado)[0,1]/var_m if var_m>0 else 0,
             VAR_HIST_ACTIVO=np.quantile(mercado-r, alfa))
    return m, bt


def main():
    par = pd.read_csv("parametros_riesgo.csv", dtype={"inicio": str}).iloc[0]
    cart = pd.read_csv("cartera.csv", dtype={"id": str})
    fecha, r, mercado, calidad, _ = construir_series(cart)
    muestra = fecha >= np.datetime64(par.inicio, "D")
    m, bt = riesgo(fecha[muestra], r[muestra], mercado[muestra], par)
    pd.Series(m).rename_axis("metrica").rename("valor").to_csv("riesgo.csv")
    pd.Series(calidad).rename_axis("indicador").rename("valor").to_csv("calidad_datos.csv")
    bt.to_csv("backtest.csv", index=False, date_format="%Y-%m-%d")


if __name__ == "__main__":
    main()
