# HidroPredict — Predicción del nivel del Río Paraguay

**Proyecto 4 — Inteligencia Artificial** · Marcelo Gómez y Fabricio Paniagua.

Prototipo académico que integra niveles hidrométricos de DMH (mediciones paraguayas vinculadas a ANNP y estaciones brasileñas), meteorología NASA POWER, modelos de series temporales, API FastAPI y una interfaz React. Pronósticos experimentales de 1 a 30 días para **Asunción, Concepción y Villeta**.

## Inicio rápido (Windows 11 / Docker Desktop)

1. Instalar Docker Desktop y comprobar que esté iniciado.
2. Clonar este repositorio y abrir su carpeta en VS Code.
3. Ejecutar en la raíz del repositorio:

```powershell
docker compose up -d --build
```

4. Abrir la **interfaz** en http://localhost:8080 y la **API** en http://localhost:8000/docs.
5. Consultar el estado de las fuentes en http://localhost:8000/estado-datos y el informe en http://localhost:8000/informe-datos.
6. Ver registros con `docker compose logs --tail=100 api`. Detener con `docker compose down` (**no** usar `-v` sin respaldo).

> El puerto 8000 no contiene una página web de inicio: es la API; su ruta `/` puede devolver `Not Found`.

## Componentes

- `backend/`: API REST y endpoints de pronóstico e informes.
- `src/`: ingeniería de variables, ingesta DMH/NASA y actualización automática.
- `web/`: React/Vite, servido con Nginx.
- `models/`: artefactos de modelos usados por la aplicación.
- `data/`: bases iniciales y archivos de auditoría (el proceso modifica datos localmente).
- `results/`, `docs/`: resultados y documentación histórica.
- `investigacion/`: experimentos de Fases 16 y 17 y resultados comparativos. **No son nuevos modelos desplegados**.

## Fuentes, calidad y límites

- Datos históricos 2016–2026; fechas reales y provisionales pueden diferir.
- Imputaciones por arrastre documentadas y corrección manual no verificada en Porto Murtinho (06/10/2026, 4,45 → 2,45 m).
- Los pronósticos e intervalos son **experimentales**; la cobertura nominal del 90 % no está garantizada y las crecidas rápidas pueden producir errores elevados.
- La actualización de observaciones no reentrena automáticamente los modelos.
- No usar resultados para decisiones operativas de navegación o seguridad.
- Los experimentos de Fase 17 no demostraron una mejora general para los tres puertos; se mantienen los modelos de referencia.

## Verificación

```powershell
docker compose ps
docker compose logs --tail=50 api
```

Las pruebas automatizadas existentes se encuentran en `tests/`. Ejecutarlas con Python y las dependencias del proyecto. El despliegue Docker de este paquete no se ha ejecutado en el entorno de preparación; verificarlo en la máquina de entrega.

## Git y trabajo en equipo

Usar commits con mensajes descriptivos y no subir contraseñas, tokens, archivos `.env` ni datos personales. El historial anterior del proyecto no se reconstruye artificialmente.

## Licencia

Ver `LICENSE` en el repositorio original del equipo.

## Fase 18 — Experimento retrospectivo (sin cambios operativos)

La investigación adicional con reentrenamiento en fechas de origen de 2026 se documenta en [`investigacion/INFORME_FASE18.md`](investigacion/INFORME_FASE18.md). Los resultados no se utilizan automáticamente en producción: la crecida de octubre sigue presentando errores elevados y la muestra experimental es limitada.

## Fase 19 — Documentación de limitaciones y mejoras futuras (sin cambio del modelo operativo)

Se incorpora el estudio de septiembre y octubre de 2026 en [`investigacion/INFORME_INVESTIGACION_SEPTIEMBRE_OCTUBRE.md`](investigacion/INFORME_INVESTIGACION_SEPTIEMBRE_OCTUBRE.md), con resultados auditables en `investigacion/septiembre_octubre_resultados/`.

**Hallazgo:** los modelos experimentales de Fase 18 presentan errores sustancialmente mayores al pronosticar la crecida rápida de octubre que al evaluar septiembre. Los resultados no constituyen una medición directa del endpoint operativo y no prueban causalidad por sí solos. La precipitación intensa observada después del origen del pronóstico es una explicación plausible de parte del error.

**Alcance académico actual:** el sistema utiliza observaciones hidrométricas y meteorológicas históricas. No se incorporan pronósticos meteorológicos futuros, que son probabilísticos y exigirían archivos de predicciones emitidas en fechas pasadas para evaluar sin fuga de información. La incorporación futura de precipitación pronosticada, lluvia de cuenca media, humedad del suelo y caudales de tributarios es una **hipótesis de mejora por validar**, no una mejora ya demostrada ni una garantía de mayor precisión. ENSO y operación de represas se mantienen como líneas de investigación, sin atribución causal comprobada para octubre.

**Calidad de datos:** el valor original 4,45 m de Porto Murtinho (06/10/2026) y la estimación usada 2,45 m deben mantenerse identificados por separado; la corrección manual continúa sin verificación independiente.

**Versionado:** esta fase es exclusivamente documental y de investigación. No cambia código de la API, interfaz, modelos entrenados ni la lógica de pronóstico. No debe presentarse como incremento de precisión en producción.

**Próximos trabajos:** validación de múltiples fechas/años y regímenes, corroboración de correcciones, integración retrospectivamente válida de pronósticos meteorológicos y medición de cobertura de intervalos.
