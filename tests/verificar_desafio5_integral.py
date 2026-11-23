"""Prueba end-to-end D5: diez CSV sintéticos, subproceso aislado y oráculo independiente.
No importa funciones del programa evaluado. No modifica datos ni cartera personales.
Uso: python3 prueba_integral.py /ruta/desafio5.py carpeta_evidencia
Requiere Python con numpy/pandas y Rscript para el contraste independiente adjunto.
"""
from pathlib import Path
import calendar,csv,hashlib,json,math,shutil,subprocess,sys,time
import numpy as np
import pandas as pd

M='NSS_B0 NSS_B1 NSS_B2 NSS_B3 NSS_TAU1 NSS_TAU2 NSS_RMSE_PB R_T N_DIAS_HIST Q_DIVIDENDOS SIGMA_HIST SIGMA_EWMA SIGMA_GARCH_T BS_PUT BS_CALL PARIDAD BIN_PUT MC_PUT MC_SE PUT_DELTA PUT_GAMMA PUT_VEGA PROB_EJERCICIO BS_PUT_SIGMA_HIST BS_PUT_SIGMA_EWMA PERDIDA_MAX_CUBIERTA COLLAR_K_CALL N_BONOS_VIGENTES VALOR_BONOS DURACION_MOD CONVEXIDAD DV01 CAMBIO_SHOCK_REAL CAMBIO_SHOCK_DURACION CAMBIO_SHOCK_DUR_CONV'.split()
Q='FILAS_TASAS FILAS_VERSION_ANTIGUA FILAS_STALE TASAS_USADAS TASAS_EN_PORCENTAJE PLAZOS_EN_DIAS PLAZOS_EN_MESES TASAS_CONTINUAS TASAS_EFECTIVAS TASAS_NOMINAL_SEMESTRAL BONOS_VENCIDOS'.split()
INPUTS='maestro_emisores precios_SCL precios_NYC tipo_cambio eventos_corporativos salidas_de_bolsa cartera tasas_mercado bonos_fondo parametros_D5'.split()

def escribir(folder,name,rows,columns,sep=',',decimal='.'):
    pd.DataFrame(rows,columns=columns).to_csv(folder/(name+'.csv'),index=False,sep=sep,decimal=decimal,float_format='%.15g')

def generar(folder,case):
    folder.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(834+case)
    valuation=pd.Timestamp(['2021-11-15','2024-02-29','2023-09-18'][case])
    dates=pd.bdate_range(end=valuation,periods=441+case*30)
    dates=dates.append(pd.bdate_range(start=valuation+pd.offsets.BDay(),periods=24))
    ids=['SYN'+str(i).zfill(3) for i in range(20)]
    weights=rng.dirichlet(np.ones(20)*3)
    escribir(folder,'cartera',zip(ids,weights),['id','peso'])
    master=[]
    for j,id_ in enumerate(ids):
        if j==0:
            master.extend([[id_,'PREV0','SCL','CLP',dates[0].date(),(dates[120]-pd.Timedelta(days=1)).date()],
                           [id_,'NEW0','SCL','CLP',dates[120].date(),'9999-12-31']])
        elif j==1:
            master.extend([[id_,'MOVE_S','SCL','CLP',dates[0].date(),(dates[200]-pd.Timedelta(days=1)).date()],
                           [id_,'MOVE_N','NYC','USD',dates[200].date(),'9999-12-31']])
        else:master.append([id_,'T'+str(j),'SCL' if j<10 else 'NYC','CLP' if j<10 else 'USD',dates[0].date(),'9999-12-31'])
    escribir(folder,'maestro_emisores',master,['id','ticker','bolsa','moneda','desde','hasta'])
    fxvals={}
    for k,dt in enumerate(dates):
        if k%4==0:fxvals[dt]=700+case*25+0.12*k+10*math.sin(k/16)
    escribir(folder,'tipo_cambio',[(d.strftime('%d-%m-%Y'),x) for d,x in fxvals.items()],['fecha','clp_por_usd'],';',',')
    common=rng.normal(.00012,.009+case*.001,len(dates));scl=[];nyc=[];events=[]
    fx=next(iter(fxvals.values()))
    for j,id_ in enumerate(ids):
        economic=30+4*j;divisor=1
        shock=rng.normal(.00005,.007,len(dates))
        for k,dt in enumerate(dates):
            if dt in fxvals:fx=fxvals[dt]
            economic*=math.exp(common[k]+shock[k])
            split=2 if j in (0,12) and k==220 else 1
            divisor*=split
            bolsa='SCL' if j<10 and not(j==1 and k>=200) else 'NYC'
            ticker=('PREV0' if k<120 else 'NEW0') if j==0 else ('MOVE_S' if k<200 else 'MOVE_N') if j==1 else 'T'+str(j)
            if (j==19 and k<45) or (bolsa=='SCL' and k%37==15):continue
            close=economic/divisor*(fx if bolsa=='SCL' else 1)
            if split!=1:events.append([ticker,dt.strftime('%Y-%m-%d'),'SPLIT',split])
            if k in (100,220,320,400) and j%3==0:events.append([ticker,dt.strftime('%Y-%m-%d'),'DIVIDENDO',close*.004])
            row=[dt.strftime('%d/%m/%Y' if bolsa=='SCL' else '%Y-%m-%d'),ticker,close,10000+j,3]
            dest=scl if bolsa=='SCL' else nyc;dest.append(row)
            if k in (80,230) and j in (0,10):dest.append([row[0],ticker,close*1.19,100,1])
    escribir(folder,'precios_SCL',scl,['fecha','ticker','cierre','volumen','version'],';',',')
    escribir(folder,'precios_NYC',nyc,['date','ticker','close','volume','version'])
    escribir(folder,'eventos_corporativos',events,['ticker','fecha','tipo','valor'])
    escribir(folder,'salidas_de_bolsa',[[ids[18],dates[300].strftime('%Y-%m-%d'),'OPA',-.17-case*.01]],['id','ultimo_dia','evento','retorno_final'],';',',')
    betas=np.array([[.034,-.008,.012,-.006],[.043,-.011,.016,-.009],[.027,.006,-.012,.008]][case])
    taus=[(1.75,10.5),(2.25,7.5),(.75,14)][case]
    quotes=[]
    for i,t in enumerate([30/365,.25,.5,1,2,3,5,8,12,20,30]):
        a,b=taus;f=(1-math.exp(-t/a))/(t/a);g=(1-math.exp(-t/b))/(t/b)
        z=betas@np.array([1,f,f-math.exp(-t/a),g-math.exp(-t/b)])
        conv=['continua','efectiva_anual','nominal_semestral'][i%3]
        rate=z if i%3==0 else math.expm1(z) if i%3==1 else 2*math.expm1(z/2)
        rate*=100 if i%2==0 else 1
        unit='dias' if i==0 else 'meses' if i in (1,2,3,4) else 'anos'
        tenor=t*365 if unit=='dias' else t*12 if unit=='meses' else t
        quotes.append(['Z'+str(i),tenor,unit,rate,conv,'ok',3])
        if i in (2,5):quotes.append(['Z'+str(i),tenor,unit,rate*1.4,conv,'ok',1])
    quotes.extend([['STALE',1.8,'anos',9,'continua','stale',5],['STALE',1.8,'anos',.04,'continua','ok',1],['X',17,'meses',7,'efectiva_anual','stale',2]])
    escribir(folder,'tasas_mercado',quotes,['instrumento','plazo','unidad','tasa','convencion','estado','version'])
    path=folder/'tasas_mercado.csv';path.write_text('# Nota del proveedor: todas las tasas son continuas.\n'+path.read_text())
    y=valuation.year
    bonds=[['ZERO',12+case,0,1,f'{y+3}-06-15'],['SEMI',18,4.2+case*.2,2,f'{y+6}-09-15'],['QUARTER',9,3.8,4,f'{y+2}-12-15'],['ANNUAL',15,5.1,1,f'{y+10}-03-15'],['EXPIRED',7,4,2,f'{y-1}-05-15'],['TODAY',2,3,1,valuation.strftime('%Y-%m-%d')]]
    escribir(folder,'bonos_fondo',bonds,['bono','nominal_usd_mm','cupon_anual_pct','frecuencia','vencimiento'])
    par=dict(fecha_valoracion=valuation.strftime('%Y-%m-%d'),inicio=dates[10].strftime('%Y-%m-%d'),ventana=[90,180,125][case],garch_alfa=[.07,.05,.1][case],garch_beta=[.88,.93,.83][case],S0=[85,130,105][case],k_put=[.94,.92,.96][case],T=[.75,.25,1.1][case],horizonte_dias=[189,63,277][case],N_binomial=900,n_mc=80000,semilla_mc=107+case,shock_pb=[75,150,25][case])
    par['lambda']=[.96,.92,.97][case]
    pd.DataFrame([par]).to_csv(folder/'parametros_D5.csv',index=False)
    return dict(betas=betas.tolist(),tau1=taus[0],tau2=taus[1],dias=len(dates),caso=case)

def oracle_lector(folder):
    """Lector escalar escrito aparte: diccionarios, vigencias y pagos por emisor."""
    cart=pd.read_csv(folder/'cartera.csv',dtype={'id':str});w=dict(zip(cart.id,cart.peso))
    master=pd.read_csv(folder/'maestro_emisores.csv',dtype=str).to_dict('records')
    def emisor(ticker,day,bolsa=None):
        matches=[r['id'] for r in master if r['ticker']==ticker and r['desde']<=day<=r['hasta'] and (bolsa is None or r['bolsa']==bolsa)]
        assert len(matches)==1,(ticker,day,bolsa,matches)
        return matches[0]
    exits={r['id']:(r['ultimo_dia'],float(r['retorno_final'])) for r in pd.read_csv(folder/'salidas_de_bolsa.csv',sep=';',decimal=',').to_dict('records')}
    quotes={};calendar_days=set()
    for file,market,sep,dec,dc,pc,fmt in [('precios_SCL.csv','SCL',';',',','fecha','cierre','%d/%m/%Y'),('precios_NYC.csv','NYC',',','.','date','close','%Y-%m-%d')]:
        for r in pd.read_csv(folder/file,sep=sep,decimal=dec).to_dict('records'):
            day=pd.to_datetime(r[dc],format=fmt).strftime('%Y-%m-%d');calendar_days.add(day)
            key=(market,r['ticker'],day)
            if key not in quotes or r['version']>quotes[key]['version']:quotes[key]={**r,'day':day,'close':r[pc]}
    fx={pd.to_datetime(r['fecha'],format='%d-%m-%Y').strftime('%Y-%m-%d'):r['clp_por_usd'] for r in pd.read_csv(folder/'tipo_cambio.csv',sep=';',decimal=',').to_dict('records')}
    ev={}
    for r in pd.read_csv(folder/'eventos_corporativos.csv').to_dict('records'):
        key=(emisor(r['ticker'],r['fecha']),r['fecha']);item=ev.setdefault(key,{'split':1.,'div':0.})
        if r['tipo']=='SPLIT':item['split']*=r['valor']
        else:item['div']+=r['valor']
    by_day={d:[] for d in calendar_days}
    for (market,ticker,day),r in quotes.items():
        id_=emisor(ticker,day,market)
        if id_ in exits and day>exits[id_][0]:continue
        by_day[day].append((id_,market,r['close']))
    previous={};current_fx=None;out=[];paid=set()
    for day in sorted(calendar_days):
        if day in fx:current_fx=fx[day]
        total=price=0.
        for id_,market,close in by_day[day]:
            conversion=current_fx if market=='SCL' else 1.
            usd=close/conversion
            if id_ in previous:
                e=ev.get((id_,day),{'split':1.,'div':0.})
                rp=usd*e['split']/previous[id_]-1
                rt=rp+e['div']/conversion/previous[id_]
                total+=w.get(id_,0)*rt;price+=w.get(id_,0)*rp
            previous[id_]=usd
        for id_,(last,ret) in exits.items():
            if day>last and id_ not in paid:
                total+=w.get(id_,0)*ret;price+=w.get(id_,0)*ret;paid.add(id_)
        out.append((day,total,price))
    ans=pd.DataFrame(out,columns=['fecha','total','precio']);ans.to_csv(folder/'series_verificacion.csv',index=False)
    return ans

def quality_expected(folder):
    rows=pd.read_csv(folder/'tasas_mercado.csv',comment='#').to_dict('records');latest={}
    for r in rows:
        if r['instrumento'] not in latest or r['version']>latest[r['instrumento']]['version']:latest[r['instrumento']]=r
    used=[r for r in latest.values() if r['estado']=='ok']
    b=pd.read_csv(folder/'bonos_fondo.csv');p=pd.read_csv(folder/'parametros_D5.csv').iloc[0]
    values=[len(rows),len(rows)-len(latest),len(latest)-len(used),len(used),sum(abs(r['tasa'])>1 for r in used),sum(r['unidad']=='dias' for r in used),sum(r['unidad']=='meses' for r in used),sum(r['convencion']=='continua' for r in used),sum(r['convencion']=='efectiva_anual' for r in used),sum(r['convencion']=='nominal_semestral' for r in used),sum(b.vencimiento<=p.fecha_valoracion)]
    return dict(zip(Q,values))

def validar(folder,script,contraste):
    # La carpeta estaba vacía salvo los diez insumos; se copia únicamente el ejecutable.
    assert not (folder/'resultados_D5.csv').exists()
    shutil.copy2(script,folder/'desafio5.py')
    before={n:hashlib.sha256((folder/(n+'.csv')).read_bytes()).hexdigest() for n in INPUTS}
    start=time.perf_counter();proc=subprocess.run([sys.executable,'-I','desafio5.py'],cwd=folder,capture_output=True,text=True,timeout=120)
    elapsed=time.perf_counter()-start
    (folder/'ejecucion_programa.log').write_text(proc.stdout+proc.stderr)
    assert proc.returncode==0,(folder.name,proc.returncode,proc.stderr)
    assert before=={n:hashlib.sha256((folder/(n+'.csv')).read_bytes()).hexdigest() for n in INPUTS}
    r=pd.read_csv(folder/'resultados_D5.csv');q=pd.read_csv(folder/'calidad_tasas.csv')
    assert r.columns.tolist()==['metrica','valor'] and r.metrica.tolist()==M
    assert q.columns.tolist()==['indicador','valor'] and q.indicador.tolist()==Q
    assert np.isfinite(r.valor).all() and np.isfinite(q.valor).all()
    expected=quality_expected(folder)
    assert dict(zip(q.indicador,q.valor))==expected
    # Las series de referencia se construyen sin importar ni ejecutar el lector evaluado.
    oracle_lector(folder)
    rc=subprocess.run(['Rscript',str(contraste)],cwd=folder,capture_output=True,text=True,timeout=120)
    (folder/'contraste_independiente.log').write_text(rc.stdout+rc.stderr)
    assert rc.returncode==0,(folder.name,rc.stdout,rc.stderr)
    values=dict(zip(r.metrica,r.valor));p=pd.read_csv(folder/'parametros_D5.csv').iloc[0]
    # Reproducir el precio y SE con la semilla Python por un bucle escalar independiente.
    S,K,T=float(p.S0),float(p.S0*p.k_put),float(p['T']);rr=values['R_T'];qq=values['Q_DIVIDENDOS'];sig=values['SIGMA_GARCH_T']
    pagos=[]
    for z in np.random.default_rng(int(p.semilla_mc)).standard_normal(int(p.n_mc)//2):
        plus=S*math.exp((rr-qq-sig*sig/2)*T+sig*math.sqrt(T)*z)
        minus=S*math.exp((rr-qq-sig*sig/2)*T-sig*math.sqrt(T)*z)
        pagos.append(math.exp(-rr*T)*(max(K-plus,0)+max(K-minus,0))/2)
    mean=math.fsum(pagos)/len(pagos);variance=math.fsum((x-mean)**2 for x in pagos)/(len(pagos)-1);se=math.sqrt(variance/len(pagos))
    assert abs(mean-values['MC_PUT'])<1e-11 and abs(se-values['MC_SE'])<1e-11
    assert abs(values['MC_PUT']-values['BS_PUT'])<4*values['MC_SE']
    checks=pd.read_csv(folder/'contraste_R.csv')
    checks['metodo']='R independiente desde lector escalar de los CSV'
    extra=pd.DataFrame([dict(metrica='MC_PUT',python=values['MC_PUT'],R=mean,diferencia=abs(mean-values['MC_PUT']),metodo='Bucle escalar Python, mismos pares y semilla'),dict(metrica='MC_SE',python=values['MC_SE'],R=se,diferencia=abs(se-values['MC_SE']),metodo='Varianza muestral escalar de promedios antitéticos')])
    pd.concat([checks,extra],ignore_index=True).to_csv(folder/'comparacion_35.csv',index=False)
    return dict(caso=folder.name,estado='PASS',segundos=elapsed,metricas=35,indicadores=11,max_diferencia_R=float(checks.diferencia.max()),mc_error_en_SE=abs(values['MC_PUT']-values['BS_PUT'])/values['MC_SE'],datos_originales_intactos=True)

def variante(base,dest,kind):
    dest.mkdir(parents=True,exist_ok=True)
    for n in INPUTS:shutil.copy2(base/(n+'.csv'),dest/(n+'.csv'))
    if kind=='filas':
        formats={'precios_SCL':(';',','),'tipo_cambio':(';',','),'salidas_de_bolsa':(';',',')}
        for n in INPUTS:
            sep,dec=formats.get(n,(',','.'));df=pd.read_csv(dest/(n+'.csv'),sep=sep,decimal=dec,comment='#')
            df.sample(frac=1,random_state=13).to_csv(dest/(n+'.csv'),index=False,sep=sep,decimal=dec,float_format='%.15g')
    else:
        p=pd.read_csv(dest/'parametros_D5.csv').iloc[0];cut=p.fecha_valoracion
        for n,sep,dec,dc,pc,fmt in [('precios_SCL',';',',','fecha','cierre','%d/%m/%Y'),('precios_NYC',',','.','date','close','%Y-%m-%d')]:
            df=pd.read_csv(dest/(n+'.csv'),sep=sep,decimal=dec);later=pd.to_datetime(df[dc],format=fmt)>pd.Timestamp(cut)
            df.loc[later,pc]*=50.;df.to_csv(dest/(n+'.csv'),index=False,sep=sep,decimal=dec,float_format='%.15g')

def main():
    script=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();out.mkdir(parents=True,exist_ok=True)
    contraste=Path(__file__).with_name('contraste_independiente.R')
    summary=[];known=[]
    for case in range(3):
        f=out/('mercado_'+str(case+1));known.append(generar(f,case));summary.append(validar(f,script,contraste));print(summary[-1],flush=True)
    base=out/'mercado_1'
    for kind,name in [('filas','mercado_1_desordenado'),('futuro','mercado_1_futuro_extremo')]:
        f=out/name;variante(base,f,kind);summary.append(validar(f,script,contraste));print(summary[-1],flush=True)
        for filename in ['resultados_D5.csv','calidad_tasas.csv']:
            a=pd.read_csv(base/filename);b=pd.read_csv(f/filename)
            assert a.iloc[:,0].tolist()==b.iloc[:,0].tolist()
            np.testing.assert_allclose(a.iloc[:,1],b.iloc[:,1],atol=2e-6,rtol=1e-10)
    pd.DataFrame(summary).to_csv(out/'resumen.csv',index=False)
    (out/'parametros_generadores.json').write_text(json.dumps(known,indent=2))
    (out/'manifiesto.json').write_text(json.dumps(dict(programa_sha256=hashlib.sha256(script.read_bytes()).hexdigest(),resultados=summary,limite='Pruebas sintéticas propias; no equivalen a los archivos ocultos del profesor.'),indent=2))
    print('PASS: cinco ejecuciones completas, 35 métricas y 11 indicadores por ejecución.',flush=True)

if __name__=='__main__':main()
