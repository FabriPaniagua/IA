from fastapi.testclient import TestClient
from backend.main import app
client=TestClient(app)
def test_health():
    r=client.get('/health');assert r.status_code==200;assert r.json()['modelos_disponibles']==90
def test_info():
    r=client.get('/info');assert r.status_code==200;assert r.json()['total_dias']==3653
def test_forecast():
    r=client.get('/pronostico/Asuncion',params={'fecha_origen':'2025-11-01','dias':15});assert r.status_code==200,r.text
    j=r.json();assert len(j['pronosticos'])==15;assert j['tipo']=='simulacion_historica'
    for p in j['pronosticos']:assert p['limite_inferior90_m']<=p['nivel_estimado_m']<=p['limite_superior90_m']
def test_invalid():
    assert client.get('/pronostico/ninguno').status_code==404
    assert client.get('/pronostico/Villeta?dias=31').status_code==422
    assert client.get('/pronostico/Villeta?fecha_origen=2026-01-01').status_code==422
def test_history_and_metrics():
    assert len(client.get('/historico/Concepcion?dias=20&fecha_origen=2025-11-01').json()['niveles'])==20
    assert len(client.get('/metricas/Villeta').json()['metricas'])==2


def test_pronostico_fechas_consecutivas():
    from datetime import date, timedelta
    for puerto in ('Concepcion', 'Asuncion', 'Villeta'):
        r=client.get(f'/pronostico/{puerto}',params={'fecha_origen':'2025-10-01','dias':30})
        assert r.status_code == 200, r.text
        j=r.json()
        assert len(j['pronosticos']) == 30
        for i, item in enumerate(j['pronosticos'], start=1):
            assert item['dia']==i
            assert date.fromisoformat(item['fecha']) == date(2025,10,1)+timedelta(days=i)
            assert item['limite_inferior90_m'] <= item['nivel_estimado_m'] <= item['limite_superior90_m']

def test_api_limites_y_modo_historico():
    assert client.get('/pronostico/Asuncion?dias=0').status_code==422
    assert client.get('/pronostico/Asuncion?dias=31').status_code==422
    assert client.get('/pronostico/Asuncion?fecha_origen=2026-11-05').status_code==422
    r=client.get('/info')
    assert r.status_code==200
    assert r.json()['fecha_maxima']=='2025-12-31'

def test_tres_puertos_metricas():
    for puerto in ('Concepcion','Asuncion','Villeta'):
        r=client.get(f'/metricas/{puerto}')
        assert r.status_code==200
        assert {x['horizonte'] for x in r.json()['metricas']}=={15,30}
