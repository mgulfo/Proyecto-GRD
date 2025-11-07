# utils.py

"""
Módulo de utilidades generales.
Incluye funciones auxiliares que pueden ser reutilizadas en distintos módulos.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
import pytz
from config import LOCAL_TIMEZONE

def convert_utc_to_local(utc_date_str, fmt="%Y-%m-%dT%H:%M:%SZ"):
    """
    Convierte una fecha en formato UTC a la zona local definida en la configuración.

    Args:
        utc_date_str (str): Fecha en formato UTC.
        fmt (str): Formato de la fecha.

    Returns:
        datetime: Fecha convertida a la zona local.
    """
    utc_dt = datetime.strptime(utc_date_str, fmt)
    utc_dt = pytz.utc.localize(utc_dt)
    local_tz = pytz.timezone(LOCAL_TIMEZONE)
    return utc_dt.astimezone(local_tz)

import pandas as pd

def convert_df_utc_to_local(df, time_column='time'):
    if time_column in df.columns:
        df[time_column] = pd.to_datetime(df[time_column], errors="coerce")

        # Solo si no tiene zona horaria, la asumimos UTC
        if df[time_column].dt.tz is None:
            df[time_column] = df[time_column].dt.tz_localize("UTC")

        df[time_column] = df[time_column].dt.tz_convert(LOCAL_TIMEZONE)
        df[time_column] = df[time_column].dt.tz_localize(None)
    return df

import os
import json
from datetime import datetime
import pandas as pd

def save_normalization_stats(df, output_path="data/stats/normalization_stats.json"):
    """Guarda la media y desviación estándar de columnas numéricas."""
    stats = {}
    for col in df.select_dtypes(include='number').columns:
        stats[col] = {
            "mean": df[col].mean(),
            "std": df[col].std()
        }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(stats, f, indent=4)

    print(f"[✓] Estadísticas de normalización guardadas en {output_path}")

def quality_report(df, output_path=None):
    """Genera un reporte de calidad del DataFrame y lo guarda como .txt"""
    report_lines = []
    report_lines.append("📋 QUALITY REPORT")
    report_lines.append("=" * 50)
    report_lines.append(f"Total filas: {df.shape[0]}")
    report_lines.append(f"Total columnas: {df.shape[1]}\n")

    # Nulos
    report_lines.append("🔍 Porcentaje de nulos por columna:")
    nulls = df.isnull().mean() * 100
    report_lines += [f"{col}: {val:.2f}%" for col, val in nulls.items()]
    
    # Outliers por IQR
    report_lines.append("\n⚠️ Outliers detectados (1.5 * IQR):")
    for col in df.select_dtypes(include='number').columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        outliers = df[(df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)]
        report_lines.append(f"{col}: {len(outliers)} outliers")

    # Gaps temporales si hay columna 'time'
    if 'time' in df.columns:
        try:
            df_sorted = df.sort_values('time')
            time_diffs = pd.to_datetime(df_sorted['time']).diff().dropna()
            gap_stats = time_diffs.value_counts().sort_index()
            report_lines.append("\n⏱ Gaps temporales:")
            for delta, count in gap_stats.items():
                report_lines.append(f"{delta}: {count} veces")
        except Exception as e:
            report_lines.append(f"\n[!] Error al analizar gaps temporales: {e}")
    
    # Guardado
    if output_path is None:
        now = datetime.now().strftime("%Y-%m-%d_%H-%M")
        output_path = f"data/stats/quality_report_{now}.txt"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"[✓] Quality report guardado en {output_path}")

def hora_local_a_utc(fecha_local_str):
    """Convierte string local (ej: '2024-11-01T00:00:00') a string UTC '2024-10-31T21:00:00Z'"""
    local = pytz.timezone(LOCAL_TIMEZONE)
    dt_local = local.localize(datetime.fromisoformat(fecha_local_str))
    dt_utc = dt_local.astimezone(pytz.utc)
    return dt_utc.strftime('%Y-%m-%dT%H:%M:%SZ')