# Fase 8 — Diagnóstico temporal por origen móvil

## Metodología
Se evalúan pronósticos ya generados en la Fase 7, con origen de predicción que avanza día a día. Los resultados se agrupan por **fecha objetivo** en años y trimestres de 2024–2025. **Esto NO es reentrenamiento rolling-window ni validación cruzada con reajuste de hiperparámetros**: los modelos permanecen congelados. Se evitan afirmaciones de que los resultados sean nuevos experimentos de entrenamiento.

Las bandas son las recalibradas con validación 2023; 2024–2025 se usa solo para evaluar. Cobertura = proporción de observaciones dentro del intervalo; no es porcentaje de acierto del valor puntual.

## Resultados anuales para horizontes de 15 y 30 días

| Puerto | Horizonte | Año | N | MAE (cm) | Cobertura 90% | Ancho medio (m) |
|---|---:|---:|---:|---:|---:|---:|
| Asuncion | 15 | 2024 | 366 | 37.6 | 94.0% | 1.80 |
| Asuncion | 15 | 2025 | 365 | 38.1 | 90.7% | 1.80 |
| Asuncion | 30 | 2024 | 366 | 67.1 | 97.3% | 3.88 |
| Asuncion | 30 | 2025 | 365 | 51.8 | 99.7% | 3.88 |
| Concepcion | 15 | 2024 | 366 | 22.4 | 100.0% | 2.45 |
| Concepcion | 15 | 2025 | 365 | 26.1 | 95.6% | 2.45 |
| Concepcion | 30 | 2024 | 366 | 38.9 | 100.0% | 5.13 |
| Concepcion | 30 | 2025 | 365 | 44.9 | 98.1% | 5.13 |
| Villeta | 15 | 2024 | 366 | 37.5 | 90.7% | 1.68 |
| Villeta | 15 | 2025 | 365 | 38.2 | 91.5% | 1.68 |
| Villeta | 30 | 2024 | 366 | 69.9 | 94.5% | 3.76 |
| Villeta | 30 | 2025 | 365 | 53.3 | 100.0% | 3.76 |

## Precauciones
- Los horizontes se superponen y sus errores no son independientes; no interpretar los tamaños muestrales como observaciones independientes.
- La cobertura por trimestre puede variar mucho y no garantiza cobertura futura.
- El modelo sigue limitado a simulación histórica hasta 2025.
- El siguiente experimento necesario es reentrenamiento expansivo con validación temporal y comparación de modelos en ventanas independientes.
- La imputación por arrastre y la corrección hipotética de Concepción deben auditarse también en los subconjuntos de evaluación.
