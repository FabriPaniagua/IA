# Fase 12: actualización automática experimental

## Instalación
Abrir la carpeta principal en VS Code y ejecutar `docker compose up -d --build`. Dashboard: http://localhost:8080; API: http://localhost:8000/docs; auditoría: http://localhost:8000/estado-datos.

El servicio API intenta actualizar los datos unos 20 segundos después del inicio y después cada 6 horas (variable `UPDATE_INTERVAL_SECONDS`). Para iniciar inmediatamente sin esperar: `docker compose exec api python -m src.actualizacion_automatica`. **No hace falta ejecutarlo diariamente**. El equipo y Docker Desktop deben permanecer encendidos. Si el equipo está apagado, se actualizará tras el siguiente inicio de Docker.

## Fuentes
- DMH: historiales convencionales de seis estaciones; se consulta por paginación y se preservan los valores existentes (incluidas correcciones manuales). No se alteran valores previos cuando la fuente difiere; se registran diferencias.
- NASA POWER: API Daily/Point, AG, UTC, T2M, T2M_MAX, T2M_MIN, PRECTOTCORR; se rechaza -999.

## Retrasos de publicación
El sistema mantiene las fechas de observación. Para evitar interrumpir una demostración, permite **imputación provisional por arrastre** de nivel de hasta 2 días y meteorología de hasta 3 días. El pronóstico resultante es experimental y se etiqueta como provisional. No debe interpretarse como predicción operativa validada. Si faltan datos más antiguos o suficientes variables para crear características, el endpoint responde error y no inventa pronósticos. No se reemplazan correcciones históricas ni se introducen ceros ficticios.

Los modelos Ridge ya entrenados se mantienen SIN reentrenamiento; sus métricas 2024-2025 no acreditan desempeño con 2026. Los intervalos de 90 % son empíricos, no garantías. El sistema no se debe usar para navegación.

## Persistencia y auditoría
La carpeta `data` se monta en Docker: los cambios al Excel persisten en Windows. `data/auditoria_actualizaciones.jsonl` almacena las consultas, errores y ajustes. El Excel conserva hojas originales y añade `ACTUALIZACIONES` (última ejecución). Mantener copias del Excel antes de las pruebas. Los cambios del Excel se escriben en archivo temporal y se reemplaza el original solo al terminar la exportación.

## Limitaciones
No se ha probado conectividad a DMH/NASA desde el Docker del usuario. La extracción HTML de DMH puede romperse si cambia el sitio. Los modelos necesitan 90 días de historial y las mismas variables que en entrenamiento. Para la defensa, guardar una copia offline de la versión estable. El dashboard utiliza la fecha del equipo; mantener hora y zona horaria correctas.
