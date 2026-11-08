"""Evaluación expanding-window: reentrena al iniciar cada año, sin conocer objetivos futuros."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error,mean_squared_error
from features_base import make_features,PORTS

def run(input_path, output_dir):
    out=Path(output_dir); (out/'results').mkdir(parents=True,exist_ok=True)
    d=pd.read_excel(input_path,sheet_name='BASE_MAESTRA')
    d['fecha']=pd.to_datetime(d['fecha'])
    assert d.fecha.is_unique and d.fecha.is_monotonic_increasing
    x=make_features(d).astype(float)
    usable=x.notna().all(axis=1)
    rows=[]; examples=[]
    for year in (2022,2023,2024,2025):
      cutoff=pd.Timestamp(year-1,12,31)
      for port,col in PORTS.items():
       for h in (15,30):
        y=d[col].shift(-h)-d[col]
        target=d.fecha.shift(-h)
        # Solo entrenar con resultados cuya fecha objetivo ya había ocurrido al corte.
        train=usable & y.notna() & (target<=cutoff)
        # Evaluar pronósticos con fecha de origen dentro del año y objetivo también dentro del año.
        test=usable & y.notna() & (d.fecha>=pd.Timestamp(year,1,1)) & (target<=pd.Timestamp(year,12,31))
        model=make_pipeline(StandardScaler(),Ridge(alpha=300.0))
        model.fit(x.loc[train],y.loc[train])
        actual=(d.loc[test,col]+y.loc[test]).to_numpy()
        baseline=d.loc[test,col].to_numpy()
        forecast=baseline+model.predict(x.loc[test])
        for method,pred in [('Ridge_delta',forecast),('Persistencia',baseline)]:
         rows.append({'anio_prueba':year,'puerto':port,'horizonte_dias':h,'modelo':method,'entrenamiento_hasta':cutoff.date().isoformat(),'n_entrenamiento':int(train.sum()),'n_prueba':int(test.sum()),'MAE_m':float(mean_absolute_error(actual,pred)),'RMSE_m':float(np.sqrt(mean_squared_error(actual,pred))),'sesgo_m':float(np.mean(pred-actual))})
        for idx,a,p,b in zip(d.index[test],actual,forecast,baseline):
         examples.append({'anio_prueba':year,'puerto':port,'horizonte_dias':h,'fecha_origen':d.loc[idx,'fecha'].date().isoformat(),'fecha_objetivo':target.loc[idx].date().isoformat(),'real_m':float(a),'ridge_m':float(p),'persistencia_m':float(b)})
    df=pd.DataFrame(rows)
    df.to_csv(out/'results'/'reentrenamiento_anual_metricas.csv',index=False,float_format='%.5f')
    pd.DataFrame(examples).to_csv(out/'results'/'reentrenamiento_anual_predicciones.csv',index=False,float_format='%.5f')
    pivot=df.pivot_table(index=['anio_prueba','puerto','horizonte_dias'],columns='modelo',values='MAE_m').reset_index()
    pivot['mejora_ridge_pct']=100*(pivot['Persistencia']-pivot['Ridge_delta'])/pivot['Persistencia']
    pivot.to_csv(out/'results'/'reentrenamiento_anual_comparacion.csv',index=False,float_format='%.3f')
    print(pivot.to_string(index=False,float_format=lambda v:f'{v:.3f}'))
    print('Ridge gana',int((pivot['mejora_ridge_pct']>0).sum()),'de',len(pivot),'comparaciones')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',default='data/BASE_MAESTRA_RIO_PARAGUAY_2016_2025_AJUSTADA.xlsx');p.add_argument('--output',default='.');a=p.parse_args();run(a.input,a.output)
