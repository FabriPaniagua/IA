# Fase 10 — Evaluación y preparación de despliegue

## Objetivo
Comparar una estrategia híbrida de selección retrospectiva Ridge/persistencia, auditar la amplitud de intervalos y crear una puerta de entrada para datos nuevos.

## Diseño experimental
Se reutilizan las predicciones del reentrenamiento anual de 2022 a 2025. Para cada puerto y horizonte de 15 o 30 días, el selector escoge el método que obtuvo menor MAE acumulado **antes del año evaluado**. El primer año se fija a Ridge. Se evita elegir sobre el año de prueba. La comparación no demuestra que el híbrido mejore el rendimiento futuro: es una evaluación retrospectiva.

## Resultados agregados
- Ridge: MAE 0,4488 m
- Persistencia: MAE 0,5571 m
- Híbrido: MAE 0,4653 m

Ridge supera al híbrido en el agregado de este experimento. No corresponde reemplazar el modelo desplegado por la estrategia híbrida sin más validación.

## Intervalos
La cobertura observada y el ancho medio se calculan a partir del archivo de predicciones de prueba recalibradas, sin ajustar parámetros sobre las pruebas. Los intervalos a 30 días son amplios (Concepción 5,13 m, Asunción 3,88 m, Villeta 3,76 m). Reducirlos requiere una nueva calibración con validación cronológica independiente. Una banda de 90 % no significa 90 % de aciertos exactos.

## Actualización
El validador de CSV permite inspeccionar datos nuevos con el esquema exacto de la base maestra, pero no implementa todavía descarga automática ni reentrenamiento. Sin datos verificados de 2026, la aplicación debe mantenerse etiquetada como simulación histórica. La ANNP sigue sin integrarse como fuente identificada.

## Comprobaciones
- Pruebas automatizadas Python: 11 aprobadas.
- Compilación frontend: no verificada (instalación npm agotó el tiempo disponible).
- Docker: no ejecutado (Docker Engine no disponible en el entorno de trabajo).
- La API existente sigue exponiendo los modelos diarios anteriores, no el selector híbrido anual.

## Riesgos
El arrastre de 66 niveles DMH y la corrección hipotética de Concepción 2018-02-08 deben mantenerse identificados. La información meteorológica NASA se expresa en días UTC y la hora de referencia DMH/ANA no está confirmada. No utilizar los pronósticos para decisiones de navegación.
