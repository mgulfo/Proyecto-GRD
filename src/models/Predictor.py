import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # Oculta alertas innecesarias
import tensorflow as tf
tf.config.threading.set_intra_op_parallelism_threads(1)
tf.config.threading.set_inter_op_parallelism_threads(1)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from datetime import datetime, timezone, timedelta
import pytz
import time
from utils.utils import convert_utc_to_local
from utils.logger import logger
from sklearn.model_selection import train_test_split
from keras import Model
from keras import models
from keras import Sequential
from keras import *
from keras import layers, losses, callbacks, metrics, optimizers
from keras.layers import RepeatVector, TimeDistributed
from keras.layers import Reshape
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error
from math import sqrt
#import trend_analysis as tendencias
import seaborn as sns
import warnings
from query_engine import subir_prediccion_influxdb_v2
from config import OUTPUT_DIR, UNITS, PASOS, freq, USAR_TRENDS, LISTA_DATOS_PREDICCION
from query_engine import busqueda_influx2, merge_data, obtener_ultimo_dato_dataframe
#from config2 import OUTPUT_DIR, MAX_ST, VISUALIZAR_MAE, LOCAL_TIMEZONE
from utils.utils import convert_utc_to_local
#lista_datos = ['Irms_L1_Ins', 'Irms_L2_Ins', 'Irms_L3_Ins','PowA_L1_Ins', 'PowA_L2_Ins', 'PowA_L3_Ins','PowF_T_Ins']
lista_datos = LISTA_DATOS_PREDICCION.split(",") if LISTA_DATOS_PREDICCION else []
def create_future_dates_column(ultima_fecha, timesteps, frequency):
    time_column_data = pd.date_range(start=ultima_fecha, periods=timesteps, freq=frequency)
    # Create a DataFrame with the new time column
    df = pd.DataFrame({'time': time_column_data})
    return df
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
    X, Y = [], []
    # Iteramos desde el primer punto hasta donde podamos tomar 30 de entrada + 60 de salida
    for i in range(len(y) - n - m  + 1):
        # Secuencia de Entrada (X): Desde 'i' hasta 'i + n_input'
        seq_x = y[i:(i + n)]
        # Secuencia de Salida (y): Desde 'i + n_input' hasta 'i + n_input + n_out'
        seq_y = y[(i + n):(i + n + m)]
        X.append(seq_x)
        Y.append(seq_y)
    return np.array(X), np.array(Y)    
def modelo_lstm(x,y,nf,lp,nombre_columna):
    x = np.reshape(x, (x.shape[0], 1, x.shape[1]))
    model = Sequential()
    model.add(layers.LSTM(128, return_sequences=True, input_shape=(1,lp))) #generalizar 2 parametro numero de features
    model.add(layers.LSTM(64,return_sequences=False,))
    model.add(layers.Dense(nf))
    model.compile(loss='mse', optimizer='adam') 
    model.fit(x, y, epochs=100, batch_size=32, validation_split=0.5, verbose=0)   
    #print("compilado")
    model.summary()
    # generate the multi-step forecasts
    n_future = nf
    # generate the forecasts
    print(y.shape)
    X_i = y[-lp:]  # last available input sequence
    #print(X_.shape)      
    #print("ya pasamos lazo")
    X_i = X_i.reshape(lp, 1, lp) 
    #print(X_.shape)      
    # transform the forecasts back to the original scale
    Y_ = model.predict(X_i, verbose=0)
    nom = nombre_columna + '.keras'
    model.save(nom)
    row_copy = Y_[0,:].copy()
    #print(row_copy)
    y_future = row_copy    
    return y_future
def modelo_multi_lstm(x,y,nf,lp, medidor):
    total_samples = x.shape[0] 
    # Dividir los datos manteniendo el orden cronológico
    tf.keras.backend.clear_session()
    NCOLUMNAS = x.shape[2]
    print(NCOLUMNAS)
    train_sample = int(0.5* total_samples)    
    X_train = x[:train_sample]
    y_train = y[:train_sample]

    X_test = x[train_sample:]
    y_test = y[train_sample:]
    _activation='sigmoid'
    #_activation='tanh'
    # Verificar las dimensiones finales de los conjuntos
    print("\n--- Dimensiones de los conjuntos de datos ---")
    print(f"X_train shape: {X_train.shape} | y_train shape: {y_train.shape}")
    print(f"X_test shape: {X_test.shape}   | y_test shape: {y_test.shape}")
    # Definir el Codificador (Encoder)
    
    encoder_inputs = tf.keras.Input(shape=(lp, NCOLUMNAS))
    encoder_lstm1 = layers.LSTM(units=UNITS, activation=_activation, return_sequences=True,return_state=True) # units=100 es un hiperparámetro
    encoder_outputs1, state_h1, state_c1 = encoder_lstm1(encoder_inputs)   
    encoder_lstm2 = layers.LSTM(units=UNITS, activation=_activation,return_sequences=False, return_state=True) # units=100 es un hiperparámetro
    encoder_outputs2, state_h2, state_c2 = encoder_lstm2(encoder_outputs1)
    # Definir el Decodificador (Decoder)
    decoder_inputs = RepeatVector(nf)(encoder_outputs2) # Repite el vector de contexto n_out veces
    decoder_lstm1 = layers.LSTM(units=UNITS, activation=_activation, return_sequences=True)
    decoder_outputs1 = decoder_lstm1(decoder_inputs, initial_state=[state_h1, state_c1])
    decoder_lstm2 = layers.LSTM(units=UNITS, activation=_activation, return_sequences=True)
    decoder_outputs2 = decoder_lstm2(decoder_outputs1)
   # return_sequences=True es crucial para obtener una salida por cada paso de tiempo
    # Capa de salida TimeDistributed para predecir las N variables en cada paso de tiempo futuro
    '''
    decoder_dense = TimeDistributed(layers.Dense(NCOLUMNAS, activation = 'linear'))(decoder_outputs2)
    '''
    #Calculamos el total de salidas futuras de un solo golpe (60 pasos * 7 columnas = 420 neuronas)
    TOTAL_SALIDAS_FUTURAS = nf * NCOLUMNAS
    capa_densa_futuro = layers.Dense(TOTAL_SALIDAS_FUTURAS, activation='linear')(encoder_outputs2)
    # Reformamos la salida lineal para que vuelva a tener la estructura (60, 7) 
    salida_reformada = Reshape((nf, NCOLUMNAS))(capa_densa_futuro)
    print(salida_reformada.shape)
    # Definir el modelo completo usando la API Funcional
    model = Model(inputs=encoder_inputs, outputs=salida_reformada)
    model.compile(optimizer='adam', loss='mae') # mse es común para regresión
    print(model.summary())

    # --- PASO 4: Entrenar el modelo ---
    model.fit(X_train, y_train, epochs=80, batch_size=60, verbose=0) #, validation_data=(X_test, y_test) quitado por vel en pc
    # Predicción
    # Predeciremos la secuencia futura de los últimos datos disponibles en el conjunto de prueba
    # Tomamos la última muestra del conjunto X_test
    input_sequence = X_test[-1:]
    actual_value = y_test[-1]
    prediction_scaled = model.predict(input_sequence, verbose=0)
    y_pred = np.squeeze(prediction_scaled,axis = 0)
    print(f'Forma de la predicción: {y_pred.shape}')
    print(f'Forma de los valores a comparar: {actual_value.shape}') 
    # Calcular métricas (ej. RMSE y MAE para la última muestra)
    #print(y_pred)
    rmse = sqrt(mean_squared_error(actual_value, y_pred))
    mae = mean_absolute_error(actual_value, y_pred)
    print(f'RMSE de la predicción: {rmse}')
    print(f'MAE de la predicción: {mae}')
    datos_reformados = y_pred.reshape(nf, NCOLUMNAS)    
    y_future = datos_reformados
    nom = medidor + '.keras'
    model.save(nom)
    return y_future
def correr_modelo(data, nombre):
    nom = nombre + '.keras'
    model = Model.load_model(nom) 
    # 2. Asegurar que los datos de entrada tengan el formato correcto (float32)
    # data debe tener la forma (1, lp, NCOLUMNAS) -> ej: (1, 1, NCOLUMNAS)
    input_data = data.astype('float32')    
    # 3. Realizar la predicción directa
    prediction = model.predict(input_data, verbose=0)    
    # 4. Limpiar las dimensiones para obtener tu matriz 
    y_pred = np.squeeze(prediction, axis=0)       
    return y_pred
def correr_predictor(data, nfut, nombre_columna):
    lp = 60 #4 veces el forecast hacia atras
    x, y = split_train_data(data,nfut,lp)
    res = modelo_lstm(x,y,nfut,lp,nombre_columna)
    return res    
def gen_prediccion(df, nfut, train_run, multi, medidor):
    df_copy = df.iloc[:0,:].copy() 
    df_x = escalar_datos(df)
    j = 0
    if train_run: 
        if multi:
            df_y = df_x[lista_datos].copy()
            x, y = split_train_data_multi(df_y,nfut,nfut)
           # Verificar las dimensiones (shapes)
            print("\n--- Dimensiones Resultantes para Seq2Seq ---")
            print(f"Forma de X_data (Entrada al Encoder): {x.shape}") 
            print(f"Forma de y_data (Salida deseada del Decoder): {y.shape}") 
            res = modelo_multi_lstm(x,y,nfut,nfut, medidor)
            df_copy = pd.DataFrame(res, columns=lista_datos)             
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
def predictor_multi_lstm(df_clean, _PASOS, medidor, nombre):
    fecha = datetime.now()
    try:
        #extrae fecha ultima usando busqueda de ultimo registro
        # si eso no funciona usamos busqueda clasica
        dfx = obtener_ultimo_dato_dataframe(medidor)
        dfx.columns = dfx.columns.droplevel(0)
        dfx = dfx.rename_axis('time') 
        #logger.info(f'df ultimo cargado:{dfx}')
        #fecha = dfx[time].iloc[-1]  #esta es la linea que falla
        fecha = dfx.index[0]
        logger.info(f'fecha cargada desde df ultimo:{fecha}')
    except Exception as e:
        now = datetime.now(timezone.utc)        
        now_str = datetime.strftime(now, "%Y-%m-%dT%H:%M:%SZ")
        end_time = now_str  
        logger.info("fecha cargada a modo utc")
        pass
    if fecha is not None and fecha != 0 and fecha != "0":
        #now = fecha
        '''now_str = datetime.strftime(now, "%Y-%m-%dT%H:%M:%SZ")'''
        _now = fecha.strftime("%Y-%m-%dT%H:%M:%S+00:00")                
        end_time = _now
    else: 
        now = datetime.now(timezone.utc)
        now_str = datetime.strftime(now, "%Y-%m-%dT%H:%M:%SZ")
        end_time = now_str 
        logger.info("cargada fecha en modo utc")  
    #prev=datetime.now(timezone.utc) - timedelta(days = 5) #tiene que ser un mes antes
    _prev = datetime.now(timezone.utc) - timedelta(days=5)
    '''prev_str = datetime.strftime(prev, "%Y-%m-%dT%H:%M:%SZ")'''
    prev_str = _prev.strftime("%Y-%m-%dT%H:%M:%S+00:00")
    start_time = prev_str
    logger.info(f'fecha obtenida:{end_time},{start_time}')
    try:        
        dfw = busqueda_influx2(start_time, end_time, medidor)
        logger.info("Busqueda estandar")
    except Exception as e:
         logger.info("Problema con busqueda")
         mi_hora = datetime(2026, 6, 10, 9, 30, 0)
         prev = mi_hora - timedelta(days = 5)
         end_time = datetime.strftime(now, "%Y-%m-%dT%H:%M:%SZ")
         start_time = datetime.strftime(prev, "%Y-%m-%dT%H:%M:%SZ")
         dfw = busqueda_influx2(start_time, end_time, medidor)
    ultima_med = merge_data(dfw, silenciar_warning=True)
    ultima_med['time']=ultima_med['time']+pd.Timedelta(hours = 3)
    ultima_fecha = ultima_med['time'].iloc[-1]
    ultima_fecha = datetime.strftime(ultima_fecha, "%Y-%m-%dT%H:%M:%S+00:00")
    logger.info(f'ultimafecha:{ultima_fecha}')        
    df_a = ultima_med[['time'] + lista_datos]
    df_pred = df_a.tail(4*_PASOS).reset_index(drop=True)
    df_pred = df_pred.set_index('time')
    if _PASOS > 360:
        df_pred = df_pred.resample('2min').mean().reset_index()
        pasos = _PASOS//12
        second = 10*12
    else:
        pasos = _PASOS
        second = 10    
    df_pred = df_pred.fillna(df_pred.mean())
    logger.info(f'longitud de resample={len(df_pred)}')
    df_res = gen_prediccion(df_pred,pasos,1,1, medidor)
    df_fin = df_pred.tail(pasos).reset_index(drop=True)
    rmse = sqrt(mean_squared_error(df_fin['PowA_L1_Ins'], df_res['PowA_L1_Ins']))
    mae = mean_absolute_error(df_fin['PowA_L1_Ins'], df_res['PowA_L1_Ins'])
    mape = mean_absolute_percentage_error(df_fin['PowA_L1_Ins'], df_res['PowA_L1_Ins'])*100
    print(f'RMSE de la predicción: {rmse}')
    print(f'MAE de la predicción: {mae}')
    print(f'MAPE de la predicción: {mape}')     
    future_dates = create_future_dates_column(ultima_fecha, pasos, pd.Timedelta(seconds=second))
    df_res['time'] = future_dates['time']
    df_res['time'] = pd.to_datetime(df_res['time']).dt.strftime('%Y-%m-%dT%H:%M:%S+00:00')
    last_col = df_res.pop(df_res.columns[-1])
    df_res.insert(0,last_col.name,last_col)
    logger.info(f'El dataframe arranca con los siguientes datos:{df_res.head(5)}')
    #df_res['time'] = df_res['time'].dt.tz_localize('UTC').dt.tz_convert('America/Argentina/Buenos_Aires')
    _nombre = nombre
    subir_prediccion_influxdb_v2(df_res,_nombre)
    return df_res
'''
def usar_trends(data, periodo):
    t,s,r = tendencias.decompose_series(data, periodo)
    return t,s,r
'''