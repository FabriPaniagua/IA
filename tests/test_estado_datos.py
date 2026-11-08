from fastapi.testclient import TestClient
from backend.main import app

def test_estado_datos():
    r = TestClient(app).get("/estado-datos")
    assert r.status_code == 200
    d = r.json()
    assert d["fecha_ultima_observacion"] == "2025-12-31"
    assert d["pronostico_operativo_habilitado"] is False
    assert d["modo"] == "simulacion_historica"
    assert d["antiguedad_dias"] >= 0
