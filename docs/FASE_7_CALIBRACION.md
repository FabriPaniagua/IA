# Fase 7: calibración conservadora de bandas

Se mantiene exactamente el predictor de la Fase 6. Para cada puerto y horizonte se obtiene el cuantil empírico 95% del error absoluto de los datos de validación 2023 y se utiliza el máximo entre este valor y el cuantil 90% original. La decisión de ensanchar se tomó antes de observar el desempeño recalibrado de 2024–2025.

**Importante:** las bandas siguen siendo aproximaciones empíricas y **no** tienen garantía formal de cobertura del 90%: los errores son autocorrelacionados, las distribuciones cambian y los cuantiles se basan en un único año. El rótulo de la API `limite_inferior90_m` se conserva por compatibilidad; se añade un campo explicativo.

La cobertura posterior en 2024–2025 se utiliza **solo** para informar, no para elegir parámetros. El mayor ancho reduce utilidad operativa. No se modifican las predicciones puntuales ni los MAE.

Archivos: `results/calibracion_validacion_2023.csv`, `results/backtest_diario_recalibrado.csv` y `results/metricas_diarias_precalibracion.csv`.

Reproducir: `py src/calibrate_intervals.py`. Atención: se debe ejecutar sobre los modelos originales de Fase 6; la segunda ejecución sobre modelos recalibrados conserva el ancho ya ampliado.
