'''
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
anom = pd.read_csv("data/raw/serie_anomala_AutoReg.csv")
anom['time'] = pd.to_datetime(anom['time'])

# Seleccionar variable a analizar
variable = "THDI_L1_Ins"

# Asegurar que los índices estén alineados
df.set_index('time', inplace=True)

anom = pd.read_csv("data/raw/serie_anomala_AutoReg.csv")
anom['time'] = pd.to_datetime(anom['time'])

# Eliminar duplicados directamente al cargar
anom.drop_duplicates(subset='time', inplace=True)
anom.set_index('time', inplace=True)
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
'''


import warnings
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt

# Configuración
warnings.simplefilter(action='ignore', category=pd.errors.DtypeWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from models.anomaly_detection import filtrar_eventos_unicos

# Parámetros de entrada
variable = "THDI_L1_Ins"  # Cambiar por "THDI_L1_Ins" o "PowF_T_Ins" si querés usar Factor de Potencia

# Cargar datos normalizados
df = pd.read_csv("data/raw/df_norm.csv", low_memory=False)
df['time'] = pd.to_datetime(df['time'])
df.set_index('time', inplace=True)

# Cargar resultados de anomalía y limpiar duplicados
anom = pd.read_csv("data/raw/serie_anomala_AutoReg.csv")
anom['time'] = pd.to_datetime(anom['time'])
anom.drop_duplicates(subset='time', inplace=True)
anom.set_index('time', inplace=True)
anom = anom.reindex(df.index, fill_value=False)

# Aplicar filtrado de eventos únicos
anom_filtradas = filtrar_eventos_unicos(anom[[variable]], min_sep=300, sample_rate_sec=10)

# Crear máscara de puntos anómalos
mask_filtradas = df.index.isin(anom_filtradas.index)

# === Gráfico con subplots ===
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 6), sharex=True, gridspec_kw={'height_ratios': [1.5, 1]})

# Subplot superior: Potencia Activa L1
ax1.plot(df.index, df["PowA_L1_Ins"], label="Potencia Activa L1", color='tab:green', alpha=0.7)
ax1.set_ylabel("Potencia Activa\n[Valor Normalizado]")
ax1.set_title("Potencia Activa vs. " + variable)
ax1.grid(True)
ax1.legend()

# Subplot inferior: Variable seleccionada con anomalías
ax2.plot(df.index, df[variable], label=variable, color='tab:blue', alpha=0.6)
ax2.scatter(df.index[mask_filtradas], df[variable][mask_filtradas], color='r', label='Anomalías detectadas', s=12)
ax2.set_ylabel("THDI\n[Valor Normalizado]")
ax2.set_xlabel("Tiempo")
ax2.grid(True)
ax2.legend()

plt.tight_layout()
plt.show()