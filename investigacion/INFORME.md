# HidroPredict — Fase 17: experimento hidrológico

## Alcance y método
Se evaluaron 3 puertos × 8 horizontes (1, 3, 7, 10, 15, 20, 25 y 30 días) con dos familias de variables y modelos de persistencia, Ridge (α=100, 1000, 10000), y HistGradientBoosting (horizontes 7, 15 y 30). Se emplearon niveles de estaciones aguas arriba, velocidades, aceleraciones, rezagos adicionales, diferencias entre escalas convertidas a metros y precipitaciones acumuladas (3–90 días). Solo se utilizan variables disponibles hasta la fecha de origen.

Entrenamiento: objetivos hasta 31/12/2023. Selección: MAE en orígenes 2024–2025 con objetivos hasta 31/12/2025. Prueba retrospectiva: orígenes de 2026 con objetivos hasta 31/10/2026. **La selección de candidatos no consultó 2026**, pero esta fase de investigación sí usa 2026 para juzgar su rendimiento; posteriores decisiones de despliegue requieren evaluación prospectiva.

## Resultado MAE 2026, media de ocho horizontes

| Puerto | Referencia Fase 15 (mismos horizontes, métricas archivadas) | Candidato seleccionado con validación 2024–2025 |
|---|---:|---:|
| Concepción | 0,1866 m | **0,1779 m** |
| Asunción | **0,3524 m** | 0,3582 m |
| Villeta | **0,3562 m** | 0,3599 m |

**Advertencia de comparabilidad:** las métricas archivadas de Fase 15 pueden proceder de modelos reajustados o seleccionados usando 2026; no son un benchmark prospectivo limpio. Estos promedios cubren solo ocho horizontes, no los treinta.

A 30 días, el candidato hidrológico seleccionado arroja MAE 2026 de 0,2953 m en Concepción, 0,6407 m en Asunción y 0,6589 m en Villeta. La cobertura de intervalos empíricos al 90% queda por debajo de 90% en la mayoría de combinaciones, lo que impide declarar una recalibración satisfactoria.

## Decisión
**No reemplazar automáticamente los modelos operativos de Fase 16.** Hay una señal de mejora en Concepción, pero no una mejora general en los tres puertos. El proyecto Fase 16 se mantiene intacto como respaldo. Los experimentos son reproducibles desde `experimento_hidrologico.py` si la ruta `P` se adapta al directorio de instalación.

## Límites
- Los modelos no disponen de pronósticos de lluvia futura. NASA POWER es meteorología observada.
- No se midieron episodios hidrológicos independientes por separado en esta corrida; la crecida de octubre es un caso crítico para continuar.
- Las bandas se basan en cuantiles absolutos de validación, no son intervalos probabilísticos garantizados.
- No se completó backtesting de origen móvil con reentrenamiento en cada origen, ni la compilación Docker en esta fase.
- La comparación con Fase 15 no puede considerarse prueba de superioridad causal o prospectiva.

## Archivos
- `experimento_hidrologico.py`: código reproducible.
- `fase17_resultados.csv`: métricas de todos los candidatos.
- `fase17_seleccion_validacion.csv`: candidatos elegidos sin mirar 2026.
- `fase17_predicciones_auditables.csv`: pronósticos y resultados por fecha para auditoría.
- `fase17_log.txt`: registro de ejecución.
