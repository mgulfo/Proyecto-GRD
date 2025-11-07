# data_cleaning.py
# src/data_processing/data_cleaning.py

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
    cols_to_scale = [col for col in numeric_cols if col not in ['PowF_T_Ins']]

    # Aplicar StandardScaler solo a las columnas seleccionadas
    scaler = StandardScaler()
    df_copy[cols_to_scale] = scaler.fit_transform(df_copy[cols_to_scale])

    return df_copy

from utils.logger import logger
from sklearn.preprocessing import StandardScaler

def remove_outliers_zscore(df, threshold=3):
    """
    Elimina outliers en base al Z-score.
    """
    return df[(np.abs((df - df.mean()) / df.std()) < threshold).all(axis=1)]

def preprocess_data2(df: pd.DataFrame) -> pd.DataFrame:
    # Eliminar duplicados por columna time
    if 'time' in df.columns:
        before_dup = len(df)
        df.drop_duplicates(subset='time', inplace=True)
        logger.info(f"Eliminadas {before_dup - len(df)} filas duplicadas por 'time'")

    # Eliminar nulos
    before_rows = len(df)
    df = df.dropna(how='any')
    after_rows = len(df)
    logger.info(f"Se eliminaron {before_rows - after_rows} filas con valores nulos")

    # Eliminar columnas duplicadas
    df = df.loc[:, ~df.columns.duplicated()]
    return df

def preprocess_data(df: pd.DataFrame, silenciar_logs: bool = False) -> pd.DataFrame:
    df = df.copy()
    
    if not silenciar_logs:
        logger.info("===== INICIO DEL PREPROCESAMIENTO =====")
        logger.info(f"Shape original: {df.shape}")

    # Diagnóstico inicial
    null_counts = df.isnull().sum()
    if not silenciar_logs:
        if null_counts.any():
            logger.info("Valores nulos por columna:\n" + str(null_counts[null_counts > 0]))
        else:
            logger.info("No se encontraron valores nulos.")

    # Eliminar duplicados por 'time'
    if 'time' in df.columns:
        before_dup = len(df)
        df.drop_duplicates(subset='time', inplace=True)
        if not silenciar_logs:
            logger.info(f"Eliminadas {before_dup - len(df)} filas duplicadas por 'time'")

    # Eliminar columnas duplicadas
    before_cols = df.shape[1]
    df = df.loc[:, ~df.columns.duplicated()]
    if not silenciar_logs:
        logger.info(f"Eliminadas {before_cols - df.shape[1]} columnas duplicadas")

    # Eliminar filas con al menos un NaN
    before_rows = len(df)
    df = df.dropna(how='any')
    after_rows = len(df)
    filas_eliminadas = before_rows - after_rows
    pct_eliminadas = (filas_eliminadas / before_rows * 100) if before_rows > 0 else 0
    if not silenciar_logs:
        logger.info(f"Eliminadas {filas_eliminadas} filas con valores nulos ({pct_eliminadas:.2f}%)")

    # Detección de outliers con z-score
    zscore_threshold = 3
    outlier_counts = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    for col in numeric_cols:
        z_scores = np.abs((df[col] - df[col].mean()) / df[col].std(ddof=0))
        outliers = z_scores > zscore_threshold
        count = np.sum(outliers)
        if count > 0:
            outlier_counts[col] = count
            if not silenciar_logs:
                logger.warning(f"Outliers detectados en '{col}': {count} valores (z-score > {zscore_threshold})")

    # Resumen final
    if not silenciar_logs:
        logger.info(f"Shape final: {df.shape}")
        if outlier_counts:
            logger.info("Resumen columnas con outliers:")
            for col, count in outlier_counts.items():
                logger.info(f" - {col}: {count} valores extremos detectados")
        else:
            logger.info("No se detectaron outliers significativos según z-score > 3.")
        if not silenciar_logs:
            logger.info("===== FIN DEL PREPROCESAMIENTO =====")

    return df

def normalize_all_numeric(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if numeric_cols.empty:
        logger.warning("No se encontraron columnas numéricas para normalizar")
        return df
    df[numeric_cols] = (df[numeric_cols] - df[numeric_cols].min()) / (df[numeric_cols].max() - df[numeric_cols].min())
    logger.info(f"Se normalizaron las columnas: {list(numeric_cols)}")
    return df


def clean_influx2_meta(df):
    """
    Limpia columnas meta innecesarias de InfluxDB 2.7 y renombra _time.
    """
    cols_to_drop = ["_start", "_stop", "result", "table", "_measurement",
                    "device", "location", "name", "type", "slave_id", "valuetype"]
    df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True, errors="ignore")
    if "_time" in df.columns:
        df.rename(columns={"_time": "time"}, inplace=True)
    return df
