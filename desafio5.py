"""FIN443 · Desafío 5. Ejecutar sin argumentos en la carpeta con los CSV."""

from math import exp, log, sqrt

import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.special import ndtr
from scipy.stats import binom

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


def normalizar_tasas(valor, escala, convencion):
    """Convertir cotizaciones con escala y convención identificadas por fila."""
    valor = np.asarray(valor, dtype=float)
    escala = np.broadcast_to(escala, valor.shape)
    convencion = np.broadcast_to(convencion, valor.shape)
    if not np.isfinite(valor).all() or not np.isin(escala, ["fraccion", "porcentaje"]).all():
        raise ValueError("Se requieren tasas finitas con escala explícita")
    tasa = np.where(escala == "porcentaje", valor / 100, valor)
    continua = tasa.copy()
    for nombre, frecuencia in (("efectiva_anual", 1), ("nominal_semestral", 2)):
        filas = convencion == nombre
        if np.any(tasa[filas] <= -frecuencia):
            raise ValueError(f"Tasa fuera del dominio de {nombre}")
        continua[filas] = frecuencia * np.log1p(tasa[filas] / frecuencia)
    if not np.isin(convencion, ["continua", "efectiva_anual", "nominal_semestral"]).all():
        raise ValueError("Convención de tasa desconocida")
    return continua


def factores_nss(plazos, tau1, tau2):
    """Matriz NSS, incluido el límite en plazo cero."""
    plazos = np.asarray(plazos, dtype=float)
    if not np.isfinite(plazos).all() or np.any(plazos < 0) or min(tau1, tau2) <= 0:
        raise ValueError("Se requieren plazos no negativos y taus positivos")
    x1, x2 = plazos / tau1, plazos / tau2
    carga1 = np.divide(-np.expm1(-x1), x1, out=np.ones_like(x1), where=x1 != 0)
    carga2 = np.divide(-np.expm1(-x2), x2, out=np.ones_like(x2), where=x2 != 0)
    return np.stack((np.ones_like(plazos), carga1, carga1 - np.exp(-x1),
                     carga2 - np.exp(-x2)), axis=-1)


def ajustar_nss(plazos, tasas, grilla_tau1, grilla_tau2):
    """Seleccionar los taus por error cuadrático y obtener los betas por MCO."""
    plazos, tasas = np.asarray(plazos, dtype=float), np.asarray(tasas, dtype=float)
    if plazos.ndim != 1 or plazos.shape != tasas.shape or np.unique(plazos).size < 6:
        raise ValueError("Se requieren tasas para al menos seis plazos distintos")
    if not np.isfinite(tasas).all():
        raise ValueError("Las tasas deben ser finitas")
    grilla_tau2 = tuple(grilla_tau2)
    mejor = None
    for tau1 in grilla_tau1:
        for tau2 in grilla_tau2:
            factores = factores_nss(plazos, tau1, tau2)
            betas, _, rango, _ = np.linalg.lstsq(factores, tasas, rcond=None)
            if rango == 4:
                error = float(np.mean((factores @ betas - tasas) ** 2))
                if mejor is None or error < mejor[-1]:
                    mejor = (betas, tau1, tau2, error)
    if mejor is None:
        raise ValueError("La grilla no permite identificar los betas NSS")
    return mejor


def riesgo_acciones(fechas, total, precio, inicio, valoracion, ventana, horizonte,
                    lam, alfa, beta, dias_anuales=252):
    """Medir q y las tres volatilidades con retorno de precio hasta la valoración."""
    fechas = np.asarray(fechas, dtype="datetime64[D]")
    desde, hasta = np.datetime64(inicio, "D"), np.datetime64(valoracion, "D")
    muestra = (fechas >= desde) & (fechas <= hasta)
    fechas_muestra = fechas[muestra]
    if ventana < 2 or horizonte < 1 or dias_anuales <= 0 or len(fechas_muestra) < ventana:
        raise ValueError("Ventana, horizonte o número de datos insuficiente")
    if not np.all(fechas_muestra[1:] > fechas_muestra[:-1]):
        raise ValueError("Las fechas de la muestra deben estar ordenadas y ser únicas")
    if not (0 < lam < 1 and alfa >= 0 and beta >= 0 and alfa + beta < 1):
        raise ValueError("Se requiere 0 < lambda < 1 y GARCH estacionario")

    total = np.asarray(total, dtype=float)[muestra]
    precio = np.asarray(precio, dtype=float)[muestra]
    if not np.isfinite(total).all() or not np.isfinite(precio).all() or min(total.min(), precio.min()) <= -1:
        raise ValueError("Los retornos de la muestra deben ser finitos y mayores que -1")
    ultimos = precio[-ventana:]
    q = np.log1p(np.sum(total[-dias_anuales:] - precio[-dias_anuales:]))
    var_hist = ultimos.var(ddof=1)
    var_largo = precio[:ventana].var(ddof=1)
    var_ewma = var_garch = var_largo
    persistencia = alfa + beta
    omega = (1 - persistencia) * var_largo
    for cuadrado in precio[ventana:] ** 2:
        var_ewma = lam * var_ewma + (1 - lam) * cuadrado
        var_garch = omega + alfa * cuadrado + beta * var_garch
    pronostico = var_largo + (var_garch - var_largo) * (
        persistencia ** np.arange(horizonte)
    )
    return {
        "ultima_fecha": fechas_muestra[-1],
        "n_retornos": len(fechas_muestra),
        "q": float(q),
        "sigma_historica": sqrt(dias_anuales * var_hist),
        "sigma_ewma": sqrt(dias_anuales * var_ewma),
        "sigma_garch": sqrt(dias_anuales * pronostico.mean()),
        "sigma_garch_acumulada": sqrt(pronostico.sum()),
    }


def riesgo_cartera(inicio, valoracion, ventana, horizonte, lam, alfa, beta):
    """Leer las bases del D4 y construir ambas versiones de la cuota."""
    cartera = pd.read_csv("cartera.csv", dtype={"id": str})
    fechas, total, _, _, escenarios = construir_series(cartera, auditar=True)
    return riesgo_acciones(fechas, total, escenarios["sin_dividendos"], inicio,
                           valoracion, ventana, horizonte, lam, alfa, beta)


def black_scholes(spot, strike, plazo, tasa, q, sigma):
    """Call, put y griegas de la put. Vega mide un cambio unitario de sigma."""
    if not (spot > 0 and strike > 0 and sigma >= 0 and plazo >= 0):
        raise ValueError("Spot y strike positivos, plazo y sigma no negativos")
    spot_vp = spot * exp(-q * plazo)
    strike_vp = strike * exp(-tasa * plazo)
    if sigma == 0 or plazo == 0:
        diferencia = spot_vp - strike_vp
        delta = -exp(-q * plazo) if diferencia < 0 else 0.0
        gamma = vega = 0.0
        if diferencia == 0:
            delta = gamma = vega = np.nan
        return max(diferencia, 0), max(-diferencia, 0), delta, gamma, vega

    raiz_t = sqrt(plazo)
    desv = sigma * raiz_t
    d1 = (log(spot / strike) + (tasa - q + sigma**2 / 2) * plazo) / desv
    d2 = d1 - desv
    densidad = exp(-d1**2 / 2) / sqrt(2 * np.pi)
    call = spot_vp * ndtr(d1) - strike_vp * ndtr(d2)
    put = strike_vp * ndtr(-d2) - spot_vp * ndtr(-d1)
    delta = -exp(-q * plazo) * ndtr(-d1)
    gamma = exp(-q * plazo) * densidad / (spot * desv)
    vega = spot_vp * densidad * raiz_t
    return call, put, delta, gamma, vega


def put_crr(spot, strike, plazo, tasa, q, sigma, pasos):
    """Esperanza terminal del árbol CRR para una put europea."""
    if pasos < 1:
        raise ValueError("El árbol requiere al menos un paso")
    if sigma == 0 or plazo == 0:
        return black_scholes(spot, strike, plazo, tasa, q, sigma)[1]
    dt = plazo / pasos
    salto = sigma * sqrt(dt)
    p = np.expm1((tasa - q) * dt + salto) / np.expm1(2 * salto)
    if not 0 <= p <= 1:
        raise ValueError("Aumente los pasos para obtener una probabilidad CRR válida")
    alzas = np.arange(pasos + 1)
    terminal = spot * np.exp((2 * alzas - pasos) * salto)
    pago = np.maximum(strike - terminal, 0)
    return float(exp(-tasa * plazo) * (pago @ binom.pmf(alzas, pasos, p)))


def put_monte_carlo(spot, strike, plazo, tasa, q, sigma, pares, semilla):
    """Precio y error estándar de una put con pares antitéticos."""
    if pares < 2:
        raise ValueError("Se requieren al menos dos pares antitéticos")
    z = np.random.default_rng(semilla).standard_normal(pares)
    centro = spot * exp((tasa - q - sigma**2 / 2) * plazo)
    choque = sigma * sqrt(plazo) * z
    pago_par = (np.maximum(strike - centro * np.exp(choque), 0)
                + np.maximum(strike - centro * np.exp(-choque), 0)) / 2
    vp = exp(-tasa * plazo) * pago_par
    return float(vp.mean()), float(vp.std(ddof=1) / sqrt(pares))


def collar_costo_cero(spot, strike_put, plazo, tasa, q, sigma):
    """Strike de la call con prima igual a la de la put, si está sobre spot."""
    prima = black_scholes(spot, strike_put, plazo, tasa, q, sigma)[1]
    if prima <= 0 or black_scholes(spot, spot, plazo, tasa, q, sigma)[0] <= prima:
        raise ValueError("No hay collar de costo cero con strike de la call sobre spot")

    def saldo(strike_call):
        return black_scholes(spot, strike_call, plazo, tasa, q, sigma)[0] - prima

    techo = 2 * spot
    while saldo(techo) > 0:
        techo *= 2
    return brentq(saldo, spot, techo)


def valorar_cobertura(spot, strike, plazo, tasa, q, sigma, pasos, pares, semilla):
    """Comparar métodos y medir el costo económico de la protección."""
    call, put, delta, gamma, vega = black_scholes(spot, strike, plazo, tasa, q, sigma)
    crr = put_crr(spot, strike, plazo, tasa, q, sigma, pasos)
    mc, error = put_monte_carlo(spot, strike, plazo, tasa, q, sigma, pares, semilla)
    strike_call = None
    if 0 < put < black_scholes(spot, spot, plazo, tasa, q, sigma)[0]:
        strike_call = collar_costo_cero(spot, strike, plazo, tasa, q, sigma)
    return {
        "call_bs": call, "put_bs": put, "put_crr": crr, "put_mc": mc,
        "error_estandar_mc": error, "delta_put": delta, "gamma_put": gamma,
        "vega_put": vega, "strike_call_collar": strike_call,
        "perdida_maxima_put": spot - strike + put * exp(tasa * plazo),
    }


def riesgo_bonos(plazos, flujos, curva, choque=0.01):
    """Valorar flujos de bonos y medir el efecto de mover toda la curva."""
    plazos, flujos = np.asarray(plazos, dtype=float), np.asarray(flujos, dtype=float)
    if plazos.ndim != 1 or plazos.shape != flujos.shape or not len(plazos):
        raise ValueError("Se requieren plazos y flujos de los mismos pagos")
    if (not np.isfinite(plazos).all() or not np.isfinite(flujos).all()
            or np.any(plazos <= 0) or np.any(flujos < 0) or flujos.sum() <= 0):
        raise ValueError("Se requieren flujos no negativos con plazos futuros y valor positivo")

    def valor(desplazamiento):
        return float(flujos @ np.exp(-(curva(plazos) + desplazamiento) * plazos))

    h = 0.0001
    base, baja, sube = valor(0), valor(-h), valor(h)
    dv01 = (baja - sube) / 2
    duracion = dv01 / (base * h)
    convexidad = (sube + baja - 2 * base) / (base * h**2)
    return {
        "valor": base, "duracion": duracion, "convexidad": convexidad, "dv01": dv01,
        "cambio_pct_exacto": valor(choque) / base - 1,
        "cambio_pct_aproximado": -duracion * choque + convexidad * choque**2 / 2,
    }


def leer_curva():
    """La convención por fila prevalece sobre la nota general del proveedor."""
    tasas = pd.read_csv("tasas_mercado.csv", comment="#")
    n = len(tasas)
    nuevas = tasas.sort_values("version", kind="stable").drop_duplicates("instrumento", keep="last")
    usadas = nuevas.loc[nuevas.estado == "ok"].copy()
    porcentaje = usadas.tasa.abs() > 1
    escalas = np.where(porcentaje, "porcentaje", "fraccion")
    factores = usadas.unidad.map({"anos": 1, "meses": 1/12, "dias": 1/365})
    if factores.isna().any():
        raise ValueError("Unidad de plazo desconocida")
    plazos = usadas.plazo.to_numpy() * factores.to_numpy()
    ceros = normalizar_tasas(usadas.tasa, escalas, usadas.convencion)
    ajuste = ajustar_nss(plazos, ceros, np.arange(0.25, 5.01, 0.25),
                         np.arange(5.5, 20.01, 0.5))
    calidad = {
        "FILAS_TASAS": n, "FILAS_VERSION_ANTIGUA": n-len(nuevas),
        "FILAS_STALE": len(nuevas)-len(usadas), "TASAS_USADAS": len(usadas),
        "TASAS_EN_PORCENTAJE": int(porcentaje.sum()),
        "PLAZOS_EN_DIAS": int((usadas.unidad == "dias").sum()),
        "PLAZOS_EN_MESES": int((usadas.unidad == "meses").sum()),
        "TASAS_CONTINUAS": int((usadas.convencion == "continua").sum()),
        "TASAS_EFECTIVAS": int((usadas.convencion == "efectiva_anual").sum()),
        "TASAS_NOMINAL_SEMESTRAL": int((usadas.convencion == "nominal_semestral").sum()),
    }
    return ajuste, calidad


def flujos_bonos(valoracion):
    bonos = pd.read_csv("bonos_fondo.csv")
    fecha = pd.Timestamp(valoracion)
    bonos["vencimiento"] = pd.to_datetime(bonos.vencimiento)
    vigentes = bonos.loc[bonos.vencimiento > fecha]
    plazos, flujos = [], []
    for bono in vigentes.itertuples():
        frecuencia = int(bono.frecuencia)
        if frecuencia <= 0 or 12 % frecuencia:
            raise ValueError("La frecuencia debe dividir los doce meses del año")
        k = 0
        while True:
            pago = bono.vencimiento - pd.DateOffset(months=k * (12 // frecuencia))
            if pago <= fecha:
                break
            plazos.append((pago-fecha).days / 365)
            flujos.append(bono.nominal_usd_mm * (
                bono.cupon_anual_pct / 100 / frecuencia + (k == 0)))
            k += 1
    return np.array(plazos), np.array(flujos), len(vigentes), len(bonos)-len(vigentes)


def calcular_resultados():
    par = pd.read_csv("parametros_D5.csv", dtype={"fecha_valoracion": str, "inicio": str}).iloc[0]
    (betas, tau1, tau2, mse), calidad = leer_curva()

    def curva(plazos):
        return factores_nss(plazos, tau1, tau2) @ betas

    tasa = float(curva(float(par["T"])))
    acc = riesgo_cartera(par.inicio, par.fecha_valoracion, int(par.ventana),
                        int(par.horizonte_dias), float(par["lambda"]),
                        float(par.garch_alfa), float(par.garch_beta))
    spot, plazo = float(par.S0), float(par["T"])
    strike = float(par.k_put) * spot
    q, sigma = acc["q"], acc["sigma_garch"]
    if int(par.n_mc) % 2:
        raise ValueError("n_mc debe ser par para los pares antitéticos")
    op = valorar_cobertura(spot, strike, plazo, tasa, q, sigma,
                          int(par.N_binomial), int(par.n_mc)//2, int(par.semilla_mc))
    d2 = (log(spot/strike)+(tasa-q-sigma*sigma/2)*plazo)/(sigma*sqrt(plazo))
    tiempos, pagos, vivos, vencidos = flujos_bonos(par.fecha_valoracion)
    bonos = riesgo_bonos(tiempos, pagos, curva, float(par.shock_pb)/10000)
    shock = float(par.shock_pb)/10000
    resultados = {
        **dict(zip(("NSS_B0", "NSS_B1", "NSS_B2", "NSS_B3"), betas)),
        "NSS_TAU1": tau1, "NSS_TAU2": tau2, "NSS_RMSE_PB": sqrt(mse)*10000,
        "R_T": tasa, "N_DIAS_HIST": acc["n_retornos"], "Q_DIVIDENDOS": q,
        "SIGMA_HIST": acc["sigma_historica"], "SIGMA_EWMA": acc["sigma_ewma"],
        "SIGMA_GARCH_T": sigma, "BS_PUT": op["put_bs"], "BS_CALL": op["call_bs"],
        "PARIDAD": op["call_bs"]-op["put_bs"]-(spot*exp(-q*plazo)-strike*exp(-tasa*plazo)),
        "BIN_PUT": op["put_crr"], "MC_PUT": op["put_mc"], "MC_SE": op["error_estandar_mc"],
        "PUT_DELTA": op["delta_put"], "PUT_GAMMA": op["gamma_put"],
        "PUT_VEGA": op["vega_put"]/100, "PROB_EJERCICIO": float(ndtr(-d2)),
        "BS_PUT_SIGMA_HIST": black_scholes(spot,strike,plazo,tasa,q,acc["sigma_historica"])[1],
        "BS_PUT_SIGMA_EWMA": black_scholes(spot,strike,plazo,tasa,q,acc["sigma_ewma"])[1],
        "PERDIDA_MAX_CUBIERTA": op["perdida_maxima_put"]/spot,
        "COLLAR_K_CALL": op["strike_call_collar"], "N_BONOS_VIGENTES": vivos,
        "VALOR_BONOS": bonos["valor"], "DURACION_MOD": bonos["duracion"],
        "CONVEXIDAD": bonos["convexidad"], "DV01": bonos["dv01"],
        "CAMBIO_SHOCK_REAL": bonos["cambio_pct_exacto"],
        "CAMBIO_SHOCK_DURACION": -bonos["duracion"]*shock,
        "CAMBIO_SHOCK_DUR_CONV": bonos["cambio_pct_aproximado"],
    }
    calidad["BONOS_VENCIDOS"] = vencidos
    return resultados, calidad


def main():
    resultados, calidad = calcular_resultados()
    pd.Series(resultados).rename_axis("metrica").rename("valor").to_csv("resultados_D5.csv")
    pd.Series(calidad).rename_axis("indicador").rename("valor").to_csv("calidad_tasas.csv")


if __name__ == "__main__":
    main()
