"""Validación independiente con NumPy; no es parte del programa a entregar.

Uso: python tests/verificar_desafio3.py precios_desafio3.csv
Compara todas las métricas y pesos, ERC por Newton independiente, formatos,
permutaciones, nombres y prueba de prefijo contra look-ahead.
"""
import csv
import datetime as dt
import pathlib
import subprocess
import sys
import tempfile
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / 'precios_desafio3.csv')


def read_prices(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        first = f.readline()
        sep = ';' if first.count(';') > first.count(',') else ','
        f.seek(0)
        rows = list(csv.reader(f, delimiter=sep))
    names = rows.pop(0)
    records = {}
    for row in rows:
        date = dt.datetime.strptime(row[0], '%d-%m-%Y' if sep == ';' else '%Y-%m-%d').date()
        if date in records:
            assert records[date] == row[1:], 'Duplicado no idéntico'
        records[date] = row[1:]
    dates = sorted(records)
    p = np.array([[float(x.replace(',', '.')) if x else np.nan for x in records[d]] for d in dates])
    missing = np.isnan(p).sum(axis=0)
    events = []
    for j in range(p.shape[1]):
        idx = np.flatnonzero(~np.isnan(p[:, j]))
        factors = np.ones(len(dates))
        for prev, cur in zip(idx, idx[1:]):
            for k in (2, 3, 4, 5):
                if abs(p[cur, j] / p[prev, j] * k - 1) <= .05 + 1e-12:
                    factors[cur] = k
                    events.append((names[j+1], str(dates[cur]), k))
                    break
        # Producto de factores estrictamente futuros; distinto al bucle R.
        future = np.cumprod(factors[::-1])[::-1] / factors
        p[:, j] /= future
        last = np.nan
        for i in range(len(p)):
            if np.isnan(p[i, j]):
                p[i, j] = last
            else:
                last = p[i, j]
    r = p[1:] / p[:-1] - 1
    valid = np.isfinite(r).all(axis=1)
    print('Entrada:', len(rows), 'filas;', len(dates), 'fechas únicas; NA:', missing.tolist(), 'splits:', events)
    return names[1:], np.array(dates[1:], dtype=object)[valid], r[valid]


def estimate(r, rf):
    s = np.atleast_2d(np.cov(r, rowvar=False, ddof=1)) * 252
    u = np.ones(r.shape[1])
    a = np.linalg.solve(s, u)
    z = np.linalg.solve(s, r.mean(axis=0) * 252 - rf)
    invvol = 1 / np.std(r, axis=0, ddof=1)
    # Newton con Hessiano analítico para el objetivo convexo ERC.
    q = s / np.mean(np.diag(s))
    b = u / len(u)
    x = np.sqrt(b / np.diag(q))
    def objective(y):
        return .5 * y @ q @ y - b @ np.log(y)
    for _ in range(100):
        g = q @ x - b / x
        if np.max(np.abs(g)) < 1e-12:
            break
        direction = np.linalg.solve(q + np.diag(b / x**2), g)
        alpha = 1.
        while np.any(x - alpha * direction <= 0) or objective(x-alpha*direction) > objective(x) - 1e-4 * alpha * (g @ direction):
            alpha *= .5
            if alpha < 1e-14:
                break
        x -= alpha * direction
    erc = x / x.sum()
    assert np.max(np.abs(erc * (s @ erc) / (erc @ s @ erc) - b)) < 1e-8
    return dict(MINVAR=a/a.sum(), MAXSHARPE=z/z.sum(), EW=b, INVVOL=invvol/invvol.sum(), ERC=erc)


def metrics(r, first, last, rf):
    wealth = np.r_[1., np.cumprod(1+r)]
    vol = np.std(r, ddof=1) * np.sqrt(252)
    return np.array([wealth[-1]**(365.25/(last-first).days)-1, vol,
                     (np.mean(r)*252-rf)/vol, np.max(1-wealth/np.maximum.accumulate(wealth))])


def reference(dates, r, rf):
    n = len(r)
    ends = [i for i in range(n-1) if dates[i].month != dates[i+1].month or dates[i].year != dates[i+1].year]
    ends = [i for i in ends if i >= 251]
    assert ends
    w_is = estimate(r, rf)
    w_first = estimate(r[ends[0]-251:ends[0]+1], rf)
    expected = {}
    for key, w in w_is.items():
        expected['IS_'+key] = metrics(r @ w, dates[0], dates[-1], rf)
    all_gross = {k: [] for k in ('MINVAR','EW','INVVOL','ERC')}
    all_net = {k: [] for k in all_gross}
    turnovers = {k: [] for k in all_gross}
    max_erc_error = 0.
    prior = None
    for j, t in enumerate(ends):
        w = estimate(r[t-251:t+1], rf)
        s = np.atleast_2d(np.cov(r[t-251:t+1], rowvar=False))*252
        max_erc_error = max(max_erc_error, np.max(np.abs(w['ERC']*(s@w['ERC'])/(w['ERC']@s@w['ERC'])-1/r.shape[1])))
        stop = ends[j+1]+1 if j+1<len(ends) else n
        for key in all_gross:
            gross = r[t+1:stop] @ w[key]
            turnover = np.abs(w[key]).sum() if prior is None else np.abs(w[key]-prior[key]).sum()
            net = gross.copy()
            net[0] -= .001 * turnover
            all_gross[key].extend(gross)
            all_net[key].extend(net)
            turnovers[key].append(turnover)
        prior = w
    for key in all_gross:
        gross = np.array(all_gross[key]); net = np.array(all_net[key])
        expected['BT_'+key] = np.r_[metrics(gross, dates[ends[0]], dates[-1], rf),
            np.mean(turnovers[key][1:]) if len(ends)>1 else 0,
            (np.mean(net)*252-rf)/(np.std(net,ddof=1)*np.sqrt(252))]
    print('R:', n, 'retornos; primer rebalanceo:', dates[ends[0]], '; rebalanceos:', len(ends))
    print('Error máximo ERC independiente:', max_erc_error)
    return expected, w_is, w_first, ends


def run(path, output, rf=.05):
    result = subprocess.run(['Rscript',str(ROOT/'desafio3.R'),str(path),str(output),str(rf)], check=True,capture_output=True,text=True)
    with (output/'metricas.csv').open() as f: m = list(csv.DictReader(f))
    with (output/'pesos.csv').open() as f: p = list(csv.DictReader(f))
    return m,p


def compare(ref, names, w_is, w_first, actual):
    m,p = actual
    differences=[]
    for row in m:
        cols = ['cagr','vol','sharpe','mdd'] + ([] if row['cartera'].startswith('IS_') else ['rotacion','sharpe_neto'])
        differences.extend(np.abs(np.array([float(row[k]) for k in cols])-ref[row['cartera']]))
    for row in p:
        prefix,key = row['cartera'].split('_',1)
        correct = w_is if prefix=='IS' else w_first
        differences.append(abs(float(row['peso'])-correct[key][names.index(row['activo'])]))
    err=max(differences)
    assert err < 1e-7, err
    print('OK todas las métricas y pesos vs NumPy; diferencia máxima:',err)


names,dates,r = read_prices(SOURCE)
ref, wi, wf, ends = reference(dates,r,.05)
with tempfile.TemporaryDirectory(prefix='fin443-d3-') as tmp:
    tmp=pathlib.Path(tmp)
    public=run(SOURCE,tmp/'public')
    compare(ref,names,wi,wf,public)
    ref3,wi3,wf3,_=reference(dates,r,.03)
    compare(ref3,names,wi3,wf3,run(SOURCE,tmp/'rf03',.03))
    with SOURCE.open(encoding='utf-8-sig',newline='') as f:
        raw=list(csv.reader(f,delimiter=';'))
    header,body=raw[0],raw[1:]
    def write_variant(label, rows, international=False, renamed=False):
        path=tmp/(label+'.csv')
        with path.open('w',newline='',encoding='utf-8-sig') as f:
            writer=csv.writer(f,delimiter=',' if international else ';')
            writer.writerow(header if not renamed else [header[0]]+['ACCIÓN '+str(i) for i in range(len(names))])
            for row in rows:
                if international:
                    row=[dt.datetime.strptime(row[0],'%d-%m-%Y').strftime('%Y-%m-%d')]+[v.replace(',','.') for v in row[1:]]
                writer.writerow(row)
        return path
    for label,rows,international,renamed in [('inverso',body[::-1],False,False),('internacional',body,True,False),('duplicados',body+body[80:83],False,False),('tildes',body,True,True)]:
        actual=run(write_variant(label,rows,international,renamed),tmp/label)
        assert np.allclose([[float(x[k]) for k in ['cagr','vol','sharpe','mdd']] for x in actual[0]], [[float(x[k]) for k in ['cagr','vol','sharpe','mdd']] for x in public[0]],atol=1e-12)
        assert np.allclose([float(x['peso']) for x in actual[1]],[float(x['peso']) for x in public[1]],atol=1e-12)
        print('OK transformación:',label)
    cutoff=dates[ends[0]+3]
    prefix=[row for row in body if dt.datetime.strptime(row[0],'%d-%m-%Y').date()<=cutoff]
    short=run(write_variant('prefijo',prefix),tmp/'prefijo')
    a=[float(x['peso']) for x in public[1] if x['cartera'].startswith('BT1_')]
    b=[float(x['peso']) for x in short[1] if x['cartera'].startswith('BT1_')]
    assert np.max(np.abs(np.array(a)-b))<1e-10
    print('OK sin look-ahead: BT1 no cambia al truncar después de',cutoff)
    # Tres activos, inicio tardío y dos splits en un mismo activo.
    rng=np.random.default_rng(443)
    simulated=100*np.cumprod(1+rng.normal(.0003,.012,size=(650,3)),axis=0)
    simulated[300:,0]/=2; simulated[450:,0]/=3
    simulated[:35,2]=np.nan; simulated[[70,71,299,300],1]=np.nan
    sd=[dt.date(2020,1,1)+dt.timedelta(days=i) for i in range(650)]
    syn=tmp/'simulado.csv'
    with syn.open('w',newline='') as f:
        writer=csv.writer(f); writer.writerow(['Fecha','BANCO SUR','SALMÓN','NUEVO'])
        for date,values in zip(sd,simulated):
            writer.writerow([date.isoformat()]+['' if np.isnan(x) else format(x,'.12g') for x in values])
    sn,ds,rs=read_prices(syn)
    ex,x,y,_=reference(ds,rs,.05)
    compare(ex,sn,x,y,run(syn,tmp/'simulado'))
    print('OK robustez: tres activos, NA, inicio tardío y múltiples splits')
print('VALIDACIÓN INDEPENDIENTE COMPLETA')
