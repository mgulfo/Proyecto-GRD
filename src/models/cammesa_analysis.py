"""
src/models/cammesa_analysis.py
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
from datetime import datetime, timedelta

#imp de librerías externas 
import pandas as pd
import matplotlib.pyplot as plt
from adtk.visualization import plot
import matplotlib.dates as mdates
import random
import pandas as pd
import matplotlib.patches as Patches
from sklearn.metrics import mean_absolute_error

def leer_cammessa_csv():
    path = os.path.join(os.path.dirname(__file__), "Cammesa_res.csv")
    x = pd.read_csv(path, encoding='latin1', on_bad_lines='skip', sep=';', header=0)   
    y = x[['Fecha','AUTO+GUMAs','DEMANDA DISTRIBUIDOR','ALIMENTACIÓN. COMERCIOS Y SERVICIOS','INDUSTRIAS']]
    y['Fecha'] = pd.to_datetime(y['Fecha'], format='%d/%m/%Y')
    return y

def asociar_datos_energia(df_cam, mes):    
    df_res = df_cam[(df_cam['Fecha'].dt.month < mes) & (df_cam['Fecha'].dt.year == 2024)]
    return df_res

# Carga de datos limpios
clean_path = os.path.join("data", "raw", "df_clean.csv")
df_clean1 = pd.read_csv(clean_path, parse_dates=['time'])

# Selección de columnas necesarias
df_f = df_clean1[['time', 'PowA_L1_Ins']].copy()
df_f = df_f.set_index('time')

# Datos CAMMESA
dfc = leer_cammessa_csv()
dfr = asociar_datos_energia(dfc, 12)
dfr = dfr.set_index('Fecha')

# Crear figura con subplots alineados
fig, axes = plt.subplots(2, 1, figsize=(16, 8), sharex=True)

# Gráfico CAMMESA
dfr.plot(ax=axes[0])
axes[0].set_title('Demanda eléctrica por sector - CAMMESA (2024)', fontsize=13)
axes[0].set_ylabel('Demanda [MW]')
axes[0].legend(loc='upper right')
axes[0].grid(True)

# Gráfico de potencia L1
df_f.plot(ax=axes[1], color='tab:blue', legend=True)
axes[1].set_title('Potencia Activa Instantánea Fase L1 - Industria', fontsize=13)
axes[1].set_ylabel('Potencia [kW]')
axes[1].set_xlabel('Fecha')
axes[1].grid(True)

# Mejorar presentación
plt.tight_layout()
plt.xticks(rotation=45)
plt.subplots_adjust(hspace=0.3)

plt.show()
