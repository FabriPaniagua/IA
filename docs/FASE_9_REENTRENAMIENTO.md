# Fase 9: reentrenamiento anual de Ridge

## Objetivo
Medir estabilidad temporal de Ridge y persistencia para 15 y 30 días en tres puertos.

## Procedimiento
En cada año de prueba (2022, 2023, 2024, 2025), entrenar un Ridge(alpha=300) sobre cambios de nivel, con datos de entrenamiento cuya fecha objetivo sea anterior al primer día del año de prueba. Evaluar orígenes y objetivos dentro del año, sin utilizar meteorología futura. Los predictores son los definidos en `src/features_base.py`. La persistencia repite el nivel del origen.

## Hallazgos
Ridge supera la persistencia en 20 de 24 escenarios. Pierde en Concepción en 2022 y 2024 a 15 y 30 días. En 2025 gana en los seis escenarios: Concepción 15d 0.262 vs 0.408 m, 30d 0.440 vs 0.705 m; Asunción 15d 0.355 vs 0.499 m, 30d 0.493 vs 0.779 m; Villeta 15d 0.344 vs 0.502 m, 30d 0.487 vs 0.787 m.

## Limitaciones
No se modifican los modelos operativos ni se recalibran intervalos. Los datos 2016–2025 incluyen imputaciones de niveles DMH y una corrección hipotética. Los resultados de horizontes solapados presentan dependencia temporal. Se requiere evaluar una regla de selección de modelos sin usar datos futuros y realizar análisis de eventos extremos. Las observaciones de 2026 no están incorporadas.
