# Implementación independiente en R base, sobre precios de cuota reconstruidos.
p <- read.csv("parametros_D5.csv")
v <- setNames(read.csv("resultados_D5.csv")$valor,read.csv("resultados_D5.csv")$metrica)
h <- read.csv("series_verificacion.csv")
h <- h[as.Date(h$fecha)>=as.Date(p$inicio) & as.Date(h$fecha)<=as.Date(p$fecha_valoracion),]
n <- nrow(h);w<-p$ventana
q <- log1p(sum(tail(h$total-h$precio,252)))
s0 <- var(head(h$precio,w)); ew<-ga<-s0
omega<-(1-p$garch_alfa-p$garch_beta)*s0
for(r in h$precio[-seq_len(w)]) {
 ew<-p$lambda*ew+(1-p$lambda)*r^2
 ga<-omega+p$garch_alfa*r^2+p$garch_beta*ga
}
future <- numeric(p$horizonte_dias);future[1]<-ga
if(length(future)>1) for(i in 2:length(future)) future[i]<-omega+(p$garch_alfa+p$garch_beta)*future[i-1]
sig <- sqrt(mean(future)*252)
rates <- read.csv("tasas_mercado.csv",comment.char="#")
rates<-rates[order(rates$version),];rates<-rates[!duplicated(rates$instrumento,fromLast=TRUE),];rates<-rates[rates$estado=="ok",]
m <- rates$plazo*ifelse(rates$unidad=="dias",1/365,ifelse(rates$unidad=="meses",1/12,1))
z <- ifelse(abs(rates$tasa)>1,rates$tasa/100,rates$tasa)
z <- ifelse(rates$convencion=="efectiva_anual",log1p(z),ifelse(rates$convencion=="nominal_semestral",2*log1p(z/2),z))
X <- function(m,a,b) {
 f<-(1-exp(-m/a))/(m/a);g<-(1-exp(-m/b))/(m/b)
 cbind(1,f,f-exp(-m/a),g-exp(-m/b))
}
err<-Inf
for(a in seq(.25,5,.25)) for(b in seq(5.5,20,.5)) {
 xx<-X(m,a,b); fit<-lm.fit(xx,z); e<-sum(fit$residuals^2)
 if(e<err) {err<-e;bet<-fit$coefficients;t1<-a;t2<-b}
}
curve<-function(t) drop(X(t,t1,t2)%*%bet)
r<-curve(p$T);S<-p$S0;K<-p$k_put*S;T<-p$T
bs<-function(sigma,k=K) {
 d1<-(log(S/k)+(r-q+sigma^2/2)*T)/(sigma*sqrt(T));d2<-d1-sigma*sqrt(T)
 c(put=k*exp(-r*T)*pnorm(-d2)-S*exp(-q*T)*pnorm(-d1),
 call=S*exp(-q*T)*pnorm(d1)-k*exp(-r*T)*pnorm(d2),
 delta=-exp(-q*T)*pnorm(-d1),gamma=exp(-q*T)*dnorm(d1)/(S*sigma*sqrt(T)),
 vega=S*exp(-q*T)*dnorm(d1)*sqrt(T)/100,prob=pnorm(-d2))
}
o<-bs(sig)
# Árbol con inducción hacia atrás para contrastar la esperanza terminal Python.
steps<-p$N_binomial;dt<-T/steps;u<-exp(sig*sqrt(dt));d<-1/u;prob<-(exp((r-q)*dt)-d)/(u-d)
pay<-pmax(K-S*u^(0:steps)*d^(steps:0),0)
for(j in steps:1) pay<-exp(-r*dt)*(prob*pay[-1]+(1-prob)*pay[-length(pay)])
B<-read.csv("bonos_fondo.csv");B$vencimiento<-as.Date(B$vencimiento);date<-as.Date(p$fecha_valoracion)
B<-B[B$vencimiento>date,];tt<-cf<-numeric()
for(i in seq_len(nrow(B))) {
 # Fechas del caso público: secuencia hacia atrás desde cada vencimiento.
 dates<-seq(B$vencimiento[i],date,by=paste0("-",12/B$frecuencia[i]," months"))
 dates<-dates[dates>date]
 tt<-c(tt,as.numeric(dates-date)/365)
 cf<-c(cf,rep(B$nominal_usd_mm[i]*B$cupon_anual_pct[i]/100/B$frecuencia[i],length(dates))+c(B$nominal_usd_mm[i],rep(0,length(dates)-1)))
}
val<-function(s) sum(cf*exp(-(curve(tt)+s)*tt))
base<-val(0);baja<-val(-1e-4);sube<-val(1e-4)
D<-(baja-sube)/(2*base*1e-4);C<-(baja+sube-2*base)/(base*1e-8);dy<-p$shock_pb/1e4
expected<-c(setNames(bet,c("NSS_B0","NSS_B1","NSS_B2","NSS_B3")),NSS_TAU1=t1,NSS_TAU2=t2,NSS_RMSE_PB=sqrt(err/length(z))*1e4,R_T=r,N_DIAS_HIST=n,Q_DIVIDENDOS=q,SIGMA_HIST=sd(tail(h$precio,w))*sqrt(252),SIGMA_EWMA=sqrt(252*ew),SIGMA_GARCH_T=sig,BS_PUT=unname(o["put"]),BS_CALL=unname(o["call"]),PARIDAD=0,BIN_PUT=pay,PUT_DELTA=unname(o["delta"]),PUT_GAMMA=unname(o["gamma"]),PUT_VEGA=unname(o["vega"]),PROB_EJERCICIO=unname(o["prob"]),BS_PUT_SIGMA_HIST=unname(bs(sd(tail(h$precio,w))*sqrt(252))["put"]),BS_PUT_SIGMA_EWMA=unname(bs(sqrt(252*ew))["put"]),PERDIDA_MAX_CUBIERTA=unname((S-K+o["put"]*exp(r*T))/S),COLLAR_K_CALL=uniroot(function(k) bs(sig,k)["call"]-o["put"],c(S,10*S),tol=1e-12)$root,N_BONOS_VIGENTES=nrow(B),VALOR_BONOS=base,DURACION_MOD=D,CONVEXIDAD=C,DV01=(baja-sube)/2,CAMBIO_SHOCK_REAL=val(dy)/base-1,CAMBIO_SHOCK_DURACION=-D*dy,CAMBIO_SHOCK_DUR_CONV=-D*dy+C*dy^2/2)
dif<-abs(v[names(expected)]-expected)
write.csv(data.frame(metrica=names(expected),python=v[names(expected)],R=expected,diferencia=dif),"contraste_R.csv",row.names=FALSE)
stopifnot(length(expected)==33,all(dif<1e-5))
# MC independiente con su propia secuencia y el mismo número de pagos.
set.seed(p$semilla_mc);zz<-rnorm(p$n_mc/2)
centre<-S*exp((r-q-sig^2/2)*T)
pair<-(pmax(K-centre*exp(sig*sqrt(T)*zz),0)+pmax(K-centre*exp(-sig*sqrt(T)*zz),0))/2
mc<-exp(-r*T)*mean(pair);se<-exp(-r*T)*sd(pair)/sqrt(length(pair))
stopifnot(abs(mc-o["put"])<4*se)
cat("33 métricas contrastadas en R. Diferencia máxima:",max(dif),"\nMC independiente dentro de cuatro errores estándar.\n")

# Recuento independiente de los once indicadores.
raw<-read.csv("tasas_mercado.csv",comment.char="#")
last<-raw[order(raw$version),];last<-last[!duplicated(last$instrumento,fromLast=TRUE),]
u<-last[last$estado=="ok",]
quality<-c(FILAS_TASAS=nrow(raw),FILAS_VERSION_ANTIGUA=nrow(raw)-nrow(last),FILAS_STALE=nrow(last)-nrow(u),TASAS_USADAS=nrow(u),TASAS_EN_PORCENTAJE=sum(abs(u$tasa)>1),PLAZOS_EN_DIAS=sum(u$unidad=="dias"),PLAZOS_EN_MESES=sum(u$unidad=="meses"),TASAS_CONTINUAS=sum(u$convencion=="continua"),TASAS_EFECTIVAS=sum(u$convencion=="efectiva_anual"),TASAS_NOMINAL_SEMESTRAL=sum(u$convencion=="nominal_semestral"),BONOS_VENCIDOS=sum(as.Date(read.csv("bonos_fondo.csv")$vencimiento)<=as.Date(p$fecha_valoracion)))
qq<-read.csv("calidad_tasas.csv");stopifnot(identical(names(quality),qq$indicador),all(quality==qq$valor))
write.csv(data.frame(indicador=names(quality),R=quality,python=qq$valor),"contraste_calidad_R.csv",row.names=FALSE)
cat("Once indicadores contrastados en R: idénticos.\n")
