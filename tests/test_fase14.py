from fastapi.testclient import TestClient
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.main import app

client=TestClient(app)

def test_informe_reconoce_arrastres_historicos():
    r=client.get('/informe-datos?desde=2026-03-16&hasta=2026-03-16')
    assert r.status_code==200
    imputados={x['ubicacion'] for x in r.json()['incidencias'] if x['tipo']=='imputado'}
    assert {'caceres','ladario','porto_murtinho'}<=imputados

def test_correccion_manual_identificada():
    r=client.get('/informe-datos?desde=2026-10-06&hasta=2026-10-06')
    assert r.status_code==200
    assert any(x['tipo']=='corregido' and x['ubicacion']=='porto_murtinho' for x in r.json()['incidencias'])

def test_evaluacion_retrospectiva():
    r=client.get('/evaluacion-retrospectiva/Asuncion?fecha_origen=2026-10-01&dias=30')
    assert r.status_code==200
    assert r.json()['dias_evaluados']==30
    assert r.json()['mae_m']>1

def test_pdf_valido():
    r=client.get('/reporte-pronostico/Asuncion?fecha_origen=2026-10-01&dias=30')
    assert r.status_code==200
    assert r.content.startswith(b'%PDF')
    assert r.headers['content-type']=='application/pdf'
