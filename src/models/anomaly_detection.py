# === anomaly_detection.py ===

"""
Módulo XXXXXXXX
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import pandas as pd
import numpy as np
import logging
from adtk.data import validate_series
from adtk.detector import LevelShiftAD, VolatilityShiftAD, AutoregressionAD
from adtk.visualization import plot
import matplotlib.pyplot as plt
import logging
import matplotlib.patches as Patches
import calendar
from query_engine import busqueda_influx, merge_data
from data_processing.data_cleaning import preprocess_data, normalize_all_numeric
from sklearn.metrics import mean_absolute_error

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
    for column in df:
        s[column] = df[column]
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

def generate_ts_anomalies2(df_labels, df_datos, df_dst, df_dst2):
    """
    Genera series de tiempo con contexto para anómalos y normales (ESTUDIO)
    """    
    count = 0
    count_an = 0
    cc = 0
    RANGE = 300
    # Detección de anomalías
    for i,R in df_labels.iterrows():
        count = count + 1
        if (R['PowA_L1_Ins'] == True) and (R['THDI_L1_Ins'] == True):
            cc = cc + 1
            if(count < RANGE):
                RANGE = count -1
            else:
                RANGE = 300
            for j in range(RANGE):                
                for column in df_datos:
                    df_dst.at[count_an+j,column] = df_datos.at[count-RANGE-1+j,column]               
            for column in df_datos:
                df_dst.at[count_an+RANGE,column] = df_datos.at[count-1,column]           
            count_an = count_an + RANGE
    # Detección de normales
    count = 0
    count_an = 0
    cx = 0
    cont_anom = cc
    if (cc > 0):
        for i,R in df_labels.iterrows():
            count = count + 1
            if (R['PowA_L1_Ins'] == False) and (cx < cc) and (count > (RANGE*2)):
                cx = cx + 1
                for j in range(RANGE):
                    for column in df_datos:
                        df_dst2.at[count_an+j,column] = df_datos.at[count-RANGE-1+j,column]
                for column in df_datos:
                    df_dst2.at[count_an+RANGE,column] = df_datos.at[count-1,column]
                count_an = count_an + RANGE 
    else:        
        for i,R in df_labels.iterrows():
            count = count + 1
            if (R['PowA_L1_Ins'] == False) and (count > (RANGE*2)) and (cx < 5):
                cx = cx + 1
                for j in range(RANGE):
                    for column in df_datos:
                        df_dst2.at[count_an+j,column] = df_datos.at[count-RANGE-1+j,column]
                for column in df_datos:
                    df_dst2.at[count_an+RANGE,column] = df_datos.at[count-1,column] 
                count_an = count_an + RANGE    
    df_dst.set_index('time')
    df_dst2.set_index('time')
    medias_an = 0 
    desviaciones_an = 0
    medias_n = 0
    desviaciones_n = 0
    df_res1 = pd.DataFrame()
    for column in df_dst:
        _str = column
        if(_str != 'time'):
            _m = 'Media_an_'+_str
            _d = 'Desv_an_'+_str
            medias_an=df_dst[column].mean()
            desviaciones_an=df_dst[column].std()
            df_res1.insert(0,_m,0)
            df_res1.insert(0,_d,0)
            df_res1.at[1,_m] = medias_an 
            df_res1.at[1,_d] = desviaciones_an
            #df_res1.assign(_m=medias_an,_d=desviaciones_an)
           
    for column in df_dst2:
        _str = column
        if(_str != 'time'):
            _m = 'Media_n_'+_str
            _d = 'Desv_n_'+_str
            medias_n=df_dst2[column].mean()
            desviaciones_n=df_dst2[column].std()
            df_res1.insert(0,_m,0)
            df_res1.insert(0,_d,0)
            df_res1.at[1,_m] = medias_n 
            df_res1.at[1,_d] = desviaciones_n
            #df_res1.assign(_str=medias_n,_str=desviaciones_n) 
    columns_to_drop = [col for col in df_res1.columns if "PowA" in col]
    df_res1 = df_res1.drop(columns=columns_to_drop)     
    return df_dst, df_dst2, df_res1, cont_anom

def generate_ts_anomalies(df_labels, df_datos, df_dst, df_dst2, list_cols):
    """
    Genera series de tiempo con contexto para anómalos y normales (CÓDIGO)
    """    
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
        ventana = df_datos.iloc[pos - RANGE:pos + 1][list_cols]
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

        ventana = df_datos.iloc[i - RANGE:i + 1][list_cols]
        df_dst2 = pd.concat([df_dst2, ventana], ignore_index=True)
        cx += 1

        if cx >= cc:
            break

    df_dst.set_index('time')
    df_dst2.set_index('time')
    medias_an = 0 
    desviaciones_an = 0
    medias_n = 0
    desviaciones_n = 0
    df_res1 = pd.DataFrame()
    for column in df_dst:
        _str = column
        if(_str != 'time'):
            _m = 'Media_an_'+_str
            _d = 'Desv_an_'+_str
            medias_an=df_dst[column].mean()
            desviaciones_an=df_dst[column].std()
            df_res1.insert(0,_m,0)
            df_res1.insert(0,_d,0)
            df_res1.at[1,_m] = medias_an 
            df_res1.at[1,_d] = desviaciones_an
            #df_res1.assign(_m=medias_an,_d=desviaciones_an)
           
    for column in df_dst2:
        _str = column
        if(_str != 'time'):
            _m = 'Media_n_'+_str
            _d = 'Desv_n_'+_str
            medias_n=df_dst2[column].mean()
            desviaciones_n=df_dst2[column].std()
            df_res1.insert(0,_m,0)
            df_res1.insert(0,_d,0)
            df_res1.at[1,_m] = medias_n 
            df_res1.at[1,_d] = desviaciones_n
            #df_res1.assign(_str=medias_n,_str=desviaciones_n) 
    columns_to_drop = [col for col in df_res1.columns if "PowA" in col]
    df_res1 = df_res1.drop(columns=columns_to_drop)     
    return df_dst, df_dst2, df_res1,cc

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

######## Sección 5 del main ########
def deteccion_anomalias_pipeline(df_norm, list_cols, output_dir, save_csv=True):
    logger.info("===== INICIANDO DETECCIÓN DE ANOMALÍAS =====")

    df_prueba = df_norm[list_cols]
    df_p = crear_serie(df_prueba)
    res_levelshift, __, res_autoreg = correr_pruebas(df_prueba, df_p)

    detectores = {
        "LevelShift": res_levelshift,
        "AutoReg": res_autoreg
    }

    series_generadas = {}

    for nombre, resultado in detectores.items():
        logger.info(f"Procesando detector: {nombre}...")
        try:
            resultado_filtrado = filtrar_eventos_unicos(resultado, min_sep=300, sample_rate_sec=10)
        except Exception as e:
            logger.warning(f"Falló el filtrado de eventos únicos: {e}")
            resultado_filtrado = resultado.copy()

        df_resultado_anom = pd.DataFrame(columns=list_cols)
        df_resultado_norm = pd.DataFrame(columns=list_cols)

        try:
            df_st_anom, df_st_norm, df_resumen_anomalias, n_anomalias = generate_ts_anomalies(
                resultado_filtrado, df_prueba.copy(), df_resultado_anom, df_resultado_norm, list_cols
            )
            series_generadas[nombre] = (df_st_anom, df_st_norm, df_resumen_anomalias)
            logger.info(f"[{nombre}] Series generadas: {n_anomalias} anómalas, {df_st_norm.shape[0]} normales")
        except Exception as e:
            logger.warning(f"[{nombre}] Error generando series: {e}")

    # Selección
    SELECCION_DETECTOR = "AutoReg"
    df_st_anom, df_st_norm, df_resumen_anomalias = series_generadas[SELECCION_DETECTOR]

    if save_csv:
        df_st_anom.to_csv(os.path.join(output_dir, "serie_anomala_AutoReg.csv"), index=True)
        df_st_norm.to_csv(os.path.join(output_dir, "serie_normal_AutoReg.csv"), index=True)
        df_resumen_anomalias.to_csv(os.path.join(output_dir, "resumen_anomalias_AutoReg.csv"), index=False)
        res_autoreg.to_csv(os.path.join(output_dir, "anomalias_AutoReg.csv"), index=True)

    logger.info("===== DETECCIÓN COMPLETADA =====")
    return df_st_anom, df_st_norm, df_resumen_anomalias

import matplotlib.pyplot as plt

######## Sección 5 del main - Gráficos ########
def visualizar_series_anomalias(df_st_anom, df_st_norm):
    """
    Muestra dos gráficos: uno para las series con anomalías y otro para las normales.
    """
    # === Series con Anomalías ===
    plt.figure(figsize=(12, 6))
    plt.plot(df_st_anom.index, df_st_anom['PowF_T_Ins'], color='red', label='Factor de Potencia')
    plt.plot(df_st_anom.index, df_st_anom['THDI_L1_Ins'], color='green', label='Distorsión Armónica')
    plt.title("Series con Anomalías Detectadas", fontsize=14)
    plt.xlabel("Datos Previos a Anomalías Detectadas", fontsize=12)
    plt.ylabel("Valor Normalizado", fontsize=12)
    plt.grid(True)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
    plt.tight_layout()
    plt.show()

    # === Series Normales ===
    plt.figure(figsize=(12, 6))
    plt.plot(df_st_norm.index, df_st_norm['PowF_T_Ins'], color='red', label='Factor de Potencia')
    plt.plot(df_st_norm.index, df_st_norm['THDI_L1_Ins'], color='green', label='Distorsión Armónica')
    plt.title("Series Normales Detectadas", fontsize=14)
    plt.xlabel("Datos Previos SIN Anomalías Detectadas", fontsize=12)
    plt.ylabel("Valor Normalizado", fontsize=12)
    plt.grid(True)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
    plt.tight_layout()
    plt.show()

    ######## Sección 6 del main ########
# === FUNCIONES AUXILIARES PARA la función "analisis_anomalias" ===

def obtener_datos_mes(anio: int, mes: int, location: str) -> pd.DataFrame:
    start_date = f'{anio}-{mes:02d}-01T00:00:00Z'
    dias_mes = calendar.monthrange(anio, mes)[1]
    end_date = f'{anio}-{mes:02d}-{dias_mes:02d}T23:59:50Z'
    logger.info(f"Consultando datos desde {start_date} hasta {end_date}")

    data = busqueda_influx(start_date, end_date, location) ###ACAAAAAAAA
    df_raw = merge_data(data)
    df_clean = preprocess_data(df_raw)
    df_norm = normalize_all_numeric(df_clean)
    return df_norm


def procesar_anomalias_mes(df_mes: pd.DataFrame, columnas_objetivo: list) -> tuple:
    df_objetivo = df_mes[columnas_objetivo]
    df_serie = crear_serie(df_objetivo)
    _, _, predicciones = correr_pruebas(df_objetivo, df_serie)
    eventos_filtrados = filtrar_eventos_unicos(predicciones, min_sep=50, sample_rate_sec=10)

    df_anom = pd.DataFrame(columns=columnas_objetivo)
    df_norm = pd.DataFrame(columns=columnas_objetivo)

    df_st_anom, df_st_norm, df_resultado, n_anomalias = generate_ts_anomalies(
        eventos_filtrados, df_objetivo, df_anom, df_norm, columnas_objetivo
    )

    return df_resultado, n_anomalias


def agregar_resultado(df_total: pd.DataFrame, df_mensual: pd.DataFrame) -> pd.DataFrame:
    return pd.concat([df_total, df_mensual], ignore_index=True)


def graficar_resultados(df_estudio: pd.DataFrame):
    colnames = df_estudio.columns
    col_groups = [colnames[i:i+2] for i in range(0, len(colnames), 2)]
    df_centroide = df_estudio.copy(deep=False)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    for x, y in col_groups:
        if x not in df_estudio.columns or y not in df_estudio.columns:
            continue

        # Calcular centroide
        media_x = df_estudio[x].mean()
        media_y = df_estudio[y].mean()
        std_x = df_estudio[x].std()
        std_y = df_estudio[y].std()

        df_centroide.at[1, x] = media_x
        df_centroide.at[1, y] = media_y

        plt.scatter(df_estudio[x], df_estudio[y], label=f'{y.split(" ")[0]}')
        plt.scatter(media_x, media_y, label=f'{y.split(" ")[0]}_centroide')

        rect = Patches.Rectangle(
            (media_x - std_x, media_y - std_y),
            2 * std_x, 2 * std_y,
            color='green', alpha=0.2
        )
        ax.add_patch(rect)

    plt.legend(bbox_to_anchor=(1, 1), loc='upper right')
    plt.xlabel('Media')
    plt.ylabel('Desviación')
    plt.title('Comparación de series normales vs anómalas')
    plt.grid()
    plt.tight_layout()
    plt.show()


# === FUNCIÓN PRINCIPAL ===

def analisis_anomalias(df_inicial: pd.DataFrame, columnas_objetivo: list, pred_norm: str, anio_inicio: int, location: str):
    logger.info("=== INICIO DEL ANÁLISIS DE ANOMALÍAS ===")
    df_estudio = df_inicial.copy()
    anio_actual = anio_inicio
    anios_a_analizar = 2025 - anio_inicio

    for _ in range(anios_a_analizar - 1):
        anio_actual += 1
        logger.info(f"Año: {anio_actual}")
        for mes in range(1, 13):
            try:
                df_mes = obtener_datos_mes(anio_actual, mes, location)
                df_resultado, n_anomalias = procesar_anomalias_mes(df_mes, columnas_objetivo)
                df_estudio = agregar_resultado(df_estudio, df_resultado)

                if n_anomalias < 1:
                    logger.info(f"Mes {anio_actual}-{mes:02d}: sin anomalías detectadas.")
            except Exception as e:
                logger.warning(f"Error al procesar {anio_actual}-{mes:02d}: {e}")
                continue

    print(df_estudio.head(7))
    print(df_estudio.tail(7))

    graficar_resultados(df_estudio)

    logger.info("=== FIN DEL ANÁLISIS DE ANOMALÍAS ===")
    return df_estudio