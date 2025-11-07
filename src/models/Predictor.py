import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from sklearn.model_selection import train_test_split
from keras import Model
from keras import models
from keras import Sequential
from keras import *
from keras import layers, losses, callbacks, metrics, optimizers
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
#import trend_analysis as tendencias
import seaborn as sns
import warnings

USAR_TRENDS = 0
freq = 8640
def escalar_datos(x):
    df = x.copy()
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if numeric_cols.empty:
        print("No se encontraron columnas numéricas para normalizar")
        return df
    df[numeric_cols] = (df[numeric_cols] - df[numeric_cols].min()) / (df[numeric_cols].max() - df[numeric_cols].min())
    print(f"Se normalizaron las columnas: {list(numeric_cols)}")
    return df
def desescalar_datos(x, y):
    df = x.copy()
    df_ini = y.copy()
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if numeric_cols.empty:
        print("No se encontraron columnas numéricas para normalizar")
        return df
    df[numeric_cols] = (df[numeric_cols] * (df_ini[numeric_cols].max() - df_ini[numeric_cols].min()) + df_ini[numeric_cols].min())
    print(f"Se normalizaron las columnas: {list(numeric_cols)}")
    return df
def split_train_data(y,n,m):
    # generate the training sequences
    #print("iniciando split")
    X, Y = [], []
    np.array(Y)
    for i in range(len(y)-n-1):
        a = y[i:(i+n)]
        if len(y[i + n:i+n+m]) == m:
            X.append(a)
            Y.append(y[i + n:i+n+m])
    _x = np.array(X)
    _y = np.array(Y)
    #print(_x.shape)
    #print(_y.shape)
    return _x, _y
def split_train_data_multi(y,n,m):
    _x,_y = [],[]
    print(len(y))
    print(m)
    print("Forma:")
    print(y.shape)
    print("Fin")
    for i in range(m, n+m):
        _x.append(y[i-m:i]) 
        _y.append(y[i:i+n]) 
    return np.array(_x), np.array(_y)
def modelo_lstm(x,y,nf,lp,nombre_columna):
    #print("iniciando modelo")
    x = np.reshape(x, (x.shape[0], 1, x.shape[1]))
    #print(x.shape)
    #print(y.shape)
    model = Sequential()
    model.add(layers.LSTM(60, return_sequences=True, input_shape=(1,lp)))
    model.add(layers.LSTM(60,return_sequences=False,))
    model.add(layers.Dense(nf))
    model.compile(loss='mse', optimizer='adam') 
    model.fit(x, y, epochs=120, batch_size=12, validation_split=0.3, verbose=0)   
    #print("compilado")
    model.summary()
    # generate the multi-step forecasts
    n_future = nf
    # generate the forecasts
    X_ = y[- lp:]  # last available input sequence
    #print(X_.shape)      
    #print("ya pasamos lazo")
    X_ = X_.reshape(lp, 1, lp) 
    #print(X_.shape)      
    # transform the forecasts back to the original scale
    Y_ = model.predict(X_, verbose=0)
    nom = nombre_columna + '.keras'
    model.save(nom)
    row_copy = Y_[0,:].copy()
    #print(row_copy)
    y_future = row_copy    
    return y_future
def modelo_multi_lstm(x,y,nf,lp):
    #print("iniciando modelo")
    n = x.shape[0]
    x = np.reshape(x, (x.shape[0], 1, x.shape[1]))    
    print(x.shape)
    print(y.shape)
    model = Sequential()
    model.add(layers.LSTM(60, return_sequences=True, input_shape=(lp, x.shape[0])))
    model.add(layers.LSTM(60,return_sequences=False,))
    model.add(layers.Dense(nf))
    model.compile(loss='mse', optimizer='adam') 
    model.fit(x, y, epochs=120, batch_size=12, validation_split=0.3, verbose=0)   
    #print("compilado")
    model.summary()
    # generate the multi-step forecasts
    n_future = nf
    # generate the forecasts
    X_ = y[- lp:]  # last available input sequence
    #print(X_.shape)      
    #print("ya pasamos lazo")
    X_ = X_.reshape(lp, 1, lp) 
    #print(X_.shape)      
    # transform the forecasts back to the original scale
    Y_ = model.predict(X_, verbose=0)
    nom = "Multi_LSTM_Potencias" + '.keras'
    model.save(nom)
    row_copy = Y_[0,:].copy()
    #print(row_copy)
    y_future = row_copy    
    return y_future
def correr_modelo(data, nombre_columna):
    nom = nombre_columna + '.keras'
    model = Model.load_model(nom)    
    return data
def correr_predictor(data, nfut, nombre_columna):
    lp = 60 #4 veces el forecast hacia atras
    x, y = split_train_data(data,nfut,lp)
    res = modelo_lstm(x,y,nfut,lp,nombre_columna)
    return res    
def gen_prediccion(df, nfut, train_run, multi):
    df_copy = df.iloc[:0,:].copy() 
    df_x = escalar_datos(df)
    j = 0
    if train_run: 
        if multi:
            df_y = df_x[['PowA_L1_Ins', 'PowA_L2_Ins', 'PowA_L3_Ins']].copy()
            x, y = split_train_data_multi(df_y,nfut,60)
            res = modelo_multi_lstm(x,y,nfut,60)
            df_copy['PowA_L1_Ins'] = [res[0]]
            df_copy['PowA_L2_Ins'] = [res[1]]
            df_copy['PowA_L3_Ins'] = [res[2]]    
        else:    
            for columns in df:
                if columns != 'time':
                    df_copy[columns] = correr_predictor(df_x[columns], nfut, columns)
                    j = j + 1
    else:
        if multi:
            df_copy = correr_modelo(df_x, 'Multi_LSTM_Potencias')
        else:
            for columns in df:
                if columns != 'time':
                    df_copy[columns] = correr_modelo(df_x[columns], columns)
                    j = j + 1
    df_res = desescalar_datos(df_copy,df)
    return df_res
'''
def usar_trends(data, periodo):
    t,s,r = tendencias.decompose_series(data, periodo)
    return t,s,r
'''