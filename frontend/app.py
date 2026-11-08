import os
import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
st.set_page_config(page_title='Río Paraguay — Pronósticos',layout='wide')
st.title('Pronóstico del río Paraguay')
st.caption('Sistema experimental basado en registros históricos 2016–2025. No representa una predicción actual sin actualizar los datos.')
api=st.sidebar.text_input('Dirección de API',os.getenv('API_URL','http://localhost:8000'))
port=st.sidebar.selectbox('Puerto',['Concepcion','Asuncion','Villeta'],format_func=lambda x:{'Concepcion':'Concepción','Asuncion':'Asunción','Villeta':'Villeta'}[x])
days=st.sidebar.slider('Horizonte (días)',1,30,30)
date=st.sidebar.text_input('Fecha histórica de origen (opcional)','2025-11-01')
if st.sidebar.button('Generar pronóstico',type='primary'):
 try:
  r=requests.get(f'{api}/pronostico/{port}',params={'dias':days,'fecha_origen':date or None},timeout=45);r.raise_for_status();data=r.json()
  frame=pd.DataFrame(data['pronosticos']);frame['fecha']=pd.to_datetime(frame['fecha'])
  fig=go.Figure()
  fig.add_trace(go.Scatter(x=frame.fecha,y=frame.limite_superior90_m,mode='lines',line={'width':0},showlegend=False))
  fig.add_trace(go.Scatter(x=frame.fecha,y=frame.limite_inferior90_m,mode='lines',line={'width':0},fill='tonexty',name='Intervalo empírico 90%'))
  fig.add_trace(go.Scatter(x=frame.fecha,y=frame.nivel_estimado_m,mode='lines+markers',name='Nivel pronosticado'))
  fig.update_layout(yaxis_title='Nivel (m)',xaxis_title='Fecha')
  st.plotly_chart(fig,use_container_width=True);st.dataframe(frame,use_container_width=True)
  st.warning(data['advertencia'])
 except Exception as e: st.error(f'No se pudo consultar la API: {e}')
