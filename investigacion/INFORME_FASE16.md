# FASE 16 — Auditoría científica y ensayos de recalibración

## Decisión operativa
**Se conservan los modelos de la Fase 15.** La nueva familia Ridge 1000 no mejoró la Fase 15 en MAE agregado. Sustituirlos sería injustificado.

## Ensayos realmente ejecutados
1. Entrenamiento de modelos hasta objetivos de 2023-12-31.
2. Validación con orígenes 2024-2025 y objetivos antes de 2026.
3. Prueba temporal con orígenes y objetivos de 2026 hasta 2026-10-31.
4. Primer barrido: persistencia, 9 tendencias amortiguadas, Ridge (100 y 1000), HistGradientBoosting, en horizontes 1, 7, 15, 30 para tres puertos.
5. Segundo barrido: Ridge 1000 en 90 combinaciones puerto-horizonte, comparado con las métricas guardadas de Fase 15 y persistencia.
6. Evaluación de cobertura empírica de intervalos de Ridge 1000 calibrados en 2024-2025.

## MAE promedio 2026 por 30 horizontes
| Puerto | Fase 15 (referencia) | Ridge 1000 (prueba) | Persistencia | Cobertura Ridge 1000 |
|---|---:|---:|---:|---:|
| Asuncion | 0.3995 | 0.4039 | 0.5324 | 82.2% |
| Concepcion | 0.2121 | 0.2193 | 0.2552 | 89.6% |
| Villeta | 0.4044 | 0.4103 | 0.5416 | 81.5% |

La comparación con Fase 15 se basa en sus métricas almacenadas; los modelos Fase 15 fueron elegidos tras consultar 2026. Por eso la comparación NO constituye una evaluación prospectiva independiente de Fase 15.

## Hallazgo metodológico importante
En Concepción, los modelos desplegados se reajustaron con objetivos hasta noviembre de 2026, de modo que el contraste con origen 01/10/2026 NO es independiente. En Asunción y Villeta los artefactos conservados no incluyen metadatos de corte del entrenamiento, por lo que la independencia no puede certificarse a partir del archivo. La Fase 16 ahora distingue ambas situaciones en la respuesta JSON y el PDF.

## Cambios funcionales
- Nuevo endpoint GET /investigacion-fase16 con métricas resumidas y decisión.
- Campos `fecha_corte_entrenamiento_modelo` y `evaluacion_historica_no_independiente` en /pronostico/{puerto}.
- Advertencia de filtración temporal en PDF para orígenes anteriores al corte del entrenamiento.
- Se mantienen actualizador DMH/NASA, dashboard, PDF y modelos de Fase 15.
- Los modelos Ridge 1000 entrenados en la investigación NO se despliegan; la carpeta experimental está separada.

## Limitaciones pendientes
- La cobertura nominal del 90% no está garantizada: Asunción y Villeta tuvieron ~82% con Ridge 1000.
- Los eventos rápidos de octubre continúan difíciles de anticipar.
- La selección de Fase 15 consultó el período 2026, por lo que no se puede declarar mejora prospectiva independiente.
- Para mejorar verdaderamente es necesario backtesting de origen móvil con entrenamiento truncado en cada origen, comparar episodios de crecida y bajante, y registrar pronósticos futuros sin alterarlos.

## Pruebas de ejecución
Desde FASE_10_SISTEMA_INTEGRADO: `docker compose up -d --build`.
Consultar `/health`, `/investigacion-fase16`, `/pronostico/Asuncion?fecha_origen=2026-10-01&dias=30` y el PDF.
Guardar antes una copia de `data/` y conservar los datos más recientes de la instalación previa. No usar `docker compose down -v`.

## Archivos de resultados
`results/fase16_experimentos.csv`, `results/fase16_metricas_90_horizontes.csv`, `results/fase16_comparacion_con_fase15.csv`.

**Uso académico experimental. No utilizar para navegación, alertas ni seguridad.**
