# src/main.py

#Config iniciales
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import sys
import os
from datetime import datetime, timezone, timedelta
import calendar
import time
import pytz


current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

#imp de módulos propios
import models.anomaly_detection as anom
from models.prediction_lstm import correr_prediccion
from models.anomaly_detection import analisis_anomalias, visualizar_series_anomalias
from models.prediction_lstm import evaluar_prediccion
from models.cammesa_analysis import leer_cammessa_csv, asociar_datos_energia
from query_engine import consultar_datos_influx
from data_processing.data_cleaning import preprocess_data, normalize_all_numeric
from utils.logger import logger
from utils.utils import hora_local_a_utc
from ejecucion_continua.ejecutar_loop_continuo import loop_continuo

from config import (
    EXECUTE_VISUALIZATION,
    SHOW_GRAPHS,
    SAVE_OUTPUTS,
    OUTPUT_DIR,
    IMAGES_DIR,
    EJECUTAR_ANALISIS_ANOMALIAS,
    VISUALIZAR_MAE,
    LOCAL_TIMEZONE
)

# Definir zonas
arg_tz = pytz.timezone(LOCAL_TIMEZONE)

#imp de librerías externas 
import pandas as pd
import matplotlib.pyplot as plt
from adtk.visualization import plot
import matplotlib.dates as mdates
import random
import pandas as pd
import matplotlib.patches as Patches
from sklearn.metrics import mean_absolute_error

def main():

    logger.info("==== INICIO DEL PROCESO ====")

    # ---------------------------------------------
    # 1. PARÁMETROS DE CONSULTA
    # ---------------------------------------------
    
    # Ingrese fechas en HORA ARGENTINA (lo que VOS querés)
    fecha_inicio_arg = '2024-01-01T00:00:00'
    fecha_fin_arg    = '2024-12-31T23:59:00'

    # Se convierte a UTC automáticamente
    fecha_inicio = hora_local_a_utc(fecha_inicio_arg)
    fecha_fin    = hora_local_a_utc(fecha_fin_arg)

    # Locación
    location = "MEDIA"

    if SAVE_OUTPUTS:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        os.makedirs(IMAGES_DIR, exist_ok=True)

    # ---------------------------------------------
    # 2. CONSULTA A LAS BASES DE DATOS
    # ---------------------------------------------

    df = consultar_datos_influx(fecha_inicio, fecha_fin, location, output_dir=OUTPUT_DIR, guardar=SAVE_OUTPUTS)

    if df.empty or 'time' not in df.columns:
        logger.error("No se puede continuar: DataFrame inválido")
        return

    # ---------------------------------------------
    # 3. LIMPIEZA DE DATOS
    # ---------------------------------------------

    logger.info("Limpieza básica ...")
    df_clean = preprocess_data(df)
  
    if SAVE_OUTPUTS:
        clean_path = os.path.join(OUTPUT_DIR, "df_clean.csv")
        df_clean.to_csv(clean_path, index=False)
        logger.info(f"Datos limpios InfluxDB guardados en {os.path.abspath(clean_path)}")

    # ---------------------------------------------
    # 4. NORMALIZACIÓN
    # ---------------------------------------------

    df_norm = normalize_all_numeric(df_clean)

    if SAVE_OUTPUTS:
        norm_path = os.path.join(OUTPUT_DIR, "df_norm.csv")
        df_norm.to_csv(norm_path, index=False)
        logger.info(f"Datos normalizados InfluxDB guardados en {os.path.abspath(norm_path)}")

    # ---------------------------------------------
    # 5. DETECCIÓN DE PERTURBACIONES
    # ---------------------------------------------

    list_cols = ['time','PowA_L1_Ins','PowF_T_Ins','THDI_L1_Ins']
    df_st_anom, df_st_norm, df_resumen_anomalias = anom.deteccion_anomalias_pipeline(df_norm, list_cols, OUTPUT_DIR)

    if SHOW_GRAPHS:
        anom.visualizar_series_anomalias(df_st_anom, df_st_norm)

    # ---------------------------------------------
    # 6. ANÁLISIS POST-DETECCIÓN DE ANOMALÍA       
    # ---------------------------------------------

    # Flag de control (puede centralizarse en config si se estabiliza)
    EJECUTAR_ANALISIS_ANOMALIAS = False

    if EJECUTAR_ANALISIS_ANOMALIAS:
        logger.info("Ejecutando análisis de anomalías post detección...")
        analisis_anomalias(df_resumen_anomalias, list_cols , pred_norm, 2023, location) 

    # ---------------------------------------------
    # 7. EVALUACIÓN DE PREDICCIÓN
    # ---------------------------------------------
    
    # Flag de control (puede centralizarse en config si se estabiliza)    
    EJECUTAR_EVALUACION = True
    MOSTRAR_GRAFICO_PREDICCION = True

    if EJECUTAR_EVALUACION:
        mae_normal, mae_anom, pred_norm, pred_anom = evaluar_prediccion(
            df_st_norm, df_st_anom, visualizar_prediccion=MOSTRAR_GRAFICO_PREDICCION
        )

    # ---------------------------------------------
    # 8. EJECUCION CONTINUA 
    # ---------------------------------------------
    
    # Flag de control (puede centralizarse en config si se estabiliza)
    VISUALIZAR_MAE = False

    loop_continuo(location, pred_norm, df_clean, visualizar_mae=VISUALIZAR_MAE)

    logger.info("==== FIN DEL PROCESO ====")

# ESTA PARTE VA FUERA DE LA FUNCIÓN MAIN
if __name__ == "__main__":
    main()