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
