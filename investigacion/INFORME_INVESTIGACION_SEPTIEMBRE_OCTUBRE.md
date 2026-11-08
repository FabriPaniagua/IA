# HidroPredict — Auditoría hidrológica y contraste septiembre/octubre 2026

## Fuentes y método
- Base maestra entregada: `BASE_MAESTRA_RIO_PARAGUAY_2016_2026_ACTUALIZADA(2).xlsx` (2016-01-01 a 2026-11-07), hoja `BASE_MAESTRA` y `AJUSTES_2026`.
- Backtesting de origen móvil ejecutado nuevamente con el script de Fase 18 y fechas 2026-09-01 y 2026-10-01; horizontes 15 y 30 días; reentrenamiento con objetivos conocidos hasta cada fecha de origen. Comparación: persistencia, Ridge(alpha=1000), XGBoost regularizado. Las predicciones son **dos puntos por mes**, no trayectorias diarias completas.
- Contexto externo: DMH, FIUNA (medición de caudal 20/10), NOAA CPC (ENSO 08/10), prensa que reproduce boletines de DMH. Fuentes al final.

## Corrección Porto Murtinho, 6 de octubre
- Original DMH: **4,45 m**. Ajuste manual: **2,45 m**, explícitamente **no verificado**.
- 05/10: 2,32 m; 06/10 corregido: 2,45 m; 07/10: 2,60 m; 08/10: 2,72 m. El original implicaría **+2,13 m** y luego **−1,85 m** en 24 h, pese a que los días posteriores muestran un ascenso sostenido.
- En la base corregida, la variación del 06/10 es **+0,13 m**. El percentil 99 histórico del cambio absoluto diario en esa serie es ~**0,17 m**; el máximo de la serie corregida es ~**0,44 m**. El valor original sería extraordinariamente discordante.
- Lluvia NASA POWER de Porto Murtinho el 06/10: **3,63 mm**, y 10,68 mm el 05/10; por sí sola no acredita una subida y caída de casi 2 m en días consecutivos. Tampoco descarta una crecida local por aportes aguas arriba.
- **Conclusión:** el valor 4,45 es *muy sospechoso*, pero no se demuestra que sea un error tipográfico. Mantener original y valor usado en auditoría; buscar observación ANA/Marinha del 06/10, registro horario, boletín o fotografía de regla antes de clasificarlo como definitivamente falso. La descarga ANA disponible llega hasta junio 2026 y no corrobora octubre.

## Precipitación y crecida de octubre
- NASA POWER acumulado en Concepción: **6,7 mm** en los primeros 12 días de septiembre frente a **131,8 mm** en los primeros 12 días de octubre. En particular **79,69 mm el 05/10** en la celda NASA de Concepción. Estos datos son estimaciones meteorológicas de grilla, no pluviómetros locales.
- Acumulados de octubre completo: Concepción **193,2 mm**, Porto Murtinho **161,0 mm**, Asunción **92,1 mm**, Pantanal **72,0 mm**. Septiembre completo: Concepción **81,0 mm**, Porto Murtinho **103,6 mm**, Asunción **55,7 mm**, Pantanal **63,4 mm**.
- Asunción: **0,50 m (01/10)** a **2,76 m (31/10)**, aumento **2,26 m**. Villeta: **0,89 m** a **3,31 m**, aumento **2,42 m**. Concepción subió rápidamente al inicio de octubre y después retrocedió parcialmente; su diferencia entre extremos mensuales no refleja el pico intermedio.
- FIUNA documentó un caudal de **3.200 m³/s** en Asunción el 20/10 a nivel de **2,77 m**, atribuyendo el repunte a grandes lluvias en cuenca media. Esto corrobora la crecida de Asunción de manera independiente.
- En los datos NASA, la lluvia de Asunción y Villeta es exactamente igual todos los días, lo que sugiere celdas de grilla compartidas o series duplicadas. No tratarlas como dos señales meteorológicas independientes sin verificar coordenadas.

## ENSO, represas y mecanismos
- NOAA CPC informó el 08/10/2026 que El Niño estaba fortaleciéndose. Es un **factor climático de fondo**, no una prueba causal de que provocó una crecida concreta en Asunción ni una variable conocida con exactitud el 01/10.
- La lluvia de la **cuenca media y tributarios** parece una explicación inmediata más plausible para la crecida rápida que una onda originada exclusivamente en el Pantanal lejano; esta es una hipótesis compatible con FIUNA y con la evolución relativamente más moderada de Ladário.
- Las grandes represas del **río Paraná** (p. ej. Yacyretá) no deben incorporarse como causa directa de los niveles de Asunción/Concepción/Villeta sin estudiar ubicación, conectividad y remanso. La operación de embalses y los afluentes podrían importar en sectores específicos, pero **no hay datos de maniobras de compuertas ni evidencia de causalidad para octubre** en este análisis.
- Otros factores no modelados: humedad antecedente de suelos, caudales de tributarios, lluvia de alta resolución en cuenca media, condiciones de drenaje/remanso, y **pronósticos meteorológicos futuros** (no solo NASA POWER observado).

## Backtesting septiembre frente a octubre
Los resultados de `resultados/predicciones_origen_movil.csv` evalúan pronósticos emitidos el 01/09 y 01/10 para 15 y 30 días, reentrenados solo con información disponible al origen. Errores absolutos en metros:

| Puerto | Horizonte | Sep persist. | Sep Ridge | Sep XGB | Oct persist. | Oct Ridge | Oct XGB |
|---|---:|---:|---:|---:|---:|---:|---:|
| Concepción | 15 | 0,270 | 0,248 | **0,107** | 1,030 | **0,859** | 1,072 |
| Concepción | 30 | 0,370 | 0,162 | **0,067** | 0,510 | **0,147** | 0,434 |
| Asunción | 15 | **0,400** | 0,424 | 0,418 | 2,060 | 1,802 | **1,767** |
| Asunción | 30 | 0,380 | 0,291 | **0,269** | 2,260 | 1,692 | **1,343** |
| Villeta | 15 | 0,400 | 0,329 | **0,233** | 2,040 | **1,922** | 1,972 |
| Villeta | 30 | 0,370 | 0,174 | **0,144** | 2,420 | 1,983 | **1,684** |

**Interpretación:** en septiembre XGBoost obtuvo error ≤0,269 m en cinco de seis combinaciones, mientras que en octubre los errores de Asunción y Villeta a 15/30 días fueron mucho mayores. El pronóstico del 01/09 a 30 días apunta al **01/10**, por lo que no incluye la crecida posterior. Estas son 12 comparaciones de fechas/horizontes, **no un MAE mensual de todas las predicciones diarias**. Además, son modelos experimentales Fase 18, **no el endpoint operativo Fase 15/16**. No presentar estas cifras como precisión verificada de la API actual.

## Recomendaciones priorizadas
1. Mantener 4,45 original y 2,45 corregido como *estimación pendiente de corroboración*; no revertir ni afirmar error confirmado.
2. Incorporar precipitación observada de **cuenca media**, especialmente cuencas tributarias, y mapas/series espaciales; comprobar NASA vs estaciones DMH.
3. Para horizontes 15–30 días, incorporar **pronósticos de precipitación emitidos en cada fecha** (archivos históricos de pronósticos para backtesting), no precipitación realizada en el futuro.
4. Añadir alertas por lluvia extrema/ascenso rápido como **clasificador complementario** de riesgo, sin fingir que pronostica el nivel exacto a 30 días.
5. Repetir backtesting en múltiples fechas de septiembre y octubre y en años independientes, reportando MAE/RMSE, sesgo y cobertura por régimen.
6. No usar ENSO ni represas como variables causales sin series históricas con fecha de disponibilidad y evidencia de aporte predictivo.

## Fuentes externas
- DMH Asunción: https://www.meteorologia.gov.py/nivel-rio/vermas_convencional.php?code=2000086218
- FIUNA, medición 20/10/2026: https://www.ing.una.py/FIUNA3/?p=90288
- NOAA CPC, discusión ENSO 08/10/2026: https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso_advisory/ensodisc.shtml
- ABC Color, repunte de Asunción 13/10: https://www.abc.com.py/clima/2026/10/13/nivel-del-rio-paraguay-en-la-bahia-de-asuncion-aumento-mas-de-un-metro-en-15-dias/
- ABC Color, anomalías de precipitación 14/10: https://www.abc.com.py/clima/2026/10/14/meteorologia-revela-cantidad-de-lluvia-acumulada-y-anomalias-durante-octubre/
