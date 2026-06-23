# tests/test_query_engine.py

'''
🧪 Test Query Engine

-> Verifica que merge_data() incluya la columna time

-> Asegura que no esté vacía y que sea tipo datetime
'''

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from query_engine import busqueda_influx, merge_data
import pandas as pd

# Parámetros de prueba (ajustar si es necesario)
fecha_inicio = '2023-08-01T00:00:00Z'
fecha_fin = '2023-08-02T00:00:00Z'
location = 'MEDIA'

def test_merge_data_includes_time():
    data = busqueda_influx(fecha_inicio, fecha_fin, location) #ACAAAAAAAA
    df = merge_data(data)
    assert not df.empty, "La consulta no debe devolver un DataFrame vacío"
    assert 'time' in df.columns, "El DataFrame combinado debe contener la columna 'time'"
    assert pd.api.types.is_datetime64_any_dtype(df['time']), "La columna 'time' debe ser tipo datetime"
