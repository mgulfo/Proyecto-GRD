import warnings

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pandas as pd
import matplotlib.pyplot as plt
from models.anomaly_detection import filtrar_eventos_unicos

warnings.simplefilter(action='ignore', category=pd.errors.DtypeWarning)

# Cargar datos normales y resultados de anomalía
df = pd.read_csv("data/raw/df_norm.csv", low_memory=False)
df['time'] = pd.to_datetime(df['time'])
print(df.dtypes)
print(df['PowA_L1_Ins'].unique()[:10])
print(df['PowF_T_Ins'].unique()[:10])
print(df['THDI_L1_Ins'].unique()[:10])

# Cargar resultados de anomalía
anom = pd.read_csv("data/raw/anomalias_AutoReg.csv")
anom.index = pd.to_datetime(anom['time'])

# Seleccionar variable a analizar
variable = "THDI_L1_Ins"

# Asegurar que los índices estén alineados
df.set_index('time', inplace=True)
anom = anom.reindex(df.index, fill_value=False)

# === NUEVO: aplicar filtrado de eventos únicos
anom_filtradas = filtrar_eventos_unicos(anom[[variable]], min_sep=300, sample_rate_sec=10)

# Crear máscara de puntos anómalos
mask_filtradas = df.index.isin(anom_filtradas.index)

# Plot
plt.figure(figsize=(14, 5))
plt.plot(df.index, df[variable], label=variable, color='tab:blue', alpha=0.6)
plt.scatter(df.index[mask_filtradas], df[variable][mask_filtradas], color='r', label='Anomalías detectadas', s=15)
plt.title(f"Anomalías detectadas en {variable}")
plt.xlabel("Tiempo")
plt.ylabel("Valor normalizado")
plt.legend()
plt.tight_layout()
plt.grid(True)
plt.show()
