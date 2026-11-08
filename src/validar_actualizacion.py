"""Auditoría de un CSV de nuevos datos; nunca modifica la base original."""
import argparse
import json
from pathlib import Path
import pandas as pd


def validar(nuevos, base):
    original = pd.read_excel(base, sheet_name="BASE_MAESTRA")
    entrada = pd.read_csv(nuevos)
    columnas = list(original.columns)
    errores, advertencias = [], []
    if list(entrada.columns) != columnas:
        faltan = sorted(set(columnas) - set(entrada.columns))
        sobran = sorted(set(entrada.columns) - set(columnas))
        errores.append(f"Esquema distinto: faltan={faltan}; sobran={sobran}; comprobar también el orden de columnas")
    if "fecha" not in entrada:
        errores.append("Falta columna fecha")
        return {"aprobado": False, "errores": errores, "advertencias": advertencias}
    fechas = pd.to_datetime(entrada.fecha, errors="coerce")
    if fechas.isna().any(): errores.append("Hay fechas inválidas")
    if fechas.duplicated().any(): errores.append("Hay fechas duplicadas")
    if not fechas.is_monotonic_increasing: errores.append("Fechas desordenadas")
    if len(fechas) and fechas.notna().all():
        ultimo = pd.to_datetime(original.fecha).max()
        if fechas.min() <= ultimo: errores.append(f"Los datos nuevos se superponen con la base (última fecha: {ultimo.date()})")
        if fechas.min() > ultimo + pd.Timedelta(days=1): errores.append("Hay días sin cubrir entre la base y la actualización")
        if len(fechas) > 1 and not fechas.diff().iloc[1:].eq(pd.Timedelta(days=1)).all(): errores.append("La actualización tiene saltos de fechas")
    if not set(columnas).difference(entrada.columns):
        cols = [c for c in columnas if c != "fecha"]
        numeric = entrada[cols].apply(pd.to_numeric, errors="coerce")
        if numeric.isna().any().any(): errores.append("Existen valores faltantes o no numéricos")
        if (numeric == -999).any().any(): errores.append("Se encontró el valor centinela -999")
        rain = [c for c in cols if c.endswith("_PREC_mm_dia")]
        if rain and (numeric[rain] < 0).any().any(): errores.append("Precipitación negativa")
        for c in [c for c in cols if c.endswith("_T2M_C")]:
            prefix = c[:-len("_T2M_C")]
            mn, mx = prefix + "_T2M_MIN_C", prefix + "_T2M_MAX_C"
            if mn in numeric and mx in numeric and ((numeric[mn] > numeric[c]) | (numeric[c] > numeric[mx])).any():
                errores.append(f"Temperaturas mínima/media/máxima inconsistentes en {prefix}")
    advertencias.append("Una validación estructural no acredita procedencia, horarios, calibración de escalas ni calidad hidrológica")
    advertencias.append("No imputar automáticamente observaciones nuevas ni tratar datos futuros como disponibles")
    return {"aprobado": not errores, "filas": len(entrada), "errores": errores, "advertencias": advertencias}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--base", default="data/BASE_MAESTRA_RIO_PARAGUAY_2016_2025_AJUSTADA.xlsx")
    ap.add_argument("--salida", default="results/auditoria_actualizacion.json")
    a = ap.parse_args()
    resultado = validar(a.csv, a.base)
    destino = Path(a.salida)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    raise SystemExit(0 if resultado["aprobado"] else 1)
