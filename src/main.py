# main.py

"""
Script principal del proyecto de medición inteligente.
Orquesta las consultas a ambas bases de datos:
  - InfluxDB 1.8 (modelo antiguo, usando InfluxQL)
  - InfluxDB 2.7 (modelo nuevo, usando Flux)
  
Se solicitan las siguientes mediciones:
  - Voltage: Vrms_L1_Ins, Vrms_L2_Ins, Vrms_L3_Ins, THDV_L1_Ins, THDV_L2_Ins, THDV_L3_Ins
  - Power: PowA_L1_Ins, PowA_L2_Ins, PowA_L3_Ins, PowS_L1_Ins, PowS_L2_Ins, PowS_L3_Ins, PowF_T_Ins
  - Energy: EA_I_IV_T
  - Frequency: Fre_Ins
  - Current: Irms_L1_Ins, Irms_L2_Ins, Irms_L3_Ins, THDI_L1_Ins, THDI_L2_Ins, THDI_L3_Ins

El script realiza las consultas, fusiona los resultados en un único DataFrame y muestra las primeras y últimas filas 
para verificar que la conexión y los datos sean correctos. También genera un gráfico de ejemplo para visualizar la tensión en L1.
"""

import pandas as pd
import matplotlib.pyplot as plt
from functools import reduce

from db_connector import DBConnector
from config import INFLUXDB2_CONFIG
from data_processing.data_cleaning import clean_influx2_meta, clean_dataframe
from visualization import plot_time_series

############################################################################################################
# - Definición de funciones y parámetros de búsqueda de variables en BDs. UNA VEZ PROBADO, MODULARIZAR
############################################################################################################

def busqueda_influx1(fecha_inicio, fecha_fin, location):
    """
    Consulta a InfluxDB 1.8 utilizando InfluxQL para obtener las mediciones deseadas.

    Args:
        fecha_inicio (str): Fecha de inicio en formato ISO (e.g., '2023-12-01T00:00:00Z')
        fecha_fin (str): Fecha fin en formato ISO (e.g., '2023-12-31T23:59:50Z')
        location (str): Ubicación (e.g., "MEDIA")
    
    Returns:
        dict: Diccionario con DataFrames para cada medición.
    """
    db = DBConnector()
    client1 = db.connect_influxdb1()

    # Consulta para Voltaje
    query_voltage = f"""
    SELECT Vrms_L1_Ins, Vrms_L2_Ins, Vrms_L3_Ins, THDV_L1_Ins, THDV_L2_Ins, THDV_L3_Ins
    FROM "Voltage"
    WHERE time >= '{fecha_inicio}' AND time <= '{fecha_fin}'
      AND location='{location}'
    """
    points_voltage = db.query_influx1(query_voltage)
    df_voltage = pd.DataFrame(points_voltage)

    # Consulta para Potencia
    query_power = f"""
    SELECT PowA_L1_Ins, PowA_L2_Ins, PowA_L3_Ins, PowS_L1_Ins, PowS_L2_Ins, PowS_L3_Ins, PowF_T_Ins
    FROM "Power"
    WHERE time >= '{fecha_inicio}' AND time <= '{fecha_fin}'
      AND location='{location}'
    """
    points_power = db.query_influx1(query_power)
    df_power = pd.DataFrame(points_power)

    # Consulta para Energía
    query_energy = f"""
    SELECT EA_I_IV_T
    FROM "Energy"
    WHERE time >= '{fecha_inicio}' AND time <= '{fecha_fin}'
      AND location='{location}'
    """
    points_energy = db.query_influx1(query_energy)
    df_energy = pd.DataFrame(points_energy)

    # Consulta para Frecuencia
    query_frequency = f"""
    SELECT Fre_Ins
    FROM "Frequency"
    WHERE time >= '{fecha_inicio}' AND time <= '{fecha_fin}'
      AND location='{location}'
    """
    points_frequency = db.query_influx1(query_frequency)
    df_frequency = pd.DataFrame(points_frequency)

    # Consulta para Corriente
    query_current = f"""
    SELECT Irms_L1_Ins, Irms_L2_Ins, Irms_L3_Ins, THDI_L1_Ins, THDI_L2_Ins, THDI_L3_Ins
    FROM "Current"
    WHERE time >= '{fecha_inicio}' AND time <= '{fecha_fin}'
      AND location='{location}'
    """
    points_current = db.query_influx1(query_current)
    df_current = pd.DataFrame(points_current)

    return {
        'voltage': df_voltage,
        'power': df_power,
        'energy': df_energy,
        'frequency': df_frequency,
        'current': df_current
    }


def busqueda_influx2(fecha_inicio, fecha_fin, location):
    """
    Consulta a InfluxDB 2.7 utilizando Flux para obtener las mismas mediciones.
    Se replican los filtros de la consulta antigua.

    Args:
        fecha_inicio (str): Fecha de inicio en formato ISO con comillas simples (e.g., "'2023-12-01T00:00:00Z'")
        fecha_fin (str): Fecha fin en formato ISO con comillas simples (e.g., "'2023-12-31T23:59:50Z'")
        location (str): Ubicación (e.g., "MEDIA")
    
    Returns:
        dict: Diccionario con DataFrames para cada medición.
    """
    db = DBConnector()
    client2 = db.connect_influxdb2()
    query_api = client2.query_api()
    bucket = INFLUXDB2_CONFIG["bucket"]

    # Consulta para Voltaje
    query_voltage = f'''
    from(bucket:"{bucket}")
      |> range(start: time(v: "{fecha_inicio}"), stop: time(v: "{fecha_fin}"))
      |> filter(fn: (r) => r._measurement == "Voltage")
      |> filter(fn: (r) => r.location == "{location}")
      |> filter(fn: (r) =>
             r._field == "Vrms_L1_Ins" or
             r._field == "Vrms_L2_Ins" or
             r._field == "Vrms_L3_Ins" or
             r._field == "THDV_L1_Ins" or
             r._field == "THDV_L2_Ins" or
             r._field == "THDV_L3_Ins")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    df_voltage = query_api.query_data_frame(query=query_voltage)
    df_voltage = clean_influx2_meta(df_voltage)

    # Consulta para Potencia
    query_power = f'''
    from(bucket:"{bucket}")
      |> range(start: time(v: "{fecha_inicio}"), stop: time(v: "{fecha_fin}"))
      |> filter(fn: (r) => r._measurement == "Power")
      |> filter(fn: (r) => r.location == "{location}")
      |> filter(fn: (r) =>
             r._field == "PowA_L1_Ins" or
             r._field == "PowA_L2_Ins" or
             r._field == "PowA_L3_Ins" or
             r._field == "PowS_L1_Ins" or
             r._field == "PowS_L2_Ins" or
             r._field == "PowS_L3_Ins" or
             r._field == "PowF_T_Ins")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    df_power = query_api.query_data_frame(query=query_power)
    df_power = clean_influx2_meta(df_power)

    # Consulta para Energía
    query_energy = f'''
    from(bucket:"{bucket}")
      |> range(start: time(v: "{fecha_inicio}"), stop: time(v: "{fecha_fin}"))
      |> filter(fn: (r) => r._measurement == "Energy")
      |> filter(fn: (r) => r.location == "{location}")
      |> filter(fn: (r) => r._field == "EA_I_IV_T")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    df_energy = query_api.query_data_frame(query=query_energy)
    df_energy = clean_influx2_meta(df_energy)

    # Consulta para Frecuencia
    query_frequency = f'''
    from(bucket:"{bucket}")
      |> range(start: time(v: "{fecha_inicio}"), stop: time(v: "{fecha_fin}"))
      |> filter(fn: (r) => r._measurement == "Frequency")
      |> filter(fn: (r) => r.location == "{location}")
      |> filter(fn: (r) => r._field == "Fre_Ins")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    df_frequency = query_api.query_data_frame(query=query_frequency)
    df_frequency = clean_influx2_meta(df_frequency)

    # Consulta para Corriente
    query_current = f'''
    from(bucket:"{bucket}")
      |> range(start: time(v: "{fecha_inicio}"), stop: time(v: "{fecha_fin}"))
      |> filter(fn: (r) => r._measurement == "Current")
      |> filter(fn: (r) => r.location == "{location}")
      |> filter(fn: (r) =>
             r._field == "Irms_L1_Ins" or
             r._field == "Irms_L2_Ins" or
             r._field == "Irms_L3_Ins" or
             r._field == "THDI_L1_Ins" or
             r._field == "THDI_L2_Ins" or
             r._field == "THDI_L3_Ins")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    df_current = query_api.query_data_frame(query=query_current)
    df_current = clean_influx2_meta(df_current)

    return {
        'voltage': df_voltage,
        'power': df_power,
        'energy': df_energy,
        'frequency': df_frequency,
        'current': df_current
    }

def merge_data(dict_data):
    """
    Une los DataFrames obtenidos de las distintas consultas utilizando la columna de tiempo.
    Se asegura que la columna de tiempo esté unificada y en formato datetime.
    
    Args:
        dict_data (dict): Diccionario con DataFrames para cada medición.
        
    Returns:
        pd.DataFrame: DataFrame combinado.
    """
    def fix_time(df):
        if '_time' in df.columns:
            df = df.rename(columns={'_time': 'time'})
        if 'time' in df.columns:
            df['time'] = pd.to_datetime(df['time'], errors='coerce')
        return df

    dfs = [fix_time(dict_data[measure]) for measure in dict_data] 
    df_combined = reduce(lambda left, right: pd.merge(left, right, on="time", how="outer"), dfs)
    
    # Eliminar columnas duplicadas relacionadas al tiempo
    cols_to_drop = [col for col in df_combined.columns if "time" in col and col != "time"]
    if cols_to_drop:
        df_combined.drop(columns=cols_to_drop, inplace=True)
    return df_combined


############################################################################################################
# - MAIN
############################################################################################################

def main():
    # ------------------------------------
    # 1. CONSULTA A LA BD (Fecha de incumbencia de cada BD ... V1< 16/12/24 y V2>= 16/12/24)
    # ------------------------------------
    fecha_inicio_v1 = '2023-08-01T00:00:00Z'
    fecha_fin_v1 = '2023-08-11T23:59:50Z'
    
    fecha_inicio_v2 = "2025-01-20T00:00:00Z"
    fecha_fin_v2 = "2025-01-21T23:59:50Z"
    
    location = "MEDIA"

    print("Consultando InfluxDB 1.8 ...")
    data_v1 = busqueda_influx1(fecha_inicio_v1, fecha_fin_v1, location)
    df_combined_v1 = merge_data(data_v1)
    print("=== Datos combinados InfluxDB 1.8 ===")
    print(df_combined_v1.head())
    print(df_combined_v1.tail())
    
    print("\nConsultando InfluxDB 2.7 ...")
    data_v2 = busqueda_influx2(fecha_inicio_v2, fecha_fin_v2, location)
    df_combined_v2 = merge_data(data_v2)
    print("=== Datos combinados InfluxDB 2.7 ===")
    print(df_combined_v2.head())
    print(df_combined_v2.tail())
    
    # ------------------------------------
    # 2. LIMPIEZA BÁSICA
    # ------------------------------------
    df_clean = clean_dataframe(df_combined_v1)
    
    # Asegurarse de que la columna 'time' esté en datetime
    if 'time' in df_clean.columns:
        df_clean['time'] = pd.to_datetime(df_clean['time'], errors='coerce')

    # ------------------------------------
    # 3. GRÁFICOS EJEMPLO
    # ------------------------------------
    if "EA_I_IV_T" in df_clean.columns:
        fig_energy = plot_time_series(
            df_clean.dropna(subset=["EA_I_IV_T"]),
            time_col="time",
            value_cols=["EA_I_IV_T"],
            title="Energía Consumida (EA_I_IV_T)",
            xlabel="Tiempo",
            ylabel="Energía (unidades originales)"
        )
        plt.show(block=True)

if __name__ == "__main__":
    main()
