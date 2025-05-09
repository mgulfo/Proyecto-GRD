# src/main.py

#Config iniciales
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

#imp de módulos propios
import models.anomaly_detection as anom
from models.anomaly_detection import filtrar_eventos_unicos
from query_engine import busqueda_influx1, busqueda_influx2, merge_data
from data_processing.data_cleaning import preprocess_data, normalize_all_numeric
from utils.logger import logger
from utils.utils import save_normalization_stats, quality_report, hora_local_a_utc
from visualization import (
    plot_time_series,
    plot_boxplot,
    plot_histogram,
    plot_multiple_series
)
from config import (
    EXECUTE_VISUALIZATION,
    SHOW_GRAPHS,
    SAVE_OUTPUTS,
    OUTPUT_DIR,
    IMAGES_DIR,
    RANGE
)
# from event_detection import detect_anomalies          # ← A implementar más adelante
# from models.modeling import predict_consumption       # ← A implementar más adelante

#imp de librerías externas 
import pandas as pd
import matplotlib.pyplot as plt
from adtk.visualization import plot
import matplotlib.dates as mdates

def main():
    logger.info("==== INICIO DEL PROCESO ====")

    # ---------------------------------------------
    # 1. PARÁMETROS DE CONSULTA
    # ---------------------------------------------
    # Ingresás fechas en HORA ARGENTINA (lo que VOS querés)
    fecha_inicio_arg_v1 = '2023-02-28T21:00:00'
    fecha_fin_arg_v1    = '2023-03-31T00:00:30'
    fecha_inicio_arg_v2 = '2025-04-10T00:00:00'
    fecha_fin_arg_v2    = '2025-04-11T23:59:50'

    # Se convierte a UTC automáticamente
    fecha_inicio_v1 = hora_local_a_utc(fecha_inicio_arg_v1)
    fecha_fin_v1    = hora_local_a_utc(fecha_fin_arg_v1)
    fecha_inicio_v2 = hora_local_a_utc(fecha_inicio_arg_v2)
    fecha_fin_v2 = hora_local_a_utc(fecha_fin_arg_v2)
    location = "MEDIA"

    if SAVE_OUTPUTS:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        os.makedirs(IMAGES_DIR, exist_ok=True)

    # ---------------------------------------------
    # 2. CONSULTA A LAS BASES DE DATOS
    # ---------------------------------------------
    try:
        logger.info("Consultando InfluxDB 1.8 ...")
        data_v1 = busqueda_influx1(fecha_inicio_v1, fecha_fin_v1, location)
        df_v1 = merge_data(data_v1)
        #df_v1["time"] = pd.to_datetime(df_v1["time"]) + pd.Timedelta(hours=3)
        logger.info(f"Datos InfluxDB 1: {df_v1.shape}")

        logger.info("Consultando InfluxDB 2.7 ...")
        data_v2 = busqueda_influx2(fecha_inicio_v2, fecha_fin_v2, location)
        df_v2 = merge_data(data_v2)
        #df_v2["time"] = pd.to_datetime(df_v2["time"]) + pd.Timedelta(hours=3)
        logger.info(f"Datos InfluxDB 2: {df_v2.shape}")
    except Exception as e:
        logger.error(f"Error en la consulta: {e}")
        return
    logger.info(f"🕐 Fecha mínima: {df_v1['time'].min()} | Fecha máxima: {df_v1['time'].max()}")

    # Verificación básica
    if df_v1.empty:
        logger.warning("⚠️ Consulta a InfluxDB 1.8 no trajo datos")
    if df_v2.empty:
        logger.warning("⚠️ Consulta a InfluxDB 2.7 no trajo datos")
    if 'time' not in df_v1.columns:
        logger.warning("⚠️ 'time' no está en las columnas de df_v1")

    # Mostrar previews
    logger.info("📥 InfluxDB 1 - Preview:")
    print(df_v1.head())
    print(df_v1.tail())

    logger.info("📥 InfluxDB 2 - Preview:")
    print(df_v2.head())
    print(df_v2.tail())

    '''
    # Guardar datos crudos antes de limpieza
    if SAVE_OUTPUTS:
        raw_v1_path = os.path.join(OUTPUT_DIR, "df_v1_raw.csv")
        raw_v2_path = os.path.join(OUTPUT_DIR, "df_v2_raw.csv")
        df_v1.to_csv(raw_v1_path, index=False)
        df_v2.to_csv(raw_v2_path, index=False)
        logger.info(f"Datos crudos InfluxDB 1 guardados en {os.path.abspath(raw_v1_path)}")
        logger.info(f"Datos crudos InfluxDB 2 guardados en {os.path.abspath(raw_v2_path)}")
    '''
    
    # ---------------------------------------------
    # 3. LIMPIEZA DE DATOS
    # ---------------------------------------------
    logger.info("Limpieza básica ...")  
    df_clean_v1 = preprocess_data(df_v1)
    df_clean_v2 = preprocess_data(df_v2)

    if SAVE_OUTPUTS:
        clean_path_v1 = os.path.join(OUTPUT_DIR, "df_clean_v1.csv")
        df_clean_v1.to_csv(clean_path_v1, index=False)
        logger.info(f"Datos limpios InfluxDB 1 guardados en {os.path.abspath(clean_path_v1)}")

        clean_path_v2 = os.path.join(OUTPUT_DIR, "df_clean_v2.csv")
        df_clean_v2.to_csv(clean_path_v2, index=False)
        logger.info(f"Datos limpios InfluxDB 2 guardados en {os.path.abspath(clean_path_v2)}")

    # ---------------------------------------------
    # 4. NORMALIZACIÓN (para futuros modelos)
    # ---------------------------------------------
    df_norm_v1 = normalize_all_numeric(df_clean_v1)

    if SAVE_OUTPUTS:
        norm_path_v1 = os.path.join(OUTPUT_DIR, "df_norm_v1.csv")
        df_norm_v1.to_csv(norm_path_v1, index=False)
        logger.info(f"Datos normalizados InfluxDB 1 guardados en {os.path.abspath(norm_path_v1)}")
    # Guardar estadísticas de normalización
      #save_normalization_stats(df_norm_v1, output_path="data/stats/normalization_stats.json")

    # Generar quality report del dataset limpio
      #quality_report(df_clean_v1)

    '''
    # ---------------------------------------------
    # 5. VISUALIZACIONES
    # ---------------------------------------------
    if EXECUTE_VISUALIZATION:
        logger.info("Ejecutando visualizaciones...")

        if 'time' in df_clean_v1.columns and 'EA_I_IV_T' in df_clean_v1.columns:
            fig = plot_time_series(df_clean_v1, 'time', ['EA_I_IV_T'], title='Energía Consumida', ylabel='Energía')
            if fig and SAVE_OUTPUTS:
                fig.savefig(os.path.join(IMAGES_DIR, "energia_consumida.png"))
            if SHOW_GRAPHS and fig:
                fig.show()
            else:
                plt.close(fig)

        fig = plot_boxplot(df_clean_v1, ['Vrms_L1_Ins', 'Vrms_L2_Ins', 'Vrms_L3_Ins'], title='Tensión por Fase')
        if fig and SAVE_OUTPUTS:
            fig.savefig(os.path.join(IMAGES_DIR, "boxplot_tension.png"))
        if SHOW_GRAPHS and fig:
            fig.show()
        else:
            plt.close(fig)

        for col in ['Irms_L1_Ins', 'Irms_L2_Ins', 'Irms_L3_Ins']:
            fig = plot_histogram(df_clean_v1, col)
            if fig and SAVE_OUTPUTS:
                fig.savefig(os.path.join(IMAGES_DIR, f"hist_{col}.png"))
            if SHOW_GRAPHS and fig:
                fig.show()
            else:
                plt.close(fig)

        figuras = plot_multiple_series(df_clean_v1, 'time', {
            'Tensión': ['Vrms_L1_Ins', 'Vrms_L2_Ins', 'Vrms_L3_Ins'],
            'Corriente': ['Irms_L1_Ins', 'Irms_L2_Ins', 'Irms_L3_Ins'],
            'Potencia Activa': ['PowA_L1_Ins', 'PowA_L2_Ins', 'PowA_L3_Ins']
        })
        for grupo, fig in figuras:
            if fig and SAVE_OUTPUTS:
                fig.savefig(os.path.join(IMAGES_DIR, f"grupo_{grupo.lower().replace(' ', '_')}.png"))
            if SHOW_GRAPHS and fig:
                fig.show()
            else:
                plt.close(fig)
    '''

    # ---------------------------------------------
    # 6. DETECCIÓN DE PERTURBACIONES
    # ---------------------------------------------
    
    # === DETECCIÓN DE ANOMALÍAS ===
    logger.info("===== INICIANDO DETECCIÓN DE ANOMALÍAS =====")

    # Filtrar columnas relevantes
    logger.info("Filtrando columnas clave para análisis...")
    df_prueba = df_norm_v1[['time','PowA_L1_Ins','PowF_T_Ins','THDI_L1_Ins']]

    # Crear serie temporal validada
    logger.info("Creando serie temporal para ADTK...")
    df_p = anom.crear_serie(df_prueba)
    logger.info("Preview de serie creada para ADTK:\n%s", df_p.head())

    # Ejecutar detectores de anomalías
    rr, __, pp = anom.correr_pruebas(df_prueba, df_p)   

    # Guardar resultados del último detector
    logger.info("Guardando resultados de los 2 modelos de detección...")
    rr.to_csv(os.path.join(OUTPUT_DIR, "anomalias_LevelShift.csv"))
    pp.to_csv(os.path.join(OUTPUT_DIR, "anomalias_AutoReg.csv"), index=True)
    
    logger.info(f"LevelShiftAD detectó {rr.any(axis=1).sum()} anomalías")
    for col in rr.columns:
        logger.info(f"AutoregressionAD detectó {rr[col].sum()} anomalías en {col}")

    logger.info(f"AutoregressionAD detectó {pp.any(axis=1).sum()} anomalías")
    for col in pp.columns:
        logger.info(f"AutoregressionAD detectó {pp[col].sum()} anomalías en {col}")
    
    detectores = {
        "LevelShift": rr,
        "AutoReg": pp
    }

    for nombre, resultado in detectores.items():
        logger.info(f"Generando series para {nombre}...")
        
        # Filtrar eventos únicos antes de pasar a generate_ts_anomalies
        resultado_filtrado = filtrar_eventos_unicos(resultado, min_sep=300, sample_rate_sec=10)
        logger.info(f"{nombre}: {resultado_filtrado.shape[0]} eventos únicos seleccionados")
        
        df_resultado_anom = pd.DataFrame({'time':[], 'PowA_L1_Ins':[], 'PowF_T_Ins':[], 'THDI_L1_Ins':[]})
        df_resultado_norm = pd.DataFrame({'time':[], 'PowA_L1_Ins':[], 'PowF_T_Ins':[], 'THDI_L1_Ins':[]})

        try:
            df_anom, df_norm = anom.generate_ts_anomalies(resultado_filtrado, df_prueba.copy(), df_resultado_anom, df_resultado_norm)

            if not df_anom.empty:
                df_anom.to_csv(os.path.join(OUTPUT_DIR, f"series_anomalas_{nombre}.csv"), index=False)
                df_norm.to_csv(os.path.join(OUTPUT_DIR, f"series_normales_{nombre}.csv"), index=False)
                logger.info(f"Series para {nombre} guardadas: {df_anom.shape[0]} anómalas, {df_norm.shape[0]} normales")
            else:
                logger.warning(f"[!] No se generaron series para {nombre} (df_anom vacío)")

        except Exception as e:
            logger.warning(f"[!] Error generando series para {nombre}: {e}")
    
    #                                  #
    # Visualizar resultados (opcional) # 
    #                                  # 

    ### Gráfico Series CON anomalías
    plt.figure(figsize=(12, 6))
    #plt.plot(df_anom.index, df_anom['PowF_T_Ins'], color='red')
    #plt.plot(df_anom.index, df_anom['THDI_L1_Ins'], color='green')
    plt.plot(df_anom.index, df_anom['PowF_T_Ins'], color='red', label='Factor de Potencia')
    plt.plot(df_anom.index, df_anom['THDI_L1_Ins'], color='green', label='Distorción Armónica')
    plt.title("Series con Anomalías Detectadas", fontsize=14)
    plt.xlabel("Datos Previos a Anomalías Detectadas", fontsize=12)
    plt.ylabel("Valor Normalizado", fontsize=12)
    plt.grid(True)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
    #plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

        ### Gráfico Series SIN anomalías
    plt.plot(df_norm.index, df_norm['PowF_T_Ins'], color='red', label='Factor de Potencia')
    plt.plot(df_norm.index, df_norm['THDI_L1_Ins'], color='green', label='Distorción Armónica')
    plt.title("Series sin Anomalías Detectadas", fontsize=14)
    plt.xlabel("Datos Previos SIN Anomalías Detectadas", fontsize=12)
    plt.ylabel("Valor Normalizado", fontsize=12)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
    #plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    logger.info("===== DETECCIÓN COMPLETADA =====")
    
    # ---------------------------------------------
    # 7. PREDICCIÓN DE CONSUMO (próxima etapa)
    # ---------------------------------------------
    # predicciones = predict_consumption(df_norm_v1)
    # print(predicciones.head())
        
    logger.info("==== FIN DEL PROCESO ====")

# ESTA PARTE VA FUERA DE LA FUNCIÓN MAIN
if __name__ == "__main__":
    main()