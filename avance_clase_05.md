# Clase 5 — Desafío 5

Pedí a Codex resolver el Bloque 2 de la foto y después completar el Desafío 5 con las diapositivas de la clase. Ambos pedidos se registran como resúmenes.

Codex reutilizó el lector del D4 para construir las cuotas con y sin dividendos. En `desafio5.py` dejó los cálculos para tasas en tres convenciones, ajuste NSS por grilla y MCO, volatilidades histórica, EWMA y GARCH, tres métodos de valoración de la put, griegas, collar, duración, convexidad y DV01 con flujos descontados por la curva.

Para el caso de sala se usaron 2.204 retornos de mi cartera, del 02-01-2014 al 30-06-2022. Para estimar q se anualizó la diferencia media de retornos logarítmicos con y sin dividendos de los últimos 250 días. Para la histórica se anualizó la desviación muestral de esa misma ventana. GARCH y EWMA se inicializaron con la varianza de los primeros 250 retornos sin dividendos, según la convención de mi D4. Con estos criterios, q = 0,0168, σ histórica = 0,1327, EWMA = 0,1278 y GARCH a 126 días en escala anual = 0,1454. GARCH acumulada a 126 días = 0,1028. Falta cotejar estas convenciones con el enunciado detallado del D5.

Codex verificó el ajuste NSS con tasas construidas desde parámetros conocidos, los límites de la curva y una conversión de tasas en tres convenciones. Para un caso sintético, obtuvo una put de 3,312680 por Black–Scholes, 3,312997 por CRR y 3,314519 por Monte Carlo, con error estándar de 0,006447. Comprobó cotas, paridad, griegas por diferencias finitas, casos límite y el collar. Contrastó duración y convexidad con un bono cero cupón, y el GARCH con un cálculo iterativo de las 126 varianzas futuras. Agregar una observación extrema posterior al corte dejó las métricas idénticas.

Las diapositivas describen la entrega, pero no traen el esquema de los CSV nuevos ni el contrato exacto de salidas. Faltan `tasas_mercado.csv`, `bonos_fondo.csv`, `parametros_D5.csv`, el enunciado detallado y `probar_mi_entrega5.R`. La página del curso pidió iniciar sesión al volver a abrirla. Quedan pendientes la ejecución oficial, el memo con cifras, el cotejo de las ocho referencias candidatas en Crossref y el foro, sus PDF locales y el video personal.

## Entrega en sala del Bloque 2

Pedí preparar el correo y el código Python para la entrega en sala. Codex reunió el lector D4 y el cálculo de volatilidades en un único adjunto local. Lo ejecutó desde la carpeta de datos sin acceso a los módulos del repositorio y confirmó los 2.204 retornos y las cuatro cifras. El borrador dejó el RUT pendiente e indicó ambas escalas de GARCH. Se verificó que el adjunto dentro del borrador coincide byte por byte con el archivo probado.

## Contrato oficial recibido el 19-11-2026

Codex completó desafio5.py con los tres CSV oficiales y el enunciado. La salida contiene las 35 métricas y los 11 indicadores. q usa ahora el logaritmo de uno más la suma de los dividendos de los últimos 252 días, según la regla B. El programa integra el lector D4 y se ejecuta autónomamente en la carpeta de datos. Se verificaron propiedades de opciones, bonos y conteos, más ejemplos calculables de q, conversiones y un cero cupón. Falta ejecutar el archivo R público completo, contrastar otros mercados y completar memo, referencias registradas con PDF y video.

## Auditoría integral del 19-11-2026

Codex ejecutó la prueba pública completa: todos los controles OK, con 17 segundos registrados. Contrastó las métricas deterministas y los conteos con R y verificó Monte Carlo estadísticamente; corrió casos alternativos y la prueba del lector D4. Preparó notebook ejecutado, memo de dos páginas, respaldo de cada aparición numérica, referencias con PDF y Crossref, guion de video, guía de defensa e informe estricto. El q y las demás cifras oficiales del contrato sustituyen los criterios preliminares del avance de sala, conservado arriba como registro histórico.

El análisis del memo utiliza el backtest propio D4 cortado a la valoración y no el período posterior. Falta consultar disponibilidad actual y registrar personalmente las referencias, y grabar/publicar el video con rostro y voz propios. No se da por enviado el trabajo ni se garantiza puntaje máximo o aprobación de datos ocultos. AGENTS.md conserva el prompt asistido solicitado y añade los procesos generales de revisión y trazabilidad.


## Referencias registradas en Webcursos

El 19-11-2026 pedí expresamente publicarlas mediante Chrome. Codex buscó cada DOI sin obtener mensajes previos y publicó las ocho referencias como temas separados. Verificó confirmaciones y autoría en mi cuenta. Enlaces en BITACORA_IA.md. El pendiente de foro de la auditoría anterior quedó resuelto; el video personal sigue pendiente. No se envió la tarea.


## Prueba integral sintética adicional

Se completó la comprobación antes pendiente: cinco ejecuciones integrales del mismo desafio5.py con diez CSV sintéticos por escenario. Tres mercados, una permutación de filas y una alteración exclusiva del futuro. Todos pasaron el contrato y el contraste independiente de cifras; no se cambió el ejecutable ni la cartera de entrega. Detalle reproducible y límites en el informe del respaldo.


## Video y enlace completos

Se agregó video_D5.txt a la carpeta de entrega con el enlace facilitado. Metadatos Drive confirman MP4 y permiso de lectura por enlace. La grabación convertida dura menos del máximo exigido. Pendiente el envío efectivo de la tarea y la defensa.


## Estándares reutilizables documentados — 23-11-2026

A petición mía se incorporó a AGENTS.md el procedimiento completo de cierre aplicado al D5, conservando el prompt asistido original y separando las reglas generales de los requisitos particulares del desafío. Se documentaron evidencia integral, trazabilidad concreta, PDF y fuentes, registro autorizado, video real y permisos, carpeta oficial y respaldos, y confirmación de envío. No se modificó la entrega.
