"""Valida observaciones nuevas sin modificar el histórico ni inventar mediciones.
CSV esperado: fecha,DMH_Concepcion_nivel_m,DMH_Asuncion_nivel_m,DMH_Villeta_nivel_m,
ANA_Caceres_nivel_cm,ANA_Ladario_nivel_cm,ANA_Murtinho_nivel_cm y variables NASA.
"""
import argparse
from pathlib import Path
import pandas as pd

def run(csv_path,root):
    root=Path(root)
    historical=pd.read_excel(root/'data'/'BASE_MAESTRA_RIO_PARAGUAY_2016_2025_AJUSTADA.xlsx',sheet_name='BASE_MAESTRA',nrows=2)
    expected=list(historical.columns)
    incoming=pd.read_csv(csv_path)
    if set(incoming.columns)!=set(expected):
        missing=sorted(set(expected)-set(incoming.columns)); extra=sorted(set(incoming.columns)-set(expected))
        raise ValueError(f'Columnas faltantes: {missing}; adicionales: {extra}')
    incoming=incoming[expected]
    dates=pd.to_datetime(incoming.fecha,format='%Y-%m-%d',errors='raise')
    if dates.isna().any() or dates.duplicated().any() or not dates.is_monotonic_increasing:
        raise ValueError('Fechas inválidas, repetidas o desordenadas')
    if dates.min()<=pd.Timestamp('2025-12-31'):
        raise ValueError('Las fechas nuevas deben ser posteriores a 2025-12-31')
    if (dates.diff().dropna()!=pd.Timedelta(days=1)).any() or dates.min()!=pd.Timestamp('2026-01-01'):
        raise ValueError('La actualización debe comenzar 2026-01-01 y no tener huecos')
    if incoming.isna().any().any():
        raise ValueError('Hay campos vacíos: documentar y tratar antes de importar')
    numeric=[c for c in expected if c!='fecha']
    for c in numeric:
        incoming[c]=pd.to_numeric(incoming[c],errors='raise')
    if not incoming[numeric].apply(lambda s: s.map(lambda x: bool(pd.notna(x) and abs(x)<1e8))).all().all():
        raise ValueError('Valores no finitos o extremos')
    output=root/'data'/'actualizacion_validada.csv'
    incoming.to_csv(output,index=False)
    print(f'Validación satisfactoria: {len(incoming)} filas. Guardado {output}. NO se ha reentrenado ni sustituido el histórico.')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--csv',required=True);p.add_argument('--root',default='.');a=p.parse_args();run(a.csv,a.root)
