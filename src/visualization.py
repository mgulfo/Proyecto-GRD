# visualization.py

"""
Módulo para la visualización de datos.
Contiene funciones para crear gráficos con Matplotlib y Seaborn.
"""

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

# ----------------------------------------
# 🔹 Subplots para variables por fase (línea)
# ----------------------------------------
def plot_variable_por_fase(df, variable_base, title_prefix="Variable por Fase", ylabel="Valor"):
    fases = ['L1', 'L2', 'L3']
    fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(15, 10), sharex=True)
    for i, fase in enumerate(fases):
        col = f"{variable_base}_{fase}_Ins"
        axes[i].plot(df["time"], df[col], label=col)
        axes[i].set_title(f"{title_prefix} - {fase}")
        axes[i].set_ylabel(ylabel)
        axes[i].legend()
        axes[i].grid(True)
    axes[-1].set_xlabel("Tiempo")
    fig.tight_layout()
    return fig

# 🔹 FP + Potencia por fase (líneas)
def plot_fp_y_potencia(df, fase, title_prefix="FP y Potencia"):
    col_fp = "PowF_T_Ins"
    col_pot = f"PowA_{fase}_Ins"
    fig, ax1 = plt.subplots(figsize=(15, 6))

    ax1.plot(df["time"], df[col_pot], color='tab:blue', label=f"Potencia Activa {fase}")
    ax1.set_ylabel("Potencia (kW)", color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    ax2 = ax1.twinx()
    ax2.plot(df["time"], df[col_fp], color='tab:red', label="Factor de Potencia")
    ax2.set_ylabel("FP", color='tab:red')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    fig.suptitle(f"{title_prefix} - {fase}")
    fig.tight_layout()
    return fig

# 🔹 FP + Tensión por fase (líneas)
def plot_fp_y_tension(df, fase, title_prefix="FP y Tensión RMS"):
    col_fp = "PowF_T_Ins"
    col_v = f"Vrms_{fase}_Ins"
    fig, ax1 = plt.subplots(figsize=(15, 6))

    ax1.plot(df["time"], df[col_v], color='tab:green', label=f"Tensión RMS {fase}")
    ax1.set_ylabel("Tensión (V)", color='tab:green')
    ax1.tick_params(axis='y', labelcolor='tab:green')

    ax2 = ax1.twinx()
    ax2.plot(df["time"], df[col_fp], color='tab:red', label="Factor de Potencia")
    ax2.set_ylabel("FP", color='tab:red')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    fig.suptitle(f"{title_prefix} - {fase}")
    fig.tight_layout()
    return fig

# 🔹 Variable por fase (Vrms, Irms, PowA, THDI, THDV)
def plot_variable_por_fase(df, variable_base, title_prefix="Variable por Fase", ylabel="Valor"):
    fases = ['L1', 'L2', 'L3']
    fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(15, 10), sharex=True)
    for i, fase in enumerate(fases):
        col = f"{variable_base}_{fase}_Ins"
        axes[i].plot(df["time"], df[col], label=col)
        axes[i].set_title(f"{title_prefix} - {fase}")
        axes[i].set_ylabel(ylabel)
        axes[i].legend()
        axes[i].grid(True)
    axes[-1].set_xlabel("Tiempo")
    fig.tight_layout()
    return fig

# 🔹 FP total (línea)
def plot_fp_total_line(df, title="Factor de Potencia Total en el Tiempo"):
    fig, ax = plt.subplots(figsize=(15, 6))
    ax.plot(df["time"], df["PowF_T_Ins"], label="FP Total", color='tab:blue')
    ax.set_title(title)
    ax.set_xlabel("Tiempo")
    ax.set_ylabel("FP")
    ax.grid(True)
    ax.legend()
    return fig

def plot_fp_vs_variable_separados(df, variable_prefix, variable_label, ylabel, fases):
    figs = []
    for fase in fases:
        col_var = f"{variable_prefix}_{fase}_Ins"
        if 'PowF_T_Ins' in df.columns and col_var in df.columns:
            fig, axs = plt.subplots(2, 1, figsize=(15, 8), sharex=True)

            axs[0].plot(df['time'], df['PowF_T_Ins'], label='FP Total', color='tab:blue')
            axs[0].set_ylabel('FP Total')
            axs[0].set_title(f'Factor de Potencia vs {variable_label} {fase}')
            axs[0].legend()
            axs[0].grid(True)

            axs[1].plot(df['time'], df[col_var], label=f'{variable_label} {fase}', color='tab:orange')
            axs[1].set_ylabel(ylabel)
            axs[1].set_xlabel('Tiempo')
            axs[1].legend()
            axs[1].grid(True)

            fig.tight_layout()
            figs.append((fase, fig))
    return figs

def plot_thd_vs_variable_separados(df, thd_prefix, variable_prefix, variable_label, ylabel, fases):
    figs = []
    for fase in fases:
        col_thd = f"{thd_prefix}_{fase}_Ins"
        col_var = f"{variable_prefix}_{fase}_Ins"
        if col_thd in df.columns and col_var in df.columns:
            fig, axs = plt.subplots(2, 1, figsize=(15, 8), sharex=True)

            axs[0].plot(df['time'], df[col_thd], label=f'THD {fase}', color='tab:red')
            axs[0].set_ylabel(f'THD {fase} (%)')
            axs[0].set_title(f'THD {fase} vs {variable_label} {fase}')
            axs[0].legend()
            axs[0].grid(True)

            axs[1].plot(df['time'], df[col_var], label=f'{variable_label} {fase}', color='tab:green')
            axs[1].set_ylabel(ylabel)
            axs[1].set_xlabel('Tiempo')
            axs[1].legend()
            axs[1].grid(True)

            fig.tight_layout()
            figs.append((fase, fig))
    return figs

def filtrar_por_rango_fecha(df, fecha_inicio, fecha_fin):
    """Filtra un DataFrame entre dos fechas."""
    return df[(df["time"] >= pd.to_datetime(fecha_inicio)) & (df["time"] <= pd.to_datetime(fecha_fin))]




