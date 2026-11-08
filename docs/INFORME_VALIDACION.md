# Fase 5 — Auditoría reproducible de evaluación

Se conservan exactamente los modelos de la Fase 4. **No hubo reentrenamiento ni modificación de las predicciones**.

## Resultados en fechas objetivo de 2024–2025

| Puerto | Día | Modelo seleccionado | MAE modelo (m) | MAE persistencia (m) | Mejora MAE | Cobertura nominal 90% observada |
|---|---:|---|---:|---:|---:|---:|
| Concepcion | 15 | Ridge_delta | 0.242 | 0.269 | +10.0% | 95.2% |
| Concepcion | 30 | Ridge_delta | 0.419 | 0.455 | +7.9% | 94.8% |
| Asuncion | 15 | Ridge_delta | 0.378 | 0.444 | +14.9% | 84.1% |
| Asuncion | 30 | Ridge_delta | 0.594 | 0.695 | +14.4% | 94.1% |
| Villeta | 15 | Ridge_delta | 0.378 | 0.454 | +16.7% | 84.0% |
| Villeta | 30 | Ridge_delta | 0.616 | 0.720 | +14.5% | 93.2% |

## Verificaciones

- 6 combinaciones puerto/horizonte recalculadas a partir de `results/backtest_diario.csv`: todas coinciden con las métricas publicadas (tolerancia de redondeo).
- No se interpreta cobertura empírica como garantía estadística de un intervalo de confianza.
- Los pronósticos son **simulaciones históricas**, no predicciones actuales.
- Los datos DMH contienen 66 imputaciones por arrastre y una corrección hipotética, que pueden afectar los errores.
- No se ha realizado validación externa contra ANNP ni un análisis formal de episodios extremos.
- El algoritmo del prototipo es Ridge o persistencia, según selección por validación. No es XGBoost.
- El desempeño puede variar si se actualiza el conjunto de datos o se retrenan modelos.

## Limitaciones que deben resolverse antes de una entrega final

1. Validación temporal por múltiples ventanas (rolling-origin) y análisis separado de crecidas/bajantes.
2. Recalibración de bandas al 90% si la cobertura empírica resulta insuficiente.
3. Comparación formal con XGBoost bajo idéntica división y métricas.
4. Compilación React y prueba de Docker en el equipo de desarrollo.
5. Actualización de niveles posteriores a 2025 y comprobación de fuentes ANNP.
