"""Entrena pronósticos directos a 15 y 30 días. Sin variables futuras."""
from pathlib import Path
import argparse, json
import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

PORTS={'Concepcion':'DMH_Concepcion_nivel_m','Asuncion':'DMH_Asuncion_nivel_m','Villeta':'DMH_Villeta_nivel_m'}
GAUGES=['ANA_Caceres_nivel_cm','ANA_Ladario_nivel_cm','ANA_Murtinho_nivel_cm',*PORTS.values()]

def make_features(df):
    d=df.copy().sort_values('fecha').reset_index(drop=True)
    dt=pd.to_datetime(d.fecha)
    f=pd.DataFrame(index=d.index)
    f['month_sin']=np.sin(2*np.pi*dt.dt.dayofyear/365.25)
    f['month_cos']=np.cos(2*np.pi*dt.dt.dayofyear/365.25)
    for c in GAUGES:
        for lag in [0,1,3,7,14,30,60,90]: f[f'{c}_lag{lag}']=d[c].shift(lag)
        for w in [7,14,30]:
            f[f'{c}_change{w}']=d[c]-d[c].shift(w)
    for c in [x for x in d.columns if x.endswith('_PREC_mm_dia')]:
        for w in [7,15,30,60]: f[f'{c}_sum{w}']=d[c].rolling(w,min_periods=w).sum()
    for c in [x for x in d.columns if x.endswith('_T2M_C')]:
        for w in [7,30]: f[f'{c}_mean{w}']=d[c].rolling(w,min_periods=w).mean()
    return f

def train(input_path,output):
    output=Path(output);(output/'models').mkdir(parents=True,exist_ok=True);(output/'results').mkdir(parents=True,exist_ok=True)
    d=pd.read_excel(input_path,sheet_name='BASE_MAESTRA')
    d['fecha']=pd.to_datetime(d.fecha)
    assert len(d)==3653 and d.fecha.is_unique and d.fecha.is_monotonic_increasing
    f=make_features(d)
    metrics=[]; predictions=[]
    for port,col in PORTS.items():
      for h in [15,30]:
        y=d[col].shift(-h)
        target_date=d.fecha.shift(-h)
        valid=f.notna().all(axis=1)&y.notna()
        train=valid&(target_date<='2022-12-31')
        validation=valid&(target_date>='2023-01-01')&(target_date<='2023-12-31')
        test=valid&(target_date>='2024-01-01')&(target_date<='2025-12-31')
        assert train.sum()>1000 and validation.sum()>300 and test.sum()>600
        model=XGBRegressor(n_estimators=350,max_depth=3,learning_rate=.035,subsample=.85,colsample_bytree=.85,objective='reg:squarederror',random_state=42,n_jobs=2)
        model.fit(f.loc[train],y.loc[train],verbose=False)
        cal=np.abs(y.loc[validation].to_numpy()-model.predict(f.loc[validation]))
        q90=float(np.quantile(cal,.90,method='higher'))
        pred=model.predict(f.loc[test]); true=y.loc[test].to_numpy(); base=d.loc[test,col].to_numpy()
        for name,values in [('XGBoost',pred),('Persistencia',base)]:
          metrics.append(dict(puerto=port,horizonte_dias=h,modelo=name,train_n=int(train.sum()),valid_n=int(validation.sum()),test_n=int(test.sum()),MAE_m=round(float(mean_absolute_error(true,values)),4),RMSE_m=round(float(np.sqrt(mean_squared_error(true,values))),4),R2=round(float(r2_score(true,values)),4),intervalo_90_cobertura=round(float(np.mean((true>=values-q90)&(true<=values+q90))),4) if name=='XGBoost' else None,semi_amplitud_intervalo_90_m=round(q90,4) if name=='XGBoost' else None))
        for idx,actual,p,b in zip(d.index[test],true,pred,base):
          predictions.append(dict(puerto=port,horizonte_dias=h,fecha_origen=d.loc[idx,'fecha'].strftime('%Y-%m-%d'),fecha_objetivo=target_date.loc[idx].strftime('%Y-%m-%d'),real_m=round(float(actual),4),predicho_m=round(float(p),4),persistencia_m=round(float(b),4),limite_inferior_90_m=round(float(p-q90),4),limite_superior_90_m=round(float(p+q90),4)))
        joblib.dump({'model':model,'features':f.columns.tolist(),'port':port,'horizon':h,'q90':q90},output/'models'/f'xgboost_{port.lower()}_{h}d.joblib')
    pd.DataFrame(metrics).to_csv(output/'results'/'metricas.csv',index=False)
    pd.DataFrame(predictions).to_csv(output/'results'/'predicciones_prueba.csv',index=False)
    (output/'results'/'configuracion.json').write_text(json.dumps({'entrenamiento':'objetivo hasta 2022-12-31','validacion':'objetivo 2023','prueba':'objetivo 2024-2025','horizontes':[15,30],'intervalo':'residuos absolutos en validación, cuantíl 90%; aproximación empírica sin garantía de cobertura futura','nota':'DMH incluye 66 valores imputados y 1 corrección hipotética; no se usaron precipitaciones futuras'},ensure_ascii=False,indent=2),encoding='utf8')
    print(pd.DataFrame(metrics).to_string(index=False))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--input',required=True);ap.add_argument('--output',default='.');a=ap.parse_args();train(a.input,a.output)
