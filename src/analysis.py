# analysis.py
"""
Módulo para realizar análisis de series temporales.
Incluye funciones para descomponer la serie en tendencia, estacionalidad y residuo,
así como para aplicar transformadas de Fourier.
"""

import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose

def decompose_series(data_series, period):
    """
    Descompone una serie temporal en tendencia, estacionalidad y residuo.

    Args:
        data_series (pd.Series): Serie temporal a descomponer.
        period (int): Período para la descomposición.

    Returns:
        DecomposeResult: Objeto con los componentes de la serie.
    """
    decomposition = seasonal_decompose(data_series, model='additive', period=period, extrapolate_trend='freq')
    return decomposition

def fourier_analysis(data_series, fs=1):
    """
    Realiza un análisis de Fourier a la serie de tiempo.

    Args:
        data_series (pd.Series): Serie temporal.
        fs (float): Frecuencia de muestreo.

    Returns:
        tuple: Frecuencias y espectro de potencia.
    """
    n = len(data_series)
    fft_vals = np.fft.fft(data_series) / n
    freqs = np.fft.fftfreq(n, d=1/fs)
    power_spectrum = np.abs(fft_vals)
    return freqs, power_spectrum
