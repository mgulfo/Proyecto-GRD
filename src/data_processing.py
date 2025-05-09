# data_processing.py

"""
Módulo para el procesamiento y transformación de datos.
Incluye funciones de limpieza, normalización y combinación de DataFrames.
"""

import pandas as pd
import numpy as np

def apply_rolling_norm(series, window):
    """
    Aplica la normalización mediante media móvil y desviación estándar a una serie.

    Args:
        series (pd.Series): Serie de datos.
        window (int): Tamaño de la ventana para el cálculo.

    Returns:
        tuple: Serie normalizada (media móvil) y serie de desviación estándar.
    """
    norm = series.rolling(window).mean()
    std = series.rolling(window).std()
    return norm, std

def apply_rolling_norm_trif(s1, s2, s3, window):
    """
    Aplica la normalización a tres series de manera simultánea.

    Args:
        s1, s2, s3 (pd.Series): Series de datos.
        window (int): Tamaño de la ventana.

    Returns:
        tuple: (norm1, norm2, norm3, std1, std2, std3)
    """
    norm1, std1 = apply_rolling_norm(s1, window)
    norm2, std2 = apply_rolling_norm(s2, window)
    norm3, std3 = apply_rolling_norm(s3, window)
    return norm1, norm2, norm3, std1, std2, std3

def merge_dataframes(dfs, on='time'):
    """
    Une una lista de DataFrames por la columna indicada.

    Args:
        dfs (list): Lista de DataFrames.
        on (str): Columna clave para la unión.

    Returns:
        pd.DataFrame: DataFrame resultante de la unión.
    """
    from functools import reduce
    return reduce(lambda left, right: pd.merge(left, right, on=on, how='outer'), dfs)

def clean_dataframe(df):
    """
    Realiza la limpieza del DataFrame, eliminando filas con NaN y outliers simples.

    Args:
        df (pd.DataFrame): DataFrame a limpiar.

    Returns:
        pd.DataFrame: DataFrame limpio.
    """
    # Ejemplo: eliminar filas con NaN
    df_clean = df.dropna()
    # Aquí se pueden incluir más filtros para outliers según el caso
    return df_clean

def clean_influx2_meta(df):
    """
    Elimina columnas meta innecesarias y renombra '_time' a 'time', si existe.
    """
    # Lista de columnas meta que no quieres conservar
    cols_to_drop = [
        "_start", "_stop", "result", "table", "_measurement",
        "device", "location", "name", "type", "slave_id", "valuetype"
    ]
    # Eliminamos esas columnas si existen en el DataFrame
    df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True, errors="ignore")
    
    # Renombrar '_time' a 'time'
    if "_time" in df.columns:
        df.rename(columns={"_time": "time"}, inplace=True)
    
    return df

# data_processing.py
from sklearn.preprocessing import StandardScaler

def normalize_all_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica StandardScaler a todas las columnas numéricas de un DataFrame,
    dejando intactas las columnas no numéricas (por ejemplo, 'time').

    Retorna un nuevo DataFrame con las columnas numéricas escaladas.
    """
    df_copy = df.copy()
    # Identificar columnas numéricas (float o int) que no sean la columna 'time'
    numeric_cols = df_copy.select_dtypes(include=[float, int]).columns
    
    # Ajustar y transformar
    scaler = StandardScaler()
    df_copy[numeric_cols] = scaler.fit_transform(df_copy[numeric_cols])
    
    return df_copy
