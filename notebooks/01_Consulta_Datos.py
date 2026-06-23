# notebooks/01_consulta_datos.ipynb

# 👉 Este notebook muestra cómo consultar datos desde InfluxDB
# y realizar una visualización básica utilizando funciones del proyecto

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from query_engine import busqueda_influx, merge_data
from data_processing.data_cleaning import preprocess_data
from visualization import plot_time_series
import matplotlib.pyplot as plt

# Parámetros de consulta
fecha_inicio = '2023-08-01T00:00:00Z'
fecha_fin = '2023-08-02T00:00:00Z'
location = 'MEDIA'

# Consulta de datos desde InfluxDB 1.8
data = busqueda_influx(fecha_inicio, fecha_fin, location)
df = merge_data(data)

# Previsualización de los datos crudos
print("Datos crudos:")
print(df.head())

# Limpieza básica
df_clean = preprocess_data(df)
print("Datos limpios:")
print(df_clean.head())

# Visualización de Energía Consumida
if 'time' in df_clean.columns and 'EA_I_IV_T' in df_clean.columns:
    fig = plot_time_series(df_clean, 'time', ['EA_I_IV_T'], title='Energía Consumida')
    fig.show()
else:
    print("No se encontró la columna EA_I_IV_T para graficar.")
