# src/query_engine.py

from db_connector import DBConnector
from config import INFLUXDB2_CONFIG
from data_processing.data_cleaning import clean_influx2_meta
from utils.logger import logger
import pandas as pd
from functools import reduce
from config import LOCAL_TIMEZONE
from utils.utils import convert_df_utc_to_local


def busqueda_influx1(fecha_inicio, fecha_fin, location):
    db = DBConnector()
    client1 = db.connect_influxdb1()

    queries = {
        "voltage": f"""
            SELECT Vrms_L1_Ins, Vrms_L2_Ins, Vrms_L3_Ins, THDV_L1_Ins, THDV_L2_Ins, THDV_L3_Ins
            FROM "Voltage"
            WHERE time >= '{fecha_inicio}' AND time <= '{fecha_fin}' AND location='{location}'
        """,
        "power": f"""
            SELECT PowA_L1_Ins, PowA_L2_Ins, PowA_L3_Ins, PowS_L1_Ins, PowS_L2_Ins, PowS_L3_Ins, PowF_T_Ins
            FROM "Power"
            WHERE time >= '{fecha_inicio}' AND time <= '{fecha_fin}' AND location='{location}'
        """,
        "energy": f"""
            SELECT EA_I_IV_T FROM "Energy"
            WHERE time >= '{fecha_inicio}' AND time <= '{fecha_fin}' AND location='{location}'
        """,
        "frequency": f"""
            SELECT Fre_Ins FROM "Frequency"
            WHERE time >= '{fecha_inicio}' AND time <= '{fecha_fin}' AND location='{location}'
        """,
        "current": f"""
            SELECT Irms_L1_Ins, Irms_L2_Ins, Irms_L3_Ins, THDI_L1_Ins, THDI_L2_Ins, THDI_L3_Ins
            FROM "Current"
            WHERE time >= '{fecha_inicio}' AND time <= '{fecha_fin}' AND location='{location}'
        """
    }

    results = {}
    for key, query in queries.items():
        try:
            logger.info(f"Ejecutando consulta InfluxDB 1.8: {key}")
            points = db.query_influx1(query)
            results[key] = pd.DataFrame(points)
            results[key] = convert_df_utc_to_local(results[key], 'time')
            logger.info(f"Consulta {key} completada con {len(results[key])} registros")
        except Exception as e:
            logger.error(f"[ERROR] Consulta {key} falló: {e}")
            results[key] = pd.DataFrame()

    return results

def busqueda_influx2(fecha_inicio, fecha_fin, location):
    db = DBConnector()
    client2 = db.connect_influxdb2()
    query_api = client2.query_api()
    bucket = INFLUXDB2_CONFIG["bucket"]

    fields = {
        "voltage": ["Vrms_L1_Ins", "Vrms_L2_Ins", "Vrms_L3_Ins", "THDV_L1_Ins", "THDV_L2_Ins", "THDV_L3_Ins"],
        "power": ["PowA_L1_Ins", "PowA_L2_Ins", "PowA_L3_Ins", "PowS_L1_Ins", "PowS_L2_Ins", "PowS_L3_Ins", "PowF_T_Ins"],
        "energy": ["EA_I_IV_T"],
        "frequency": ["Fre_Ins"],
        "current": ["Irms_L1_Ins", "Irms_L2_Ins", "Irms_L3_Ins", "THDI_L1_Ins", "THDI_L2_Ins", "THDI_L3_Ins"]
    }

    results = {}
    for measure, variables in fields.items():
        filter_fields = " or\n             ".join([f'r._field == "{v}"' for v in variables])
        query = f'''
        from(bucket:"{bucket}")
          |> range(start: time(v: "{fecha_inicio}"), stop: time(v: "{fecha_fin}"))
          |> filter(fn: (r) => r._measurement == "{measure.capitalize()}")
          |> filter(fn: (r) => r.location == "{location}")
          |> filter(fn: (r) => {filter_fields})
          |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        '''
        try:
            logger.info(f"Ejecutando consulta InfluxDB 2.0: {measure}")
            df = query_api.query_data_frame(query=query)
            results[measure] = clean_influx2_meta(df)
            results[measure] = convert_df_utc_to_local(results[measure], 'time')
            logger.info(f"Consulta {measure} completada con {len(results[measure])} registros")
        except Exception as e:
            logger.error(f"[ERROR] Consulta {measure} en Influx 2 falló: {e}")
            results[measure] = pd.DataFrame()

    return results

def merge_data(dict_data):
    def fix_time(df):
        if '_time' in df.columns:
            df.rename(columns={'_time': 'time'}, inplace=True)
        df['time'] = pd.to_datetime(df['time'], errors='coerce')
        return df

    dfs = [fix_time(df) for df in dict_data.values() if not df.empty]
    if not dfs:
        logger.warning("No hay DataFrames válidos para combinar")
        return pd.DataFrame()
    df_combined = reduce(lambda left, right: pd.merge(left, right, on="time", how="outer"), dfs)
    df_combined.drop(columns=[col for col in df_combined.columns if "time" in col and col != "time"], inplace=True, errors='ignore')

    logger.info(f"DataFrames combinados en un único DataFrame con shape {df_combined.shape}")
    return df_combined

