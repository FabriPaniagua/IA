# Fase 19 — Conclusiones, límites y trabajo futuro

**Tipo de entrega:** documentación científica y trazabilidad de investigación; no actualización de modelos operativos.

## Conclusión de investigación

La evidencia retrospectiva sugiere que los modelos basados en datos históricos tienen mayor dificultad durante crecidas rápidas asociadas con lluvias intensas que ocurren después de la fecha de emisión. El estudio septiembre/octubre 2026 documenta los datos, la metodología y los resultados. La comparación se realizó con modelos experimentales, no con el servicio operativo de la API.

## Justificación de alcance

El desafío académico exige integrar variables exógenas como precipitación histórica en la cuenca alta, niveles históricos y temperatura, además de investigar modelos alternativos. **No se requiere asumir que se dispone de precipitación futura observada**. La precipitación prevista puede constituir una mejora posterior, pero requiere fuentes archivadas por fecha de emisión, incertidumbre y evaluación temporal rigurosa. No introducir lluvia futura observada en pruebas retrospectivas, porque produciría fuga de información.

## Factores candidatos para estudios posteriores

- Pronósticos meteorológicos archivados para precipitación en cuenca media y alta.
- Precipitación espacial en tributarios y humedad antecedente del suelo.
- Caudales tributarios y propagación de ondas de crecida.
- Índices ENSO como contexto estacional, solo si demuestran valor predictivo.
- Influencia hidráulica de embalses/remanso únicamente con evidencia geográfica y operacional.

Ninguno de estos factores se presenta como causa confirmada de la crecida ni como mejora de precisión ya demostrada.

## Correcciones de calidad

La medición original de Porto Murtinho del 06/10/2026 fue 4,45 m y la serie operativa utiliza una estimación manual de 2,45 m. No se ha verificado independientemente. Conservar ambos registros y la procedencia.

## Evidencia y alcance

- `investigacion/INFORME_FASE18.md`: backtesting de origen móvil.
- `investigacion/INFORME_INVESTIGACION_SEPTIEMBRE_OCTUBRE.md`: análisis y fuentes.
- `investigacion/septiembre_octubre_resultados/`: protocolo, métricas y predicciones experimentales.

**Resultado de la fase:** mejor documentación, no nueva versión predictiva ni cambio de precisión.
