"""Audita amplitud y cobertura observadas sin reajustar intervalos sobre test."""
import argparse
from pathlib import Path
import pandas as pd
import numpy as np

def run(root):
    root=Path(root)
    d=pd.read_csv(root/'results'/'backtest_diario_recalibrado.csv')
    print('Columnas disponibles:',list(d.columns))
    needed={'puerto','horizonte','real_m','limite_inferior90_m','limite_superior90_m'}
    if not needed.issubset(d.columns):
        raise ValueError('Formato inesperado del backtest recalibrado')
    d['dentro']=((d.real_m>=d.limite_inferior90_m)&(d.real_m<=d.limite_superior90_m)).astype(int)
    d['ancho_m']=d.limite_superior90_m-d.limite_inferior90_m
    report=d.groupby(['puerto','horizonte']).agg(cobertura=('dentro','mean'),ancho_promedio_m=('ancho_m','mean'),n=('dentro','size')).reset_index()
    report.to_csv(root/'results'/'auditoria_intervalos.csv',index=False)
    print(report[report.horizonte.isin([15,30])].to_string(index=False))
    print('Advertencia: no ajustar intervalos usando este conjunto de prueba.')
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');run(ap.parse_args().root)
