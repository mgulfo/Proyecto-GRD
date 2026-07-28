import os
import sys
import time
from datetime import datetime, timezone
import pytz
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error
import config
from config import EJECUTAR_CAMMESA,OUTPUT_DIR, LISTA_DATOS_PREDICCION, MAX_ST, VISUALIZAR_MAE, LOCAL_TIMEZONE, LISTA_DATOS_PREDICCION, ERROR_UMBRAL, TAM_VENTANA, PASOS, SET_1, SET_2, SET_3, SET_4, MEDIA, PASOS_T1, PASOS_T2, PASOS_T3

import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from query_engine import busqueda_influx2, merge_data, subir_mae_influxdb_v2, obtener_ultimo_dato_dataframe, filtrar_dataframe_diccionario
from data_processing.data_cleaning import preprocess_data
#from config2 import OUTPUT_DIR, MAX_ST, VISUALIZAR_MAE, LOCAL_TIMEZONE
from utils.utils import convert_utc_to_local
from utils.logger import logger
import models.Predictor as predictor2
import models.analysis as analisis1
from models.Predictor import predictor_multi_lstm
import dataclasses
from dataclasses import dataclass
########################################################################
# Contadores y flags de estructura para distintos tiempos de prediccion
########################################################################
@dataclass
class contadores:
    contador_pasos_prediccion: int
    contador_check_prediccion: int
    flag_primer_prediccion: int
    pasos: int
    umbral: bool = False
@dataclass
class tiempos_prediccion:
    t1: contadores
    t2: contadores
    t3: contadores
# Definir zonas
arg_tz = pytz.timezone(LOCAL_TIMEZONE)
def busqueda_datos_consumo_locacion(start_time, end_time):
    dataM = busqueda_influx2(start_time, end_time, MEDIA)
    data01 = busqueda_influx2(start_time, end_time, SET_1)
    data02 = busqueda_influx2(start_time, end_time, SET_2)
    data03 = busqueda_influx2(start_time, end_time, SET_3)
    data04 = busqueda_influx2(start_time, end_time, SET_4)
    return dataM, data01, data02, data03, data04
def comparar_predicciones(df_ventana, df_prediccion, contador):    
    logger.info("Entra ventanas") 
    try:
        logger.info("Inicia ventanas")
        df_ventana_pred = df_prediccion[contador*TAM_VENTANA:(contador+1)*TAM_VENTANA]
        logger.info(f"Longitudes: la prediccion tiene:{len(df_ventana_pred)} y la ventana tiene:{len(df_ventana)}")    
        if len(df_ventana_pred) != len(df_ventana):
            raise ValueError(f"Longitudes desiguales: la ventana tiene {len(df_ventana_pred)} y prediccion tiene {len(df_prediccion)}")
        logger.info("Calcula mae")
        try:
            logger.info("Inicia calculo")             
            # 1. Filtramos las columnas originales excluyendo 'time'
            columnas_sin_time = [col for col in df_ventana.columns if col != 'time']
            # 2. Aseguramos que ambos DataFrames tengan las mismas columnas (sin 'time')
            df_ventana_filtrado = df_ventana[columnas_sin_time]
            df_ventana_pred = df_ventana_pred[columnas_sin_time]
            # 3. Validamos e imprimimos en el log
            #logger.info(f'las columnas unicas:{df_ventana_pred.columns.is_unique}')
            #logger.info(f"Arrays: la prediccion tiene:{df_ventana_pred.head(20)} y la ventana tiene:{df_ventana_filtrado.head(20)}")
            # 4. Calculamos el MAE de forma vectorizada sin la columna 'time'
            valores_mae = ((df_ventana_filtrado.reset_index(drop=True) - df_ventana_pred.reset_index(drop=True)).abs().mean())/df_ventana_filtrado.mean()
            logger.info(f'Valores mae:{valores_mae}')      
        except ValueError:
            # Si el error persiste, intenta transponiendo los datos (.T)
            logger.info("Problema de transposicion?") 
        logger.info("Se realiza comparacion con umbral")           
        umbral = bool((np.abs(valores_mae) > ERROR_UMBRAL).any())
        logger.info(f'El umbral es: {umbral}') 
        return umbral  
    except Exception as e:
        logger.info("Error en el procesado de las ventanas") 
        umbral = False       
        return umbral
def loop_continuo(location, pred_norm, df_clean, visualizar_mae=True):
    #####################################################################################
    #Inicializacion de variables para el loop continuo
    #####################################################################################
    train_pred = 1
    flag_primer_prediccion = 0
    contador_pasos_prediccion = 0
    contador_check_prediccion = 0
    t_pred = tiempos_prediccion(
        t1=contadores(contador_pasos_prediccion=0, contador_check_prediccion=0, flag_primer_prediccion=0, pasos=PASOS_T1),
        t2=contadores(contador_pasos_prediccion=0, contador_check_prediccion=0, flag_primer_prediccion=0, pasos=PASOS_T2),
        t3=contadores(contador_pasos_prediccion=0, contador_check_prediccion=0, flag_primer_prediccion=0, pasos=PASOS_T3)
    )   
    lista_contadores = [t_pred.t1, t_pred.t2, t_pred.t3]
    umbral = False   
    sin_datos_consecutivos = 0
    col_list = [col.strip() for col in LISTA_DATOS_PREDICCION.split(",") if col.strip()]
    df_f = df_clean[['time', 'PowA_L1_Ins']]
    if EJECUTAR_CAMMESA:
        dfc = analisis1.leer_cammessa_csv()
        dfr = analisis1.asociar_datos_energia(dfc,13,2024)    
        dfr.set_index('Fecha', inplace=True)
        df_f.set_index('time', inplace=True)    
        fig1, axes = plt.subplots(nrows=2, ncols=1)  
        dfr.plot(ax=axes[0], title='Datos cammesa')
        df_f.plot(ax=axes[1], title='Datos potencia')
        plt.show()
    logger.info("==== INICIO DE EJECUCION CONTINUA ====")
    #####################################################################################
    #Inicializacion de fechas y dataframes para el loop continuo
    #####################################################################################
    mae_filepath = os.path.join(OUTPUT_DIR, "mae_resultados.csv")    
    current_local_datetime = datetime.now()   
    utc_tz = pytz.timezone('UTC')
    #¡¡¡Se agrego + timezone.utc en esta linea
    now = datetime.now() 
    now_str = datetime.strftime(now, "%Y-%m-%dT%H:%M:%SZ")
    utc_time = now_str
    utc_time2 = utc_time
    logger.info(f"Hora inicial: {utc_time2}")
    df_temporal = pd.DataFrame(columns=[
        'time', 'PowA_L1_Ins', 'PowA_L2_Ins', 'PowA_L3_Ins',
        'PowF_T_Ins', 'THDI_L1_Ins', 'THDI_L2_Ins', 'THDI_L3_Ins'
    ])    
    df_temp_pred = pd.DataFrame(columns=col_list)
    df_mae = pd.DataFrame(columns=['time', 'MAE'])
    mae_1 = pd.DataFrame(columns=['time', 'MAE'])
    contador_anom = 0
    #df_pila_errores = pd.DataFrame(columns=col_list, rows=2, index=[0, 1])
    mae_hist = pd.DataFrame(columns=['time', 'MAE'])
    cont_mae_pred = 0   
    #####################################################################################
    #Lazo continuo para consulta, procesamiento, prediccion y calculo de MAE
    #####################################################################################
    while True:
        try:
            #Lineas de log comentadas. se pretende que solo haga log cuando hay eventos criticos o
            #periodicamente cada 2 min que esta operando normalmente            
            now = datetime.now(timezone.utc)
            now_str = datetime.strftime(now, "%Y-%m-%dT%H:%M:%SZ")
            utc_t = utc_tz.localize(datetime.strptime(now_str, "%Y-%m-%dT%H:%M:%SZ")) 
            utc_time = now_str
            if utc_time == utc_time2:
                #logger.warning("Rango de tiempo inválido. Saltando iteración.")
                time.sleep(8)
                continue
            #data_ult_medida = busqueda_influx2(utc_time2, utc_time, location)
            #df_m, df_set1, df_set2, df_set3, df_set4 = busqueda_datos_consumo_locacion(utc_time2, utc_time)
            #ultima_med = merge_data(data_ult_medida, silenciar_warning=True)
            data_ult_medida = obtener_ultimo_dato_dataframe(location)
            if not data_ult_medida.empty:
                #logger.info("Dataframe no vacio")
                data_ult_medida.columns = data_ult_medida.columns.droplevel(0)
                data_ult_medida = data_ult_medida.rename_axis('time')    
                #logger.info("Dataframe a filtrar")
                ultima_med = filtrar_dataframe_diccionario(data_ult_medida)
                #Convertimos el índice 'time' en columna normal AQUÍ
                # Usamos un bloque try/except por si acaso la función de filtrado ya lo había bajado
                try:
                    ultima_med = ultima_med.reset_index()
                except ValueError:
                    # Si entra aquí, significa que 'time' ya era una columna normal
                    pass
                # Limpiamos cualquier nombre residual en las columnas (como _field)
                ultima_med.columns.name = None 
            else:
                logger.info("Dataframe reciente vacio")
                ultima_med = data_ult_medida
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
                col_list = [col.strip() for col in LISTA_DATOS_PREDICCION.split(",") if col.strip()]
                df_temp = ultima_med[['time'] + col_list]
                s_pred = df_temp.iloc[[0]]
                s = df_t.iloc[[0]]
                #logger.info(f"df_t: \n{df_t}")
            except Exception as e:
                logger.warning(f"No se pudo obtener una fila válida de datos: {e}")
                time.sleep(8)
                continue
            ###########################################################################
            # Actualizacion de ultimo dato real para prediccion y calculo de MAE.
            ###########################################################################
            contador_anom += 1
            if (contador_anom % 10 == 0):
                logger.info(f"Lazo completado: {contador_anom}")
                #logger.info(f'El dataframe obtenido tras filtrar es:\n{ultima_med}')
            df_temp_pred = pd.concat([df_temp_pred, s_pred], ignore_index=True)
            df_temporal = pd.concat([df_temporal, s], ignore_index=True)
            contador_pasos_prediccion = contador_pasos_prediccion + 1

            if len(df_temporal) < MAX_ST:
                #logger.info(f"Aún no hay suficientes datos para aplicar predicción (actual: {len(df_temporal)}).")
                time.sleep(8)
                continue

            if len(df_temporal) > MAX_ST:
                df_temporal = df_temporal.tail(MAX_ST).reset_index(drop=True)                
            ##########################################################################
            #Rutina para crear slices de TAM_VENTANA de datos reales
            #y compararlos con el slice correspondiente de la prediccion
            #debe tener un contador para el tamaño de ventana y uno de 
            #pasos de prediccion total para poder realizar el desplazamiento
            #de ventana
            ###########################################################################
            
            try:
                if contador_pasos_prediccion >= TAM_VENTANA:
                    #logger.info("Primer paso logico")  
                    df_temp_pred1 = df_temp_pred.tail(TAM_VENTANA).reset_index(drop=True)  
                    contador_check_prediccion += 1                                  
                    if(flag_primer_prediccion > 0):
                        #logger.info("Segundo paso logico") 
                        umbral = comparar_predicciones(df_temp_pred1, df_datos_pred,contador_check_prediccion)
                    #reemplazar por N_PASOS_PRED/VENTANA_CHECK
                    if contador_check_prediccion >= ((PASOS/TAM_VENTANA)-1):
                        #logger.info("Tercer paso logico") 
                        contador_check_prediccion = 0
                    contador_pasos_prediccion = 0
                    df_temp_pred = df_temp_pred.drop(df_temp_pred.index)
                    #logger.info("Cuarto paso logico") 
            except Exception as e:
                logger.info("Error en logica")
                contador_check_prediccion = 0
                contador_pasos_prediccion = 0
                continue
            '''
            try:
            # Iteramos directamente sobre las instancias del objeto que contiene tus contadores
            # (Asumiendo que t_pred es una dataclass que agrupa instancias de contadores, 
            # o una lista/iterable de instancias)
            
                for contador in lista_contadores: 
                    # Si t_pred es un iterable de instancias (ej: lista de dataclasses):
                    # for contador in t_pred:
                    
                    if contador.contador_pasos_prediccion >= TAM_VENTANA:
                        # logger.info("Primer paso logico")
                        df_temp_pred1 = df_temp_pred.tail(TAM_VENTANA).reset_index(drop=True)
                        contador.contador_check_prediccion += 1
                        
                        if contador.flag_primer_prediccion > 0:
                            logger.info(f"Estructura de cuentas:{t_pred}")
                        
                        contador.umbral = comparar_predicciones(df_temp_pred1, df_datos_pred, contador.contador_check_prediccion)
                        
                        # Verificación de umbrales
                        if contador.contador_check_prediccion >= ((contador.pasos / TAM_VENTANA) - 1):
                            # logger.info("Tercer paso logico")
                            contador.contador_check_prediccion = 0
                            contador.contador_pasos_prediccion = 0
                            
                            # Forma segura de vaciar un DataFrame
                            df_temp_pred = df_temp_pred.iloc[0:0] 
                            # logger.info("Cuarto paso logico")

            except Exception as e:
                logger.error(f"Error en logica: {e}")  # Importante: loguear el error real
                
                # Reinicio al encontrar un error
                for contador in lista_contadores:
                    contador.contador_check_prediccion = 0
                    contador.contador_pasos_prediccion = 0
                
                continue
                '''
            #######################################################################
            #Calculo de mae y anotacion en dataframe para visualizacion en InfluxDB
            #######################################################################

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
                #########################################################################
                #Habilitada la prediccion, notifica el Indicador de eventos y
                #opera con el calculo del modelo por tiempo o por mae alto en tiempo real
                #########################################################################
                if train_pred == 1:                                  
                    cont_mae_pred = cont_mae_pred + 1                                          
                    if cont_mae_pred == 3:
                        logger.info(f"MAE de la predicción: {mae_anom}")                        
                        cont_mae_pred = 0
                    
                    now = datetime.now(timezone.utc)
                    if now.hour == 1 and now.minute == 12:
                        logger.info("Dispara predicción diaria")
                        nom = "Prediccion_diaria"
                        df_datos_pred = predictor_multi_lstm(df_clean, PASOS_T2, medidor=location, nombre=nom)
                        #umbral = False #Debe retornoar el umbral para no quedar disparado constantemente                                  
                    if now.minute == 50 or umbral == True:
                        flag_primer_prediccion = flag_primer_prediccion + 1
                        logger.info(f"Dispara predicción con valor de umbral: {umbral}")
                        nom = "Prediccion"
                        df_datos_pred = predictor_multi_lstm(df_clean, PASOS, medidor=location, nombre=nom)
                        umbral = False #Debe retornoar el umbral para no quedar disparado constantemente                    
                _clean = os.system('cls')
                ###############################################################################################################
                # Lazo para activar o desactivar gráfico en tiempo real del MAE (en variables de entorno está VISUALIZAR_MAE
                ##############################################################################################################
                if visualizar_mae:
                    if 'fig' not in globals():
                        plt.ion()
                        global fig, ax
                        fig, ax = plt.subplots(figsize=(10, 4))
                    mae_hist = pd.concat([mae_hist, pd.DataFrame([{'time': s.at[0, 'time'],'MAE': mae_anom}])], ignore_index=True)
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
                time.sleep(8)

            #########################################################################
            #Aqui colocamos la escritura del MAE en InfluxDB 2.7
            ##########################################################################            
            now = datetime.now(timezone.utc)
            now1 = now.strftime("%Y-%m-%dT%H:%M:%SZ")
            now_str = convert_utc_to_local(now1, "%Y-%m-%dT%H:%M:%SZ")            
            tiempo_local = now         
            mae_1 = pd.concat([mae_1, pd.DataFrame([{
            'time': tiempo_local,
            'MAE': mae_anom
            }])], ignore_index=True)
            subir_mae_influxdb_v2(mae_1)
            
        except Exception as e:
            logger.error(f"Error inesperado en la ejecución continua: {e}")
            break

    logger.info("==== FIN DE EJECUCION CONTINUA ====")
