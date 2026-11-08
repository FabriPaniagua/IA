# Fase 6 — Diagnóstico de modelos e intervalos

Se compararon Ridge/selección, XGBoost y persistencia sobre **las mismas fechas objetivo 2024–2025**, emparejadas por puerto, fecha de origen y fecha objetivo. No se han reentrenado modelos ni recalibrado bandas con los datos de prueba.

## Comparación pareada (MAE en metros)

|                    |   Persistencia |   Ridge/seleccion |   XGBoost |
|:-------------------|---------------:|------------------:|----------:|
| ('Asuncion', 15)   |          0.444 |             0.378 |     0.726 |
| ('Asuncion', 30)   |          0.695 |             0.594 |     1.03  |
| ('Concepcion', 15) |          0.269 |             0.242 |     0.392 |
| ('Concepcion', 30) |          0.455 |             0.419 |     0.562 |
| ('Villeta', 15)    |          0.454 |             0.378 |     0.584 |
| ('Villeta', 30)    |          0.72  |             0.616 |     0.872 |

## Cobertura de bandas nominales del 90% por año

| puerto     |   horizonte |   anio |   n |   cobertura90 |   MAE_m |   amplitud_media_m |
|:-----------|------------:|-------:|----:|--------------:|--------:|-------------------:|
| Asuncion   |          15 |   2024 | 366 |        0.847  |  0.3758 |             1.317  |
| Asuncion   |          15 |   2025 | 365 |        0.8356 |  0.3806 |             1.317  |
| Asuncion   |          30 |   2024 | 366 |        0.9044 |  0.6711 |             3.2464 |
| Asuncion   |          30 |   2025 | 365 |        0.9781 |  0.5177 |             3.2464 |
| Concepcion |          15 |   2024 | 366 |        0.9891 |  0.2239 |             1.5605 |
| Concepcion |          15 |   2025 | 365 |        0.9151 |  0.261  |             1.5605 |
| Concepcion |          30 |   2024 | 366 |        0.9617 |  0.3891 |             2.6748 |
| Concepcion |          30 |   2025 | 365 |        0.9342 |  0.449  |             2.6748 |
| Villeta    |          15 |   2024 | 366 |        0.8415 |  0.3745 |             1.2684 |
| Villeta    |          15 |   2025 | 365 |        0.8384 |  0.3824 |             1.2684 |
| Villeta    |          30 |   2024 | 366 |        0.8934 |  0.6985 |             3.1735 |
| Villeta    |          30 |   2025 | 365 |        0.9699 |  0.5328 |             3.1735 |

## Error por régimen (variación real respecto al nivel de origen)

| puerto     |   horizonte | modelo          | regimen          |   n |   MAE_m |
|:-----------|------------:|:----------------|:-----------------|----:|--------:|
| Asuncion   |          15 | Ridge/seleccion | bajante <=-25 cm | 304 |  0.4589 |
| Asuncion   |          15 | Ridge/seleccion | cambio <25 cm    | 238 |  0.2466 |
| Asuncion   |          15 | Ridge/seleccion | crecida >=25 cm  | 189 |  0.4142 |
| Asuncion   |          15 | XGBoost         | bajante <=-25 cm | 304 |  0.8066 |
| Asuncion   |          15 | XGBoost         | cambio <25 cm    | 238 |  0.7074 |
| Asuncion   |          15 | XGBoost         | crecida >=25 cm  | 189 |  0.6177 |
| Asuncion   |          15 | Persistencia    | bajante <=-25 cm | 304 |  0.481  |
| Asuncion   |          15 | Persistencia    | cambio <25 cm    | 238 |  0.1292 |
| Asuncion   |          15 | Persistencia    | crecida >=25 cm  | 189 |  0.7819 |
| Asuncion   |          30 | Ridge/seleccion | bajante <=-25 cm | 368 |  0.6676 |
| Asuncion   |          30 | Ridge/seleccion | cambio <25 cm    | 175 |  0.5103 |
| Asuncion   |          30 | Ridge/seleccion | crecida >=25 cm  | 188 |  0.5297 |
| Asuncion   |          30 | XGBoost         | bajante <=-25 cm | 368 |  1.237  |
| Asuncion   |          30 | XGBoost         | cambio <25 cm    | 175 |  0.9755 |
| Asuncion   |          30 | XGBoost         | crecida >=25 cm  | 188 |  0.6772 |
| Asuncion   |          30 | Persistencia    | bajante <=-25 cm | 368 |  0.6893 |
| Asuncion   |          30 | Persistencia    | cambio <25 cm    | 175 |  0.1154 |
| Asuncion   |          30 | Persistencia    | crecida >=25 cm  | 188 |  1.2441 |
| Concepcion |          15 | Ridge/seleccion | bajante <=-25 cm | 128 |  0.2474 |
| Concepcion |          15 | Ridge/seleccion | cambio <25 cm    | 491 |  0.1736 |
| Concepcion |          15 | Ridge/seleccion | crecida >=25 cm  | 112 |  0.5383 |
| Concepcion |          15 | XGBoost         | bajante <=-25 cm | 128 |  0.5488 |
| Concepcion |          15 | XGBoost         | cambio <25 cm    | 491 |  0.3175 |
| Concepcion |          15 | XGBoost         | crecida >=25 cm  | 112 |  0.5365 |
| Concepcion |          15 | Persistencia    | bajante <=-25 cm | 128 |  0.4727 |
| Concepcion |          15 | Persistencia    | cambio <25 cm    | 491 |  0.1074 |
| Concepcion |          15 | Persistencia    | crecida >=25 cm  | 112 |  0.7462 |
| Concepcion |          30 | Ridge/seleccion | bajante <=-25 cm | 261 |  0.3199 |
| Concepcion |          30 | Ridge/seleccion | cambio <25 cm    | 303 |  0.3769 |
| Concepcion |          30 | Ridge/seleccion | crecida >=25 cm  | 167 |  0.6504 |
| Concepcion |          30 | XGBoost         | bajante <=-25 cm | 261 |  0.4594 |
| Concepcion |          30 | XGBoost         | cambio <25 cm    | 303 |  0.5599 |
| Concepcion |          30 | XGBoost         | crecida >=25 cm  | 167 |  0.726  |
| Concepcion |          30 | Persistencia    | bajante <=-25 cm | 261 |  0.5421 |
| Concepcion |          30 | Persistencia    | cambio <25 cm    | 303 |  0.1297 |
| Concepcion |          30 | Persistencia    | crecida >=25 cm  | 167 |  0.9096 |
| Villeta    |          15 | Ridge/seleccion | bajante <=-25 cm | 305 |  0.4493 |
| Villeta    |          15 | Ridge/seleccion | cambio <25 cm    | 242 |  0.2528 |
| Villeta    |          15 | Ridge/seleccion | crecida >=25 cm  | 184 |  0.4262 |
| Villeta    |          15 | XGBoost         | bajante <=-25 cm | 305 |  0.5793 |
| Villeta    |          15 | XGBoost         | cambio <25 cm    | 242 |  0.5595 |
| Villeta    |          15 | XGBoost         | crecida >=25 cm  | 184 |  0.6234 |
| Villeta    |          15 | Persistencia    | bajante <=-25 cm | 305 |  0.4934 |
| Villeta    |          15 | Persistencia    | cambio <25 cm    | 242 |  0.1346 |
| Villeta    |          15 | Persistencia    | crecida >=25 cm  | 184 |  0.8104 |
| Villeta    |          30 | Ridge/seleccion | bajante <=-25 cm | 372 |  0.6942 |
| Villeta    |          30 | Ridge/seleccion | cambio <25 cm    | 171 |  0.5046 |
| Villeta    |          30 | Ridge/seleccion | crecida >=25 cm  | 188 |  0.5619 |
| Villeta    |          30 | XGBoost         | bajante <=-25 cm | 372 |  0.9058 |
| Villeta    |          30 | XGBoost         | cambio <25 cm    | 171 |  0.9502 |
| Villeta    |          30 | XGBoost         | crecida >=25 cm  | 188 |  0.7332 |
| Villeta    |          30 | Persistencia    | bajante <=-25 cm | 372 |  0.7146 |
| Villeta    |          30 | Persistencia    | cambio <25 cm    | 171 |  0.1146 |
| Villeta    |          30 | Persistencia    | crecida >=25 cm  | 188 |  1.281  |

## Precauciones metodológicas

- Los regímenes de crecida/bajante se definen **después** de observar el resultado, solo para diagnóstico, nunca como variable predictora.
- Los umbrales de 25 cm son exploratorios y no representan alertas oficiales.
- Los pronósticos diarios de orígenes consecutivos se solapan; las observaciones de error no son independientes.
- Las bandas se calibraron sobre 2023. La cobertura de 2024–2025 es una evaluación externa temporal; **no se ajustan los intervalos mirando ese resultado**.
- Las diferencias de rendimiento no constituyen una prueba estadística de superioridad. Se recomienda backtesting con ventanas temporales adicionales y análisis de incertidumbre.
- La base contiene 66 niveles imputados y una corrección hipotética. Se deben estudiar sensibilidad y métricas excluyendo objetivos imputados.
- Las predicciones no son operativas actuales: la última observación es del 31/12/2025.

## Próximos pasos

1. Recalibrar intervalos exclusivamente con validación temporal adicional (sin tocar prueba 2024–2025).
2. Implementar backtesting rolling-origin sin fuga temporal.
3. Analizar robustez ante episodios extremos e imputaciones.
4. Probar compilación real de React y Docker en Windows.