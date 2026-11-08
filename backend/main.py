from pathlib import Path
import sys
from functools import lru_cache
from contextlib import asynccontextmanager
import asyncio, os, json, threading
from datetime import timedelta, date, datetime
from zoneinfo import ZoneInfo
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from features_base import make_features, PORTS

from actualizacion_automatica import update, AUDIT, PROVENANCE, STATIONS, NASA, VARS, MET_COLS, DATA as LIVE_DATA
UPDATE_LOCK=threading.Lock()

async def periodic_update():
    await asyncio.sleep(20)
    while True:
        try:
            if UPDATE_LOCK.acquire(blocking=False):
                try:
                    await asyncio.to_thread(update)
                    prepared.cache_clear()
                finally:UPDATE_LOCK.release()
        except Exception as exc:
            print('Actualización automática fallida:',repr(exc),flush=True)
        await asyncio.sleep(int(os.getenv('UPDATE_INTERVAL_SECONDS','21600')))

@asynccontextmanager
async def lifespan(app):
    task=asyncio.create_task(periodic_update())
    yield
    task.cancel()
    try:await task
    except asyncio.CancelledError:pass

app = FastAPI(lifespan=lifespan, title="Predicción del Río Paraguay", version="0.6.0", description="Sistema académico experimental con actualización automática DMH/NASA.")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_methods=["GET"], allow_headers=["*"])
DATA = ROOT / "data" / "BASE_MAESTRA_RIO_PARAGUAY_2016_2026_ACTUALIZADA.xlsx"

@lru_cache(maxsize=1)
def prepared():
    if not DATA.exists():
        raise FileNotFoundError("No se encontró el Excel de datos")
    d = pd.read_excel(DATA, sheet_name="BASE_MAESTRA")
    d["fecha"] = pd.to_datetime(d["fecha"])
    if not d["fecha"].is_unique or not d["fecha"].is_monotonic_increasing:
        raise ValueError("La base no tiene fechas únicas y ordenadas")
    return d, make_features(d)

@lru_cache(maxsize=100)
def model_for(port, horizon):
    file = ROOT / "models" / f"{port.lower()}_{horizon:02d}.joblib"
    if not file.exists():
        raise FileNotFoundError(f"Modelo no disponible: {port}, día {horizon}")
    return joblib.load(file)

def get_data():
    try:
        return prepared()
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(503, str(exc)) from exc

def parse_origin(value, d):
    if value is None:
        today=pd.Timestamp(datetime.now(ZoneInfo('America/Asuncion')).date())
        matches=d.index[d.fecha==today]
        return int(matches[0]) if len(matches) else len(d)-1
    try:
        date = pd.Timestamp(value)
        if date.strftime("%Y-%m-%d") != value:
            raise ValueError("formato")
    except (ValueError, TypeError):
        raise HTTPException(422, "Fecha inválida; usar YYYY-MM-DD")
    matches = d.index[d.fecha == date]
    if not len(matches):
        raise HTTPException(422, "Fecha fuera del período disponible")
    return int(matches[0])

@app.get("/health")
def health():
    return {"status": "ok", "dataset_disponible": DATA.exists(), "modelos_disponibles": len(list((ROOT/'models').glob('*.joblib')))}

@app.get("/puertos")
def ports():
    return [{"id": p, "nombre": {"Concepcion": "Concepción", "Asuncion": "Asunción", "Villeta": "Villeta"}[p]} for p in PORTS]

@app.get("/info")
def info():
    d, _ = get_data()
    return {"fecha_minima": d.fecha.min().strftime("%Y-%m-%d"), "fecha_maxima": d.fecha.max().strftime("%Y-%m-%d"), "total_dias": len(d), "horizonte_maximo": 30, "fuentes": ["NASA POWER", "DMH Paraguay"], "estado": "experimental_actualizacion_automatica", "advertencia": "Datos recientes pueden incluir imputaciones provisionales. No utilizar para navegación ni decisiones de seguridad."}

@app.get("/historico/{puerto}")
def history(puerto: str, fecha_origen: str | None = None, dias: int = Query(120, ge=1, le=3653)):
    if puerto not in PORTS:
        raise HTTPException(404, "Puerto no encontrado")
    d, _ = get_data()
    ix = parse_origin(fecha_origen, d)
    sub = d.iloc[max(0, ix-dias+1):ix+1]
    return {"puerto": puerto, "niveles": [{"fecha": row.fecha.strftime("%Y-%m-%d"), "nivel_m": round(float(getattr(row, PORTS[puerto])), 3)} for row in sub.itertuples(index=False)]}

@app.get("/metricas/{puerto}")
def metrics(puerto: str):
    if puerto not in PORTS:
        raise HTTPException(404, "Puerto no encontrado")
    path = ROOT/'results'/'metricas_diarias.csv'
    if not path.exists():
        raise HTTPException(503, "Métricas no disponibles")
    d = pd.read_csv(path)
    d = d[(d.puerto == puerto) & (d.modelo == 'Seleccion_validacion') & (d.horizonte.isin([15,30]))]
    return {"puerto": puerto, "evaluacion": "2024-2025", "metricas": d.where(pd.notna(d), None).to_dict('records')}

@app.get("/pronostico/{puerto}")
def forecast(puerto: str, fecha_origen: str | None = None, dias: int = Query(30, ge=1, le=30)):
    if puerto not in PORTS:
        raise HTTPException(404, "Puerto no encontrado")
    d, f = get_data()
    ix = parse_origin(fecha_origen, d)
    if f.loc[ix].isna().any():
        raise HTTPException(422, "Historial insuficiente: seleccionar una fecha posterior")
    origin = d.loc[ix, 'fecha']
    level = float(d.loc[ix, PORTS[puerto]])
    output = []
    for h in range(1, dias+1):
        try:
            artifact = model_for(puerto, h)
        except FileNotFoundError as exc:
            raise HTTPException(503, str(exc))
        features = f.loc[[ix], artifact['features']]
        if artifact['model'] is not None:
            change = float(artifact['model'].predict(features)[0])
        elif str(artifact.get('selected', '')).startswith('Tendencia_'):
            parts = artifact['selected'].split('_')
            window = int(parts[1].removesuffix('d'))
            damping = float(parts[2])
            if ix < window:
                raise HTTPException(422, 'Historial insuficiente para tendencia')
            change = float((d.loc[ix, PORTS[puerto]] - d.loc[ix-window, PORTS[puerto]]) / window * h * damping)
            change = max(-1.5, min(1.5, change))
        else:
            change = 0.0
        pred = level + change
        q = float(artifact['q90'])
        output.append({"fecha": (origin + timedelta(days=h)).strftime('%Y-%m-%d'), "dia": h, "nivel_estimado_m": round(pred,3), "limite_inferior90_m": round(pred-q,3), "limite_superior90_m": round(pred+q,3), "metodo": artifact['selected']})
    # Una fecha de origen historica no equivale a un backtest fuera de muestra
    # si el modelo cargado fue reentrenado posteriormente.
    cutoffs=[str(model_for(puerto,h).get('train_target_cutoff','')) for h in range(1,dias+1)]
    cutoffs=[x for x in cutoffs if x]
    training_cutoff=max(cutoffs) if cutoffs else None
    historical_leakage=(origin.strftime('%Y-%m-%d')<training_cutoff) if training_cutoff else None
    status = str(d.loc[ix].get('NASA_estado',''))
    provisional = status != 'COMPLETO' or any(str(d.loc[ix].get(k,'')) not in ('Observado','HISTORICO_ANA') for k in ['DMH_Concepcion_estado','DMH_Asuncion_estado','DMH_Villeta_estado','BR_Caceres_estado','BR_Ladario_estado','BR_Murtinho_estado'])
    return {"puerto": puerto, "fecha_origen": origin.strftime('%Y-%m-%d'), "nivel_origen_m": level, "fecha_maxima_datos": d.fecha.max().strftime('%Y-%m-%d'), "tipo": "experimental_provisional" if provisional else "experimental_datos_observados", "advertencia": "Pronóstico experimental; entradas imputadas por retrasos de publicación." if provisional else "Pronóstico experimental. Intervalos empíricos, sin garantía de cobertura del 90%.", "pronosticos": output, "fecha_generacion_local":datetime.now(ZoneInfo("America/Asuncion")).isoformat(), "fecha_ultima_nasa_real":_last_real_nasa(d,ix), "observaciones_que_faltan":_origin_gaps(d,ix), "fecha_corte_entrenamiento_modelo":training_cutoff,"evaluacion_historica_no_independiente":historical_leakage}


@app.get("/estado-datos")
def data_status():
    d,_=get_data()
    latest=d.iloc[-1]
    report={}
    if AUDIT.exists():
        try:report=json.loads(AUDIT.read_text(encoding='utf8').strip().splitlines()[-1])
        except Exception:pass
    return {"fecha_consulta":datetime.now(ZoneInfo("America/Asuncion")).date().isoformat(),"fecha_maxima_tabla":d.fecha.max().strftime('%Y-%m-%d'),"fecha_ultima_nasa_real":report.get('fecha_ultima_nasa_real'),"fechas_ultima_dmh_real":report.get('fechas_ultima_dmh_real',{}),"errores":report.get('errores',{}),"actualizacion_utc":report.get('ejecutado_utc'),"estado_nasa_ultima_fila":str(latest.get('NASA_estado','')),"modo":"experimental", "advertencia":"Los valores imputados NO son mediciones observadas."}



@app.get("/informe-datos")
def data_report(desde: str | None = None, hasta: str | None = None):
    """Transparent, per-station source coverage and gaps; no silent provisional-as-observed."""
    d,_=get_data()
    try:
        start=pd.Timestamp(desde) if desde else pd.Timestamp('2026-01-01')
        end=pd.Timestamp(hasta) if hasta else d.fecha.max()
        if start>end or (end-start).days>3660:raise ValueError('Rango inválido')
    except Exception:raise HTTPException(422,'Rango de fechas inválido')
    window=d[(d.fecha>=start)&(d.fecha<=end)].copy()
    try:prov=json.loads(PROVENANCE.read_text(encoding='utf8')) if PROVENANCE.exists() else {}
    except Exception:prov={}
    if not PROVENANCE.exists() and AUDIT.exists():
        for line in AUDIT.read_text(encoding='utf8').splitlines():
            try:r=json.loads(line)
            except Exception:continue
            for e in r.get('ajustes',[]):
                if e.get('accion')=='imputacion_provisional_arrastre':prov.setdefault(e['fecha'],{})[e['variable']]=e.get('fecha_observada')
    audit=[]
    if AUDIT.exists():
        for line in AUDIT.read_text(encoding='utf8').splitlines()[-30:]:
            try:r=json.loads(line);audit.append({'ejecutado_utc':r.get('ejecutado_utc'),'celdas_nuevas_observadas':r.get('celdas_nuevas_observadas'),'errores':r.get('errores',{}),'ajustes':len(r.get('ajustes',[]))})
            except Exception:continue
    sources=[];missing=[]
    for name,(_,col,status,mult) in STATIONS.items():
        observed=d[(d[col].notna()) & (d[status].isin(['Observado','HISTORICO_ANA']))]
        dates=[];observed_count=0;imputed_count=0
        for r in window.itertuples(index=False):
            ds=r.fecha.strftime('%Y-%m-%d');st=str(getattr(r,status));val=getattr(r,col)
            if st in ('Observado','HISTORICO_ANA') and pd.notna(val):observed_count+=1
            elif st in ('Imputado_ultimo_conocido','IMPUTADO_ARRASTRE','CORRECCION_MANUAL_NO_VERIFICADA'):
                imputed_count+=1;dates.append({'fecha':ds,'tipo':'corregido' if st=='CORRECCION_MANUAL_NO_VERIFICADA' else 'imputado','campo':col,'detalle':'Corrección manual estimada 4,45 a 2,45 m; NO verificada con fuente' if st=='CORRECCION_MANUAL_NO_VERIFICADA' else 'Arrastre documentado del último nivel conocido'})
            else:dates.append({'fecha':ds,'tipo':'faltante','campo':col,'detalle':'Sin medición publicada'})
        missing.extend({'fuente':'DMH','ubicacion':name,**x} for x in dates)
        sources.append({'id':'dmh_'+name,'fuente':'DMH','ubicacion':name,'variables':[col],'ultima_observacion':observed.fecha.max().strftime('%Y-%m-%d') if len(observed) else None,'observados':observed_count,'imputados':imputed_count,'faltantes':len(dates)-imputed_count,'total_dias':len(window),'codigo':STATIONS[name][0]})
    for name in NASA:
        cols=[f'{name}_{x}' for x in VARS.values()];counts={'observados':0,'imputados':0,'faltantes':0};last=None
        for r in d.itertuples(index=False):
            ds=r.fecha.strftime('%Y-%m-%d');all_real=all(pd.notna(getattr(r,c)) and c not in prov.get(ds,{}) for c in cols)
            if all_real:last=ds
        for r in window.itertuples(index=False):
            ds=r.fecha.strftime('%Y-%m-%d')
            for col in cols:
                val=getattr(r,col)
                if col in prov.get(ds,{}):
                    counts['imputados']+=1;missing.append({'fuente':'NASA POWER','ubicacion':name,'fecha':ds,'tipo':'imputado','campo':col,'detalle':'Provisional; último dato real: '+str(prov[ds][col])})
                elif pd.isna(val):
                    counts['faltantes']+=1;missing.append({'fuente':'NASA POWER','ubicacion':name,'fecha':ds,'tipo':'faltante','campo':col,'detalle':'No publicado'})
                else:counts['observados']+=1
        sources.append({'id':'nasa_'+name,'fuente':'NASA POWER','ubicacion':name,'variables':cols,'ultima_observacion':last,'total_dias':len(window),**counts,'codigo':None})
    return {'generado_local':datetime.now(ZoneInfo('America/Asuncion')).isoformat(),'desde':start.strftime('%Y-%m-%d'),'hasta':end.strftime('%Y-%m-%d'),'fecha_maxima_tabla':d.fecha.max().strftime('%Y-%m-%d'),'total_dias':len(window),'fuentes':sources,'incidencias':missing[-2500:],'incidencias_totales':len(missing),'auditoria':list(reversed(audit)),'advertencia':'Las fechas en la tabla no equivalen a observaciones publicadas. Imputaciones separadas por campo y fecha.'}


# Fase 14: PDF, evaluacion retrospectiva y procedencia.
from io import BytesIO
from fastapi.responses import StreamingResponse

def _last_real_nasa(d,ix):
    # El estado de una fila es un resumen; las celdas provisionales se verifican
    # por procedencia para no presentar un arrastre como medicion.
    try: provenance=json.loads(PROVENANCE.read_text(encoding='utf8')) if PROVENANCE.exists() else {}
    except Exception: provenance={}
    for j in range(ix,-1,-1):
        row=d.iloc[j]; day=row.fecha.strftime('%Y-%m-%d')
        if all(pd.notna(row[c]) and c not in provenance.get(day,{}) for c in MET_COLS):return day
    return None

def _origin_gaps(d,ix):
    row=d.iloc[ix]; gaps=[]; day=row.fecha.strftime('%Y-%m-%d')
    try: provenance=json.loads(PROVENANCE.read_text(encoding='utf8')) if PROVENANCE.exists() else {}
    except Exception: provenance={}
    for c in MET_COLS:
        if pd.isna(row[c]) or c in provenance.get(day,{}):gaps.append(c)
    for _,(_,c,status,_) in STATIONS.items():
        if pd.isna(row[c]) or str(row[status]) not in ('Observado','HISTORICO_ANA'):gaps.append(c)
    return gaps

@app.get('/evaluacion-retrospectiva/{puerto}')
def retrospective(puerto:str, fecha_origen:str, dias:int=Query(30,ge=1,le=30)):
    # Evalua solo fechas con observacion real, sin usar el futuro como predictor.
    fc=forecast(puerto,fecha_origen,dias)
    d,_=get_data();col=PORTS[puerto]
    status_col={'Asuncion':'DMH_Asuncion_estado','Concepcion':'DMH_Concepcion_estado','Villeta':'DMH_Villeta_estado'}[puerto]
    lookup=d.set_index('fecha');details=[]
    for p in fc['pronosticos']:
        dt=pd.Timestamp(p['fecha'])
        if dt not in lookup.index:continue
        r=lookup.loc[dt]
        if pd.isna(r[col]) or str(r[status_col])!='Observado':continue
        real=float(r[col]);pred=float(p['nivel_estimado_m']);low=float(p['limite_inferior90_m']);high=float(p['limite_superior90_m'])
        details.append({'dia':p['dia'],'fecha':p['fecha'],'observado_m':round(real,3),'pronosticado_m':pred,'error_m':round(pred-real,3),'error_absoluto_m':round(abs(pred-real),3),'dentro_intervalo90':low<=real<=high})
    n=len(details)
    return {'puerto':puerto,'fecha_origen':fecha_origen,'dias_solicitados':dias,'dias_evaluados':n,'mae_m':round(sum(x['error_absoluto_m'] for x in details)/n,3) if n else None,'rmse_m':round((sum(x['error_m']**2 for x in details)/n)**.5,3) if n else None,'cobertura_intervalo90':round(sum(x['dentro_intervalo90'] for x in details)/n,3) if n else None,'detalle':details,'advertencia':('NO ES BACKTEST INDEPENDIENTE: el modelo fue ajustado con datos posteriores al origen. ' if fc.get('evaluacion_historica_no_independiente') else '')+'Contraste descriptivo. Los intervalos no garantizan cobertura 90%.'}

@app.get('/reporte-pronostico/{puerto}',summary='Descargar reporte PDF de pronostico')
def pdf_forecast(puerto:str,fecha_origen:str|None=None,dias:int=Query(30,ge=1,le=30)):
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.units import cm
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.dates import DateFormatter,AutoDateLocator
    from matplotlib.ticker import MaxNLocator
    fc=forecast(puerto,fecha_origen,dias)
    hist=history(puerto,fc['fecha_origen'],120)
    try:back=retrospective(puerto,fc['fecha_origen'],dias)
    except Exception:back=None
    display={'Asuncion':'Asuncion','Concepcion':'Concepcion','Villeta':'Villeta'}[puerto]
    obs=hist['niveles'];pr=fc['pronosticos']
    hd=[datetime.strptime(x['fecha'],'%Y-%m-%d') for x in obs];hv=[x['nivel_m'] for x in obs]
    fd=[datetime.strptime(x['fecha'],'%Y-%m-%d') for x in pr];fv=[x['nivel_estimado_m'] for x in pr]
    lo=[x['limite_inferior90_m'] for x in pr];hi=[x['limite_superior90_m'] for x in pr]
    fig,ax=plt.subplots(figsize=(10,3.5));fig.patch.set_facecolor('white');ax.set_facecolor('#f8fbfd')
    ax.plot(hd,hv,color='#087e92',lw=2.5,label='Historico (incluye eventuales imputaciones)')
    ax.plot([hd[-1]]+fd,[hv[-1]]+fv,color='#d79515',lw=2.6,label='Pronostico')
    ax.fill_between(fd,lo,hi,color='#e3a42d',alpha=.18,label='Intervalo empirico 90%')
    ax.axvline(hd[-1],ls='--',lw=1,color='#8b9aaa');ax.grid(axis='y',color='#e1e8ee')
    ax.set_ylabel('Nivel relativo (m)');ax.xaxis.set_major_locator(AutoDateLocator(maxticks=9));ax.xaxis.set_major_formatter(DateFormatter('%d/%m'))
    ax.tick_params(axis='both',labelsize=8);ax.legend(loc='upper left',fontsize=7,frameon=False);fig.autofmt_xdate();fig.tight_layout()
    img=BytesIO();fig.savefig(img,format='png',dpi=145,bbox_inches='tight');plt.close(fig);img.seek(0)
    buffer=BytesIO();doc=SimpleDocTemplate(buffer,pagesize=(21*cm,29.7*cm),rightMargin=1.6*cm,leftMargin=1.6*cm,topMargin=1.4*cm,bottomMargin=1.3*cm)
    styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='TitleHydro',parent=styles['Title'],fontSize=19,leading=23,textColor=colors.HexColor('#12374b'),spaceAfter=9))
    styles.add(ParagraphStyle(name='SmallHydro',parent=styles['Normal'],fontSize=8.3,leading=12,spaceAfter=5))
    story=[Paragraph('HIDROPREDICT | REPORTE DE PRONOSTICO',styles['TitleHydro']),Paragraph(f'Puerto: <b>{display}</b> &nbsp; | &nbsp; Origen: <b>{fc["fecha_origen"]}</b> &nbsp; | &nbsp; Horizonte: <b>{dias} dias</b>',styles['Normal']),Spacer(1,8),Paragraph('Resumen del pronostico',styles['Heading2'])]
    summary=[['Nivel de origen','Nivel estimado al final','Fecha final'],[f'{fc["nivel_origen_m"]:.3f} m',f'{pr[-1]["nivel_estimado_m"]:.3f} m',pr[-1]['fecha']]]
    t=Table(summary,colWidths=[5.8*cm]*3);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e9f2f5')),('TEXTCOLOR',(0,0),(-1,0),colors.HexColor('#12374b')),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),9),('LINEBELOW',(0,-1),(-1,-1),.5,colors.HexColor('#cbd9e1'))]));story.append(t)
    story.extend([Spacer(1,10),Paragraph('Curva historica y proyeccion',styles['Heading2']),Image(img,width=17.4*cm,height=6.1*cm),Spacer(1,5),Paragraph('La linea azul representa el historico disponible; la ambar, el pronostico. El area sombreada corresponde a un intervalo empirico experimental, no garantizado.',styles['SmallHydro']),Paragraph('Fuentes y calidad de entrada',styles['Heading2']),Paragraph(f'<b>Fuente de niveles:</b> DMH Paraguay (y ANA en el historico brasileno). <b>Meteorologia:</b> NASA POWER UTC, siete ubicaciones y cuatro variables por ubicacion.',styles['SmallHydro']),Paragraph(f'<b>Ultimo dia con meteorologia completa no provisional:</b> {fc.get("fecha_ultima_nasa_real") or "No determinado"}. <b>Estado del pronostico:</b> {fc["tipo"]}. <b>Variables no observadas en la fecha de origen:</b> {len(fc.get("observaciones_que_faltan",[]))}.',styles['SmallHydro'])])
    if fc.get('observaciones_que_faltan'):story.append(Paragraph('Variables provisionales o faltantes: '+', '.join(fc['observaciones_que_faltan']),styles['SmallHydro']))
    story.append(Paragraph('Detalle diario de las 30 estimaciones',styles['Heading2']))
    rows=[['Dia','Fecha','Estimacion (m)','Inferior 90%','Superior 90%','Metodo']]
    rows += [[str(x['dia']),x['fecha'],f'{x["nivel_estimado_m"]:.3f}',f'{x["limite_inferior90_m"]:.3f}',f'{x["limite_superior90_m"]:.3f}',x['metodo']] for x in pr]
    tab=Table(rows,colWidths=[1.3*cm,3.3*cm,3.1*cm,3*cm,3*cm,3.7*cm],repeatRows=1,hAlign='LEFT')
    tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#12374b')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),7.7),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f1f6f8')]),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]));story.append(tab)
    if back and back['dias_evaluados']:
        story.extend([Spacer(1,8),Paragraph('Contraste retrospectivo con observaciones disponibles',styles['Heading2']),Paragraph(f'Dias observados evaluados: {back["dias_evaluados"]}/{dias}. MAE: {back["mae_m"]:.3f} m. RMSE: {back["rmse_m"]:.3f} m. Cobertura observada del intervalo: {back["cobertura_intervalo90"]*100:.1f}%.',styles['SmallHydro']),Paragraph('Este contraste es descriptivo y no demuestra por si solo validacion fuera de muestra.',styles['SmallHydro'])])
    if fc.get('evaluacion_historica_no_independiente') is None:
        story.append(Paragraph('<b>TRAZABILIDAD:</b> el archivo de modelo no declara fecha de corte del entrenamiento; la independencia de este contraste historico no puede certificarse desde el artefacto.',styles['SmallHydro']))
    if fc.get('evaluacion_historica_no_independiente'):
        story.append(Paragraph('<b>ADVERTENCIA DE FILTRACION TEMPORAL:</b> el modelo cargado se reajusto con objetivos hasta '+str(fc.get('fecha_corte_entrenamiento_modelo'))+'. Este pronostico historico no reproduce un modelo disponible en su fecha de origen. No debe interpretarse como validacion fuera de muestra.',styles['SmallHydro']))
    story.extend([Spacer(1,10),Paragraph('Metodologia y limitaciones',styles['Heading2']),Paragraph('Predicciones diarias mediante los modelos seleccionados por horizonte (Ridge, XGBoost, tendencia o persistencia), entrenados previamente. No hay reentrenamiento automatico al actualizar la base. Las predicciones se calculan a partir de las variables disponibles en la fecha de origen. Las fechas futuras NO son observaciones.',styles['SmallHydro']),Paragraph('Los intervalos al 90% son empiricos y pueden incluir valores negativos respecto al cero local de la escala. No constituyen probabilidades calibradas para todos los escenarios. No utilizar para navegacion, evacuacion ni decisiones de seguridad.',styles['SmallHydro']),Paragraph(f'Generado: {datetime.now(ZoneInfo("America/Asuncion")).strftime("%d/%m/%Y %H:%M")} (Paraguay). Fuentes: meteorologia.gov.py y power.larc.nasa.gov.',styles['SmallHydro'])])
    doc.build(story);buffer.seek(0)
    filename=f'hidropredict_{puerto.lower()}_{fc["fecha_origen"]}_{dias}d.pdf'
    return StreamingResponse(buffer,media_type='application/pdf',headers={'Content-Disposition':f'attachment; filename="{filename}"'})


@app.get('/comparacion-modelos')
def comparison_models():
    """Comparación retrospectiva 2026, selección exploratoria sin garantía futura."""
    path=ROOT/'results'/'comparacion_modelos_2026.csv'
    if not path.exists():raise HTTPException(503,'Resultados no disponibles')
    table=pd.read_csv(path)
    summaries=[]
    for port,rows in table.groupby('puerto'):
        summaries.append({'puerto':port,'MAE_fase14_m':round(float(rows.MAE_fase14_m.mean()),4),
                          'MAE_candidato_m':round(float(rows.MAE_nuevo_m.mean()),4),
                          'MAE_desplegado_m':round(float(rows.MAE_desplegado_2026_m.mean()),4),
                          'MAE_persistencia_m':round(float(rows.MAE_persistencia_m.mean()),4),
                          'modelo_desplegado':'Fase15 experimental' if port=='Concepcion' else 'Fase14 conservado'})
    return {'periodo':'2026-01-01 a 2026-10-31','evaluacion':'retrospectiva exploratoria',
            'advertencia':'Se revisó 2026 para decidir el despliegue: NO es una prueba independiente posterior a la selección. Las métricas no garantizan resultados futuros.',
            'resumen':summaries,'detalle':table.round(5).to_dict(orient='records')}


@app.get('/investigacion-fase16')
def investigacion_fase16():
    """Evaluacion congelada: entrenamiento hasta 2023, validacion 2024-25, prueba 2026.
    No altera los modelos operativos de la fase 15.
    """
    path=ROOT/'results'/'fase16_comparacion_con_fase15.csv'
    if not path.exists():raise HTTPException(503,'No disponible')
    t=pd.read_csv(path)
    summaries=[]
    for port,g in t.groupby('puerto'):
        summaries.append({'puerto':port,
          'mae_fase15_2026_m':round(float(g.MAE_desplegado_2026_m.mean()),4),
          'mae_ridge1000_2026_m':round(float(g.MAE_test_2026.mean()),4),
          'mae_persistencia_2026_m':round(float(g.MAE_persistencia_2026.mean()),4),
          'cobertura_ridge1000_2026':round(float(g.cobertura_2026.mean()),4),
          'horizontes_ganados_por_ridge1000':int((g.MAE_test_2026<g.MAE_desplegado_2026_m).sum())})
    return {'decision':'CONSERVAR_MODELOS_FASE15','motivo':'Ridge1000 no mejora el MAE agregado en ningun puerto',
      'entrenamiento':'objetivos hasta 2023-12-31','validacion':'2024-2025',
      'prueba':'2026-01-01 a 2026-10-31, origen y objetivo dentro del periodo',
      'advertencia':'Comparacion exploratoria: la fase15 se selecciono revisando 2026. No equivale a una prueba prospectiva independiente de la fase15.',
      'resumen':summaries}
