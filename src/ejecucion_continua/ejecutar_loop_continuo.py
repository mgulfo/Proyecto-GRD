import os
import sys
import time
from datetime import datetime
import pytz
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error

import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from query_engine import busqueda_influx2, merge_data
from data_processing.data_cleaning import preprocess_data
from config import OUTPUT_DIR, MAX_ST, VISUALIZAR_MAE, LOCAL_TIMEZONE

from utils.logger import logger

# Definir zonas
arg_tz = pytz.timezone(LOCAL_TIMEZONE)

def loop_continuo(location, pred_norm, df_clean, visualizar_mae=True):

    logger.info("==== INICIO DE EJECUCION CONTINUA ====")
    mae_filepath = os.path.join(OUTPUT_DIR, "mae_resultados.csv")
    sin_datos_consecutivos = 0

    # Inicialización   
    utc_tz = pytz.timezone('UTC')
    now = datetime.now()
    now_str = datetime.strftime(now, "%Y-%m-%dT%H:%M:%SZ")
    utc_t = utc_tz.localize(datetime.strptime(now_str, "%Y-%m-%dT%H:%M:%SZ")) 
    utc_time = now_str
    utc_time2 = utc_time

    logger.info(f"Hora inicial: {utc_time2}")

    df_temporal = pd.DataFrame(columns=[
        'time', 'PowA_L1_Ins', 'PowA_L2_Ins', 'PowA_L3_Ins',
        'PowF_T_Ins', 'THDI_L1_Ins', 'THDI_L2_Ins', 'THDI_L3_Ins'
    ])
    df_mae = pd.DataFrame(columns=['time', 'MAE'])
    contador_anom = 0

    # Acumulador de errores
    mae_hist = pd.DataFrame(columns=['time', 'MAE'])

    while True:
        try:
            logger.info("Consultando InfluxDB 2.7 ...")
            now = datetime.now()
            now_str = datetime.strftime(now, "%Y-%m-%dT%H:%M:%SZ")
            utc_t = utc_tz.localize(datetime.strptime(now_str, "%Y-%m-%dT%H:%M:%SZ")) 
            utc_time = now_str
            logger.info(f"Hora actual: {utc_time}")

            if utc_time == utc_time2:
                logger.warning("Rango de tiempo inválido. Saltando iteración.")
                time.sleep(8)
                continue

            data_ult_medida = busqueda_influx2(utc_time2, utc_time, location)
            ultima_med = merge_data(data_ult_medida, silenciar_warning=True)

            if ultima_med.empty:
                sin_datos_consecutivos += 1
                if sin_datos_consecutivos >= 3:
                    logger.warning(f"No se obtienen datos nuevos desde hace {sin_datos_consecutivos} iteraciones.")
                else:
                    logger.info("Sin nuevos datos. Esperando siguiente iteración.")
                time.sleep(8)
                continue
            else:
                sin_datos_consecutivos = 0

            utc_time2 = utc_time

            df_t = ultima_med[[
                'time', 'PowA_L1_Ins', 'PowA_L2_Ins', 'PowA_L3_Ins',
                'PowF_T_Ins', 'THDI_L1_Ins', 'THDI_L2_Ins', 'THDI_L3_Ins']]

            try:
                s = df_t.iloc[[0]]
                logger.info(f"df_t: \n{df_t}")
            except Exception as e:
                logger.warning(f"No se pudo obtener una fila válida de datos: {e}")
                time.sleep(8)
                continue

            contador_anom += 1
            logger.info(f"Lazo completado: {contador_anom}")

            df_temporal = pd.concat([df_temporal, s], ignore_index=True)

            if len(df_temporal) < MAX_ST:
                logger.info(f"Aún no hay suficientes datos para aplicar predicción (actual: {len(df_temporal)}).")
                time.sleep(8)
                continue

            if len(df_temporal) > MAX_ST:
                df_temporal = df_temporal.tail(MAX_ST).reset_index(drop=True)

            df_t_proc = preprocess_data(df_temporal.copy(), silenciar_logs=True)
            n = min(len(df_t_proc), MAX_ST)
            x = pred_norm.iloc[0:n].copy()
            x['LSTM Prediction'] = (
                x['LSTM Prediction'] * (df_clean['PowF_T_Ins'].max() - df_clean['PowF_T_Ins'].min())
            ) + df_clean['PowF_T_Ins'].min()

            if len(df_t_proc) != len(x):
                logger.warning(f"Dimensiones incompatibles: df_t_proc={len(df_t_proc)} vs pred={len(x)}. Saltando.")
                continue

            try:
                time_utc = pd.to_datetime(s.at[0, 'time'])
                if time_utc.tzinfo is None:
                    time_utc = time_utc.tz_localize(arg_tz)
                time_local = time_utc.astimezone(pytz.UTC)

                mae_anom = mean_absolute_error(df_t_proc['PowF_T_Ins'], x['LSTM Prediction'])
                logger.info(f"MAE calculado: {mae_anom}")

                df_mae = pd.DataFrame([{
                    'time_utc': time_utc.strftime("%Y-%m-%d %H:%M:%S"),
                    'time_local': time_local.strftime("%Y-%m-%d %H:%M:%S"),
                    'MAE': mae_anom
                }])

                if os.path.exists(mae_filepath):
                    df_mae.to_csv(mae_filepath, mode='a', header=False, index=False)
                else:
                    df_mae.to_csv(mae_filepath, mode='w', header=True, index=False)

                # Lazo para activar o desactivar gráfico en tiempo real del MAE (en config.py está VISUALIZAR_MAE)
                if visualizar_mae:
                    if 'fig' not in globals():
                        plt.ion()
                        global fig, ax
                        fig, ax = plt.subplots(figsize=(10, 4))

                    mae_hist = pd.concat([mae_hist, pd.DataFrame([{
                        'time': s.at[0, 'time'],
                        'MAE': mae_anom
                    }])], ignore_index=True)

                    # Guardar mae
                    mae_hist = mae_hist.tail(100)
                    mae_hist['time'] = pd.to_datetime(mae_hist['time'])

                    ax.clear()
                    ax.plot(mae_hist['time'], mae_hist['MAE'], marker='o', linestyle='-')
                    ax.set_title("MAE en tiempo real")
                    ax.set_xlabel("Hora")
                    ax.set_ylabel("MAE")
                    ax.tick_params(axis='x', rotation=45)
                    ax.grid(True)
                    plt.tight_layout()
                    plt.pause(0.01)

            except Exception as e:
                logger.warning(f"Error en el cálculo o guardado del MAE: {e}")
                logger.info(f"Último UTC procesado: {utc_time2}")
                time.sleep(10)

        except Exception as e:
            logger.error(f"Error inesperado en la ejecución continua: {e}")
            break

    logger.info("==== FIN DE EJECUCION CONTINUA ====")
