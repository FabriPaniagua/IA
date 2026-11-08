"""Evaluación anual sin elegir modelos usando resultados del año evaluado.
La selección de 2022 usa Ridge por defecto; años siguientes usan el MAE de años anteriores.
"""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd


def run(root):
    root=Path(root)
    src=root/'results'/'reentrenamiento_anual_predicciones.csv'
    if not src.exists():
        raise FileNotFoundError('Ejecutar primero src/retrain_annual.py')
    d=pd.read_csv(src)
    out=[]; selections=[]
    for (port,h),group in d.groupby(['puerto','horizonte_dias']):
        for year in sorted(group.anio_prueba.unique()):
            past=group[group.anio_prueba<year]
            current=group[group.anio_prueba==year].copy()
            if past.empty:
                choice='ridge_m' # arranque sin evidencia previa; no se optimiza sobre el test
            else:
                ridge_mae=np.abs(past.real_m-past.ridge_m).mean()
                persistence_mae=np.abs(past.real_m-past.persistencia_m).mean()
                choice='ridge_m' if ridge_mae<persistence_mae else 'persistencia_m'
            current['prediccion_hibrida_m']=current[choice]
            current['metodo_elegido']=choice.replace('_m','')
            current['MAE_hibrido_m']=np.abs(current.real_m-current.prediccion_hibrida_m)
            out.append(current)
            selections.append({'puerto':port,'horizonte_dias':h,'anio_prueba':year,'seleccion':choice,'n_prueba':len(current),'MAE_hibrido_m':current.MAE_hibrido_m.mean(),'MAE_ridge_m':np.abs(current.real_m-current.ridge_m).mean(),'MAE_persistencia_m':np.abs(current.real_m-current.persistencia_m).mean(),'RMSE_hibrido_m':np.sqrt(np.mean((current.real_m-current.prediccion_hibrida_m)**2))})
    pred=pd.concat(out,ignore_index=True)
    report=pd.DataFrame(selections).sort_values(['anio_prueba','puerto','horizonte_dias'])
    pred.to_csv(root/'results'/'hibrido_predicciones_anuales.csv',index=False)
    report.to_csv(root/'results'/'hibrido_metricas_anuales.csv',index=False)
    print(report.to_string(index=False,float_format=lambda v:f'{v:.3f}'))
    print('\nPromedios ponderados por predicción (m):')
    for c in ['ridge_m','persistencia_m','prediccion_hibrida_m']:
        print(c,round(float(np.abs(pred.real_m-pred[c]).mean()),4))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');run(ap.parse_args().root)
