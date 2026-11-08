"""Incremental DMH/NASA updater with per-cell provenance, retry, and auditable gap handling."""
import json, os, re, tempfile, time, logging
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from pathlib import Path
import pandas as pd
import requests
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'/'BASE_MAESTRA_RIO_PARAGUAY_2016_2026_ACTUALIZADA.xlsx'
AUDIT=ROOT/'data'/'auditoria_actualizaciones.jsonl'
PROVENANCE=ROOT/'data'/'procedencia_nasa.json'
STATIONS={'caceres':('2000082003','ANA_Caceres_nivel_cm','BR_Caceres_estado',100),'ladario':('2000082001','ANA_Ladario_nivel_cm','BR_Ladario_estado',100),'porto_murtinho':('2000082002','ANA_Murtinho_nivel_cm','BR_Murtinho_estado',100),'concepcion':('2000086134','DMH_Concepcion_nivel_m','DMH_Concepcion_estado',1),'asuncion':('2000086218','DMH_Asuncion_nivel_m','DMH_Asuncion_estado',1),'villeta':('2000086211','DMH_Villeta_nivel_m','DMH_Villeta_estado',1)}
NASA={'pantanal':(-18,-56),'caceres':(-16.0644,-57.6879),'ladario':(-18.99656,-57.65336),'murtinho':(-21.698,-57.883),'concepcion':(-23.4064,-57.4344),'asuncion':(-25.2637,-57.5759),'villeta':(-25.5076,-57.5637)}
VARS={'T2M':'T2M_C','T2M_MAX':'T2M_MAX_C','T2M_MIN':'T2M_MIN_C','PRECTOTCORR':'PREC_mm_dia'}
MET_COLS=[f'{name}_{suffix}' for name in NASA for suffix in VARS.values()]
LOG=logging.getLogger(__name__)

def fetch_dmh(s,code,start,end):
    out={};errors=[];previous=None
    for page in range(1,75):
        try:
            r=s.get('https://www.meteorologia.gov.py/nivel-rio/vermas_convencional.php',params={'code':code,'page':page},timeout=(12,35));r.raise_for_status();rows=[]
            for tr in BeautifulSoup(r.text,'html.parser').select('tr'):
                td=tr.find_all(['td','th'])
                if len(td)<2:continue
                m=re.fullmatch(r'\s*(\d{2}-\d{2}-\d{4})\s*',td[0].get_text(' ',strip=True))
                if not m:continue
                day=datetime.strptime(m.group(1),'%d-%m-%Y').date();raw=td[1].get_text(' ',strip=True)
                n=re.fullmatch(r'\s*(-?\d+(?:[.,]\d+)?)\s*m?\s*',raw,re.I)
                rows.append((day,float(n.group(1).replace(',','.')) if n else None))
            if not rows:break
            earliest=min(x[0] for x in rows)
            if previous is not None and earliest>=previous:errors.append('paginacion_sin_avance');break
            previous=earliest
            for day,val in rows:
                if start<=day<=end and val is not None:
                    if day in out and out[day]!=val:errors.append(f'duplicado_conflictivo_{day}')
                    else:out[day]=val
            if earliest<start:break
            time.sleep(.10)
        except Exception as exc:errors.append(f'pagina_{page}: {type(exc).__name__}: {exc}');break
    return out,errors

def fetch_nasa(s,name,lat,lon,start,end):
    try:
        r=s.get('https://power.larc.nasa.gov/api/temporal/daily/point',params={'parameters':','.join(VARS),'community':'AG','longitude':lon,'latitude':lat,'start':start.strftime('%Y%m%d'),'end':end.strftime('%Y%m%d'),'format':'JSON','time-standard':'UTC'},timeout=(12,55));r.raise_for_status()
        obj=r.json();header=obj.get('header',{});assert header.get('time_standard')=='UTC','NASA no confirmó UTC'
        params=obj['properties']['parameter'];out={}
        for key,suffix in VARS.items():
            for day,v in params[key].items():
                if v is None or float(v)<=-900:continue
                out.setdefault(date(int(day[:4]),int(day[4:6]),int(day[6:])),{})[f'{name}_{suffix}']=float(v)
        return out,[]
    except Exception as exc:return {},[f'{type(exc).__name__}: {exc}']

def _atomic_json(path,obj):
    fd,tmp=tempfile.mkstemp(dir=path.parent,suffix='.json');os.close(fd)
    try:
        Path(tmp).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8');os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def load_provenance(d):
    if PROVENANCE.exists():
        try:return json.loads(PROVENANCE.read_text(encoding='utf8'))
        except Exception:pass
    # Reconstruct provisional cells from the original append-only audit.
    provisional={}
    if AUDIT.exists():
        for line in AUDIT.read_text(encoding='utf8').splitlines():
            try:r=json.loads(line)
            except Exception:continue
            for e in r.get('ajustes',[]):
                if e.get('accion')=='imputacion_provisional_arrastre':provisional.setdefault(e['fecha'],{})[e['variable']]=e.get('fecha_observada')
    # Any unknown cell on a flagged day is conservatively provisional.
    for ts,row in d.iterrows():
        day=ts.strftime('%Y-%m-%d')
        if str(row.get('NASA_estado',''))=='PROVISIONAL_IMPUTADO' and day not in provisional:
            provisional[day]={c:None for c in MET_COLS}
    return provisional

def update():
    if not DATA.exists():raise FileNotFoundError(DATA)
    AUDIT.parent.mkdir(parents=True,exist_ok=True)
    raw=pd.read_excel(DATA,sheet_name='BASE_MAESTRA');raw['fecha']=pd.to_datetime(raw.fecha).dt.normalize()
    d=raw.sort_values('fecha').drop_duplicates('fecha',keep='last').set_index('fecha')
    today=datetime.now(ZoneInfo('America/Asuncion')).date();d=d.loc[d.index<=pd.Timestamp(today)].copy();start=min((d.index.max()-pd.Timedelta(days=14)).date(),today);start=max(start,today-timedelta(days=90))
    d=d.reindex(pd.date_range(d.index.min(),max(d.index.max(),pd.Timestamp(today)),freq='D',name='fecha'))
    prov=load_provenance(d);errors={};events=[];new_obs=0
    s=requests.Session();s.headers['User-Agent']='Universidad - proyecto académico de hidrología/1.3'
    for name,(code,col,status,mult) in STATIONS.items():
        vals,errs=fetch_dmh(s,code,start,today);errors['DMH_'+name]=errs
        if errs:continue
        for day,v in vals.items():
            ts=pd.Timestamp(day);value=v*mult;old=d.at[ts,col];old_status=str(d.at[ts,status])
            if pd.notna(old) and old_status not in ('Imputado_ultimo_conocido','IMPUTADO_ARRASTRE','PENDIENTE_DMH','nan'):
                if abs(float(old)-value)>.011:events.append({'fecha':str(day),'fuente':'DMH','estacion':name,'accion':'diferencia_con_registro_existente','anterior':float(old),'nuevo_fuente':value})
                continue
            if pd.isna(old) or abs(float(old)-value)>.00001 or old_status!='Observado':new_obs+=1
            d.at[ts,col]=value;d.at[ts,status]='Observado'
    for name,(lat,lon) in NASA.items():
        vals,errs=fetch_nasa(s,name,lat,lon,start,today);errors['NASA_'+name]=errs
        if errs:continue
        for day,features in vals.items():
            ts=pd.Timestamp(day);ds=str(day)
            for col,v in features.items():
                old=d.at[ts,col];was_provisional=col in prov.get(ds,{})
                if pd.isna(old) or was_provisional:
                    if pd.isna(old) or abs(float(old)-v)>.000001 or was_provisional:new_obs+=1
                    d.at[ts,col]=v
                    if was_provisional:
                        events.append({'fecha':ds,'fuente':'NASA','variable':col,'accion':'provisional_reemplazado_por_observado','nuevo':v})
                        del prov[ds][col]
            if ds in prov and not prov[ds]:del prov[ds]
    # Fill only from the latest REAL observation, never from another provisional value.
    for ts in d.index[-10:]:
        ds=ts.strftime('%Y-%m-%d')
        for name,(_,col,status,_) in STATIONS.items():
            if pd.notna(d.at[ts,col]):continue
            previous=d.loc[d.index<ts,col].last_valid_index()
            if previous is not None and (ts-previous).days<=2:
                d.at[ts,col]=d.at[previous,col];d.at[ts,status]='Imputado_ultimo_conocido'
                events.append({'fecha':ds,'fuente':'DMH','estacion':name,'accion':'imputacion_arrastre','fecha_observada':str(previous.date())})
            else:d.at[ts,status]='PENDIENTE_DMH'
        for col in MET_COLS:
            if pd.notna(d.at[ts,col]):continue
            prev=None
            for earlier in reversed(d.index[d.index<ts][-7:]):
                ed=earlier.strftime('%Y-%m-%d')
                if pd.notna(d.at[earlier,col]) and col not in prov.get(ed,{}):prev=earlier;break
            if prev is not None and (ts-prev).days<=3:
                d.at[ts,col]=d.at[prev,col];prov.setdefault(ds,{})[col]=str(prev.date())
                events.append({'fecha':ds,'fuente':'NASA','variable':col,'accion':'imputacion_provisional_arrastre','fecha_observada':str(prev.date())})
    for ts in d.index:
        ds=ts.strftime('%Y-%m-%d')
        d.at[ts,'NASA_estado']='PROVISIONAL_IMPUTADO' if prov.get(ds) else ('COMPLETO' if d.loc[ts,MET_COLS].notna().all() else 'PENDIENTE_NASA')
    d['DMH_2026_fuente']=d['DMH_2026_fuente'].fillna('DMH')
    full=d.reset_index();full['fecha']=full.fecha.dt.strftime('%Y-%m-%d')
    fd,tmp=tempfile.mkstemp(suffix='.xlsx',dir=DATA.parent);os.close(fd)
    try:
        with pd.ExcelWriter(tmp,engine='openpyxl') as writer:
            full.to_excel(writer,sheet_name='BASE_MAESTRA',index=False)
            for sheet in ['METADATOS','AJUSTES_2026','COMPATIBILIDAD','CONTROL_CALIDAD']:
                try:pd.read_excel(DATA,sheet_name=sheet).to_excel(writer,sheet_name=sheet,index=False)
                except ValueError:pass
            pd.DataFrame(events or [{'accion':'sin_cambios'}]).to_excel(writer,sheet_name='ACTUALIZACIONES',index=False)
        os.replace(tmp,DATA)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
    _atomic_json(PROVENANCE,prov)
    def last_gauge(col,status):
        z=d[(d[col].notna())&(d[status]=='Observado')];return str(z.index.max().date()) if len(z) else None
    def last_nasa(name):
        cols=[f'{name}_{x}' for x in VARS.values()]
        for ts in reversed(d.index):
            if d.loc[ts,cols].notna().all() and not any(c in prov.get(str(ts.date()),{}) for c in cols):return str(ts.date())
        return None
    last={name:last_nasa(name) for name in NASA};valid=[v for v in last.values() if v]
    report={'ejecutado_utc':datetime.now(timezone.utc).isoformat(),'fecha_hoy':str(today),'fecha_ultima_nasa_real':min(valid) if len(valid)==len(NASA) else None,'fechas_ultima_nasa_real':last,'fechas_ultima_dmh_real':{name:last_gauge(col,status) for name,(_,col,status,_) in STATIONS.items()},'errores':errors,'celdas_nuevas_observadas':new_obs,'ajustes':events[-500:],'fecha_maxima_tabla':str(d.index.max().date()),'provisionales_nasa':sum(len(v) for v in prov.values())}
    with AUDIT.open('a',encoding='utf8') as f:f.write(json.dumps(report,ensure_ascii=False)+'\n')
    return report
if __name__=='__main__':print(json.dumps(update(),ensure_ascii=False,indent=2))
