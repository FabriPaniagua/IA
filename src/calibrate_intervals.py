"""Calibración conservadora: cuantíl 95% de errores absolutos de validación 2023.
No se utiliza ninguna observación de 2024-2025 para escoger el ancho.
Las coberturas 2024-2025 son evaluación ex post, no garantías estadísticas.
"""
from pathlib import Path
import json, sys, shutil
import numpy as np
import pandas as pd
import joblib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from features_base import make_features,PORTS
from sklearn.metrics import mean_absolute_error
ROOT=Path(__file__).resolve().parents[1]

def calibrate():
 d=pd.read_excel(ROOT/'data'/'BASE_MAESTRA_RIO_PARAGUAY_2016_2025_AJUSTADA.xlsx',sheet_name='BASE_MAESTRA')
 d['fecha']=pd.to_datetime(d.fecha)
 f=make_features(d).astype(float)
 valid=f.notna().all(axis=1)
 report=[]; predictions=[]
 for port,col in PORTS.items():
  for h in range(1,31):
   path=ROOT/'models'/f'{port.lower()}_{h:02d}.joblib'
   a=joblib.load(path)
   target=d[col].shift(-h); target_date=d.fecha.shift(-h)
   val=valid & target.notna() & target_date.between('2023-01-01','2023-12-31')
   test=valid & target.notna() & target_date.between('2024-01-01','2025-12-31')
   assert val.sum()>300 and test.sum()>600
   def predict(mask):
    origin=d.loc[mask,col].to_numpy()
    return origin+a['model'].predict(f.loc[mask,a['features']]) if a['model'] is not None else origin
   pval=predict(val); tval=target.loc[val].to_numpy(); ptest=predict(test); ttest=target.loc[test].to_numpy()
   old=float(a['q90'])
   # Wider, conservative sensitivity setting, chosen a priori based on validation only.
   new=max(old,float(np.quantile(np.abs(tval-pval),.95,method='higher')))
   a['q90_original']=old
   a['q90']=new
   a['calibration_method']='validacion_2023_abs_error_q95_conservador; banda rotulada 90 nominal, sin garantia'
   joblib.dump(a,path)
   report.append(dict(puerto=port,horizonte=h,modelo=a['selected'],n_valid=int(val.sum()),n_test=int(test.sum()),q90_original_m=round(old,4),q95_validacion_m=round(new,4),cobertura_original_test=round(float(np.mean(np.abs(ttest-ptest)<=old)),4),cobertura_nueva_test=round(float(np.mean(np.abs(ttest-ptest)<=new)),4),MAE_test_m=round(float(mean_absolute_error(ttest,ptest)),4)))
   for ix,actual,p in zip(d.index[test],ttest,ptest):
    predictions.append(dict(puerto=port,horizonte=h,fecha_origen=d.loc[ix,'fecha'].strftime('%Y-%m-%d'),fecha_objetivo=target_date.loc[ix].strftime('%Y-%m-%d'),real_m=float(actual),predicho_m=float(p),limite_inferior90_m=float(p-new),limite_superior90_m=float(p+new)))
 results=ROOT/'results'
 pd.DataFrame(report).to_csv(results/'calibracion_validacion_2023.csv',index=False)
 pd.DataFrame(predictions).to_csv(results/'backtest_diario_recalibrado.csv',index=False)
 # Preserve original test metrics for traceability, but update the operational metrics file.
 metrics=results/'metricas_diarias.csv'; original=results/'metricas_diarias_precalibracion.csv'
 if not original.exists(): shutil.copy2(metrics,original)
 m=pd.read_csv(metrics); r=pd.DataFrame(report)
 for x in report:
  sel=(m.puerto==x['puerto'])&(m.horizonte==x['horizonte'])&(m.modelo=='Seleccion_validacion')
  m.loc[sel,'cobertura90']=x['cobertura_nueva_test'];m.loc[sel,'semi_amplitud90_m']=x['q95_validacion_m']
 m.to_csv(metrics,index=False)
 print(r[r.horizonte.isin([15,30])].to_string(index=False))
 return r
if __name__=='__main__':calibrate()
