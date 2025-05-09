# === anomaly_detection.py ===

"""
Módulo XXXXXXXX
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import pandas as pd
from adtk.data import validate_series
from adtk.detector import LevelShiftAD, VolatilityShiftAD, AutoregressionAD
from adtk.visualization import plot
import matplotlib.pyplot as plt
import logging

#from tkat import TKAT
RANGE = 300

# Logger local para este módulo
logger = logging.getLogger("GenRodApp")


def crear_serie(df):
    """
    Prepara una serie temporal compatible con ADTK.
    """
    s = pd.DataFrame()
    s['time'] = pd.to_datetime(df['time'], errors='coerce')
    s['PowA_L1_Ins'] = df['PowA_L1_Ins']
    s['PowF_T_Ins'] = df['PowF_T_Ins']
    s['THDI_L1_Ins'] = df['THDI_L1_Ins']
    s["time"] = pd.to_datetime(s["time"], unit='s')
    s = s.set_index("time")
    logger.info(f"Preview de serie creada para ADTK:\n{s.head()}")
    return validate_series(s)


def correr_pruebas(df, serie):
    """
    Ejecuta y devuelve los resultados de los 3 métodos ADTK
    """
    logger.info("Corriendo métodos de detección de anomalías (ADTK)...")

    logger.info("Aplicando LevelShiftAD...")
    modela = LevelShiftAD(c=10, side='both', window=40)
    r = modela.fit_detect(serie)

    logger.info("Aplicando VolatilityShiftAD...")
    modelb = VolatilityShiftAD(c=12.0, side='both', window=200)
    k = modelb.fit_detect(serie)

    logger.info("Aplicando AutoregressionAD...")
    modelc = AutoregressionAD(n_steps=20, step_size=4, c=11.0)
    p = modelc.fit_detect(serie)

    return r, k, p

def filtrar_eventos_unicos(df_labels, min_sep=300, sample_rate_sec=10):
    """
    Devuelve un DataFrame con solo un punto por evento, filtrando anomalías consecutivas.
    - min_sep: número mínimo de muestras de separación entre eventos
    - sample_rate_sec: frecuencia de muestreo en segundos (default 10s)
    """
    
    df_labels = df_labels.copy()
    df_labels.index = pd.to_datetime(df_labels.index)
    df_labels = df_labels[df_labels.any(axis=1)]  # solo anomalías
    #df_labels = df_labels.sort_index()
    
    eventos = []
    last_time = None

    for idx in df_labels.index:
        if last_time is None or (idx - last_time).total_seconds() > (min_sep * sample_rate_sec):
            eventos.append(idx)
            last_time = idx

    df_eventos = df_labels.loc[eventos]
    return df_eventos

def generate_ts_anomalies(df_labels, df_datos, df_dst, df_dst2):
    RANGE = 300
    cc = 0

    # Resetear índice para evitar errores por datetime
    df_datos = df_datos.reset_index(drop=True)
    df_datos['time'] = pd.to_datetime(df_datos['time'])

    # Convertir labels al índice numérico
    label_times = pd.to_datetime(df_labels.index)
    df_times = pd.to_datetime(df_datos['time'])

    # Anomalías
    for t in label_times:
        if t not in df_times.values:
            continue
        pos = df_times[df_times == t].index[0]
        if pos - RANGE < 0:
            continue

        cc += 1
        ventana = df_datos.iloc[pos - RANGE:pos + 1][['time', 'PowF_T_Ins', 'THDI_L1_Ins']]
        df_dst = pd.concat([df_dst, ventana], ignore_index=True)

    # === NORMALES ===
    cx = 0
    anom_times = list(label_times)

    for i in range(RANGE + 1, len(df_datos)):
        t = df_datos.loc[i, 'time']
        
        # Si está muy cerca de alguna anomalía → descartamos
        if any(abs((t - ta).total_seconds()) < RANGE * 10 for ta in anom_times):
            continue

        if i - RANGE < 0:
            continue

        ventana = df_datos.iloc[i - RANGE:i + 1][['time', 'PowF_T_Ins', 'THDI_L1_Ins']]
        df_dst2 = pd.concat([df_dst2, ventana], ignore_index=True)
        cx += 1

        if cx >= cc:
            break

    # Estadísticas
    print("===== Estadísticas FP y THD =====")
    print(f"FP Media anomalias: {df_dst['PowF_T_Ins'].mean()}")
    print(f"FP desviacion anomalias: {df_dst['PowF_T_Ins'].std()}")
    print(f"FP Media normal: {df_dst2['PowF_T_Ins'].mean()}")
    print(f"FP desviacion normal: {df_dst2['PowF_T_Ins'].std()}")
    print(f"THD Media anomalias: {df_dst['THDI_L1_Ins'].mean()}")
    print(f"THD desviacion anomalias: {df_dst['THDI_L1_Ins'].std()}")
    print(f"THD Media normal: {df_dst2['THDI_L1_Ins'].mean()}")
    print(f"THD desviacion normal: {df_dst2['THDI_L1_Ins'].std()}")

    return df_dst, df_dst2

def metodo_propio(valores,df):
    ###Anomalias por metodo propio########################
    df_prueba = pd.DataFrame(df['time'])
    df_prueba['data'] = valores._resid.rolling(20).mean()
    df_prueba['data'] = df_prueba['data'].diff()
    val = df_prueba['data'] 
    plt.plot(df_prueba['data'], color='blue')
    plt.show()
    thresholdp = 0.05
    thresholdn = -0.05
    anomalies_filter = val.apply(lambda x: True if (x > thresholdp) or (x < thresholdn ) else False)
    anomalies = df['PowA_L1_Ins'][anomalies_filter]
    plt.figure(figsize=(14, 8))
    plt.scatter(x=anomalies.index, y=anomalies, color="red", label="anomalies")
    plt.plot(df.index, df['PowA_L1_Ins'], color='blue')
    plt.plot(df.index, df['THDI_L1_Ins'], color='orange')
    plt.title('Potencia activa')
    plt.xlabel('Fecha')
    plt.ylabel('Potencia')
    plt.legend()
    plt.show()  
    return anomalies_filter