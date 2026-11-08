from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def test_comparacion_pareada():
    df=pd.read_csv(ROOT/'results/comparacion_pareada_modelos.csv')
    assert len(df)==18
    assert (df.n>700).all()
    assert set(df.modelo)=={'Ridge/seleccion','XGBoost','Persistencia'}
def test_cobertura_anual():
    df=pd.read_csv(ROOT/'results/cobertura_por_anio.csv')
    assert len(df)==12
    assert df.cobertura90.between(0,1).all()
def test_regimenes():
    df=pd.read_csv(ROOT/'results/errores_por_regimen.csv')
    assert set(df.regimen)=={'crecida >=25 cm','bajante <=-25 cm','cambio <25 cm'}
