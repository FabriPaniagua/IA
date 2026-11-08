# Fase 11 — Preparación para actualización segura

## Resultado comprobable

- El endpoint `GET /estado-datos` informa la última fecha, días de antigüedad y el estado de simulación histórica.
- El script `src/validar_actualizacion.py` inspecciona archivos CSV nuevos sin sobrescribir la base ni reentrenar modelos.
- La base de 2016–2025, los 90 artefactos y los resultados de las fases anteriores permanecen intactos.

## Cómo usar

Desde la carpeta raíz:

```powershell
py -m pytest tests/test_estado_datos.py -q
py src/validar_actualizacion.py --csv ruta\datos_nuevos.csv
```

El CSV debe tener exactamente las mismas columnas y orden que la hoja `BASE_MAESTRA`, una fila diaria a partir del 01/01/2026, sin fechas repetidas ni huecos. Un informe se escribe en `results/auditoria_actualizacion.json`.

**Importante:** pasar este validador NO implica que el CSV sea fiable; se requiere verificar las fuentes oficiales y los horarios de observación. La imputación de niveles históricos y la corrección de Concepción de 2,58 m a 4,58 m deben permanecer documentadas como decisiones de procesamiento, no como mediciones confirmadas. No se deben rellenar automáticamente los datos nuevos con el último valor.

## Pendiente para pronóstico operativo

1. Recolectar y contrastar registros DMH (Concepción, Asunción, Villeta), ANA (Cáceres, Ladário, Porto Murtinho) y NASA POWER para las siete ubicaciones, desde 2026-01-01 hasta la fecha de emisión.
2. Verificar el retardo de publicación de cada fuente y mantener una fecha de corte común sin filtración de datos futuros.
3. Revisar faltantes, discrepancias, saltos de nivel, coordenadas, unidades, fechas y metadatos.
4. Crear una versión nueva del dataset, preservando la original y registrando procedencia y transformaciones.
5. Reentrenar y reevaluar los modelos con separación cronológica; recalibrar intervalos en datos independientes.
6. Habilitar pronóstico actual solo cuando existan datos recientes suficientes y controles de calidad.

**No utilizar esta aplicación para decisiones de navegación o seguridad.**
