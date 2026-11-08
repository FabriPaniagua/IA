"""Modelos directos diarios 1-30, comparados contra persistencia. Sin fuga temporal."""
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error,mean_squared_error
from features_base import make_features,PORTS

def run(path,out):
 out=Path(out);(out/'models').mkdir(parents=True,exist_ok=True);(out/'results').mkdir(parents=True,exist_ok=True)
 d=pd.read_excel(path,sheet_name='BASE_MAESTRA');d['fecha']=pd.to_datetime(d.fecha)
 assert len(d)==3653 and d.fecha.is_unique and d.fecha.is_monotonic_increasing
 f=make_features(d).astype(float);valid=f.notna().all(axis=1)
 rows=[]; preds=[]
 for port,col in PORTS.items():
  for h in range(1,31):
   y=d[col].shift(-h)-d[col];td=d.fecha.shift(-h)
   train=valid & y.notna() & (td<='2022-12-31')
   val=valid & y.notna() & (td>='2023-01-01') & (td<='2023-12-31')
   test=valid & y.notna() & (td>='2024-01-01') & (td<='2025-12-31')
   model=make_pipeline(StandardScaler(),Ridge(alpha=300.0))
   model.fit(f.loc[train],y.loc[train]);origin=d[col]
   pv=origin.loc[val].to_numpy()+model.predict(f.loc[val]);tv=(origin.loc[val]+y.loc[val]).to_numpy()
   baseline_val=origin.loc[val].to_numpy();mv=mean_absolute_error(tv,pv);bv=mean_absolute_error(tv,baseline_val)
   # Choose by validation only, not by test.
   chosen='Ridge_delta' if mv < bv else 'Persistencia'
   q90=float(np.quantile(np.abs(tv-(pv if chosen=='Ridge_delta' else baseline_val)),.90,method='higher'))
   pt=origin.loc[test].to_numpy()+model.predict(f.loc[test]);bt=origin.loc[test].to_numpy();tt=(origin.loc[test]+y.loc[test]).to_numpy()
   selected=pt if chosen=='Ridge_delta' else bt
   for name,p in [('Ridge_delta',pt),('Persistencia',bt),('Seleccion_validacion',selected)]:
    rows.append({'puerto':port,'horizonte':h,'modelo':name,'elegido':chosen,'n_test':int(test.sum()),'MAE_m':round(mean_absolute_error(tt,p),5),'RMSE_m':round(np.sqrt(mean_squared_error(tt,p)),5),'cobertura90':round(float(np.mean(np.abs(tt-p)<=q90)),4) if name=='Seleccion_validacion' else None,'semi_amplitud90_m':round(q90,4) if name=='Seleccion_validacion' else None})
   for ix,actual,p in zip(d.index[test],tt,selected):
    preds.append({'puerto':port,'horizonte':h,'fecha_origen':d.loc[ix,'fecha'].strftime('%Y-%m-%d'),'fecha_objetivo':td.loc[ix].strftime('%Y-%m-%d'),'real_m':float(actual),'predicho_m':float(p),'limite_inferior90_m':float(p-q90),'limite_superior90_m':float(p+q90)})
   joblib.dump({'model':model if chosen=='Ridge_delta' else None,'features':f.columns.tolist(),'port':port,'horizon':h,'q90':q90,'selected':chosen,'level_column':col},out/'models'/f'{port.lower()}_{h:02d}.joblib')
 pd.DataFrame(rows).to_csv(out/'results'/'metricas_diarias.csv',index=False)
 pd.DataFrame(preds).to_csv(out/'results'/'backtest_diario.csv',index=False)
 print(pd.DataFrame(rows).query('horizonte in [15,30] and modelo=="Seleccion_validacion"').to_string(index=False))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',default='.');a=p.parse_args();run(a.input,a.output)
