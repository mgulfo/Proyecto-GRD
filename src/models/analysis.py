# analysis.py
"""
Módulo para realizar análisis de series temporales.
Incluye funciones para descomponer la serie en tendencia, estacionalidad y residuo,
así como para aplicar transformadas de Fourier.
"""

import numpy as np
import pandas as pd
import os
from statsmodels.tsa.seasonal import seasonal_decompose
from utils.logger import logger
from datetime import datetime, timedelta


def leer_cammessa_csv():
    x = pd.read_csv(os.path.dirname(__file__)+"\\Cammesa_res.csv",encoding='latin1',on_bad_lines='skip',sep=';', header=0)   
    for col in x.columns:
        print(col)    
    y = x[['Fecha','AUTO+GUMAs','DEMANDA DISTRIBUIDOR','ALIMENTACIÓN. COMERCIOS Y SERVICIOS','INDUSTRIAS']]
    #y = y.set_index('Fecha')    
    return y
def asociar_datos_energia(df_cam, mes, anio):    
    df_cam['Fecha'] = pd.to_datetime(df_cam.Fecha, format='%d/%m/%Y')
    df_cam['Fecha'] = pd.to_datetime(df_cam['Fecha'].dt.strftime('%Y-%m-%d'))
    #print(df_cam.head())
    df_res = df_cam[(df_cam['Fecha'].dt.month < mes) & (df_cam['Fecha'].dt.year == anio)]  
    return df_res
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
#Convertir esta funcion en retorno de vector hecho en microcortes
def f(Y, N,M):
    total = 0
    ret = []
    '''
    L = len(Y)
    for x in range(N):
        total = 0
        c = 0
        for yy in Y:
            c=c+1
            #Pasar a funcion con un vector definido de N,L para calular todos los coeficientes y multiplicarlos por yy y sumar las columnas (producto matriz x elemnto)
            total = total + (yy * (np.cos(x*c*2*np.pi/N) + 1j*np.sin(x*c*2*np.pi/N)))
        a =  np.real(total)
        ret.append(a)'''
    for i in range(M):
        a = N[:,i]
        total = np.dot(Y,a)
    print(total)
    ret.append(np.real(total))
    return ret
def calcular_matriz(n,l):
    x = np.zeros(shape = (n,l))
    for i in range(l):
        for j in range(n):
            x[j,i] = np.cos(i*j*2*np.pi/n) + 1j*np.sin(i*j*2*np.pi/n)
    return x
def fourier_trends(t,s,r,m,fr):
    pt,kt = fourier_analysis(t)
    ps,ks = fourier_analysis(s)
    pr,kr = fourier_analysis(r)
    logger.info("Analizado")
    M = m
    X = calcular_matriz(fr,M)
    logger.info("MATRIZ CALCULADA")
    logger.info(f"Frecuencia: {fr}")
    pp = kt[:fr]
    y1 = f(pp,X,M)
    logger.info("y1")
    pp = ks[:fr]
    y2 = f(pp,X,M)
    logger.info("y2")
    pp = kr[:fr]
    y3 = f(pp,X,M)
    logger.info("y3")  
    yfin = np.add(np.array(y1),np.array(y2),np.array(y3))    