# visualization.py

"""
Módulo para la visualización de datos.
Contiene funciones para crear gráficos con Matplotlib y Seaborn.
"""
# src/visualization.py

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import List
import numpy as np

def plot_time_series(df: pd.DataFrame, time_col: str, value_cols: List[str],
                     title: str = "Serie de Tiempo", xlabel: str = "Tiempo", ylabel: str = "Valor") -> plt.Figure:
    """
    Genera un gráfico de series de tiempo para una o varias columnas.
    
    Se asegura de que la columna de tiempo esté en formato datetime.

    Args:
        df (pd.DataFrame): DataFrame con los datos.
        time_col (str): Columna que contiene las fechas/horas.
        value_cols (List[str]): Lista de columnas a graficar.
        title (str): Título del gráfico.
        xlabel (str): Etiqueta del eje X.
        ylabel (str): Etiqueta del eje Y.

    Returns:
        plt.Figure: La figura generada.
    """
    # Convertir la columna de tiempo a datetime si es necesario
    if not pd.api.types.is_datetime64_any_dtype(df[time_col]):
        df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
    
    df = df.sort_values(time_col)
    
    plt.figure(figsize=(15, 8))
    for col in value_cols:
        if col in df.columns:
            plt.plot(df[time_col], df[col], label=col)
        else:
            print(f"Advertencia: La columna '{col}' no se encuentra en el DataFrame.")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True)
    fig = plt.gcf()
    return fig

def plot_fourier(freqs: np.ndarray, power: np.ndarray,
                 title: str = "Espectro de Fourier", xlabel: str = "Frecuencia", ylabel: str = "Amplitud") -> plt.Figure:
    """
    Genera el gráfico del espectro de Fourier.

    Args:
        freqs (np.ndarray): Array de frecuencias.
        power (np.ndarray): Espectro de potencia.
        title (str): Título del gráfico.
        xlabel (str): Etiqueta del eje X.
        ylabel (str): Etiqueta del eje Y.

    Returns:
        plt.Figure: La figura generada.
    """
    plt.figure(figsize=(15, 8))
    plt.plot(freqs, power)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    return plt.gcf()

import numpy as np
from typing import List

def plot_time_series(df: pd.DataFrame, time_col: str, value_cols: List[str],
                     title: str = "Serie de Tiempo", xlabel: str = "Tiempo", ylabel: str = "Valor",
                     save_path=None, subplots=False) -> plt.Figure:
    if not pd.api.types.is_datetime64_any_dtype(df[time_col]):
        df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
    df = df.sort_values(time_col)
    fig, ax = plt.subplots(figsize=(15, 8))

    if subplots:
        for i, col in enumerate(value_cols):
            plt.subplot(len(value_cols), 1, i + 1)
            plt.plot(df[time_col], df[col])
            plt.title(col)
            plt.grid(True)
    else:
        for col in value_cols:
            if col in df.columns:
                ax.plot(df[time_col], df[col], label=col)
            else:
                print(f"Advertencia: La columna '{col}' no se encuentra en el DataFrame.")
        ax.legend()

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True)
    return fig

def plot_boxplot(df, cols, title="Distribución de variables"):
    fig, ax = plt.subplots(figsize=(15, 6))
    sns.boxplot(data=df[cols], ax=ax)
    ax.set_title(title)
    ax.grid(True)
    return fig

def plot_histogram(df, col, bins=50):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(df[col].dropna(), bins=bins, alpha=0.7)
    ax.set_title(f"Histograma de {col}")
    ax.grid(True)
    return fig

def plot_multiple_series(df, time_col, value_groups):
    figures = []
    for title, cols in value_groups.items():
        fig, ax = plt.subplots(figsize=(15, 6))
        for col in cols:
            if col in df.columns:
                ax.plot(df[time_col], df[col], label=col)
        ax.set_title(title)
        ax.set_xlabel("Tiempo")
        ax.set_ylabel("Magnitud")
        ax.legend()
        ax.grid(True)
        figures.append((title, fig))
    return figures