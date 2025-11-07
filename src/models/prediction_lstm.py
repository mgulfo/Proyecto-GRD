import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from keras import Sequential
from utils.logger import logger
from keras import layers, losses, callbacks, metrics, optimizers
import warnings

warnings.filterwarnings('ignore')

def Sequential_Input_LSTM(df, input_sequence):
    df_np = df.to_numpy()
    X = []
    y = []    
    for i in range(len(df_np) - input_sequence):
        row = [a for a in df_np[i:i + input_sequence]]
        X.append(row)
        label = df_np[i + input_sequence]
        y.append(label)    
    return np.array(X), np.array(y)
  
def plot(data, n, autoencoder):
  enc_img = autoencoder.encoder(data)
  dec_img = autoencoder.decoder(enc_img)
  N = n
  plt.plot(data[n], 'b')
  plt.plot(dec_img[n], 'r')
  plt.fill_between(np.arange(N), data[n], dec_img[n], color = 'lightcoral')
  plt.legend(labels=['Input', 'Reconstruction', 'Error'])
  plt.show()


def prediction(model, data, threshold):
  rec = model(data)
  loss = losses.mae(rec, data)
  return tf.math.less(loss, threshold)

def cfg_lstm(model, units, ret, activations, functions):
    j = 0
    for i in units:
        if ret[j] == 1:
            model.add(layers.LSTM(i, return_sequences = True))
        else:
            model.add(layers.LSTM(i))
        j=j+1    
    j = 0
    for i in activations:
        model.add(layers.Dense(i, activation = functions[j]))
        j=j+1
    return model

def gen_split(x,y,valor1, valor2):
    _x, _y = x[valor1:valor2], y[valor1:valor2]      
    return np.array(_x), np.array(_y)

def gen_split_un(x,valor1, valor2):
    _x = x.loc[valor1:valor2]      
    return _x.to_numpy()

def correr_prediccion(df_norm, df_anorm):
  X, Y = Sequential_Input_LSTM(df_norm['PowF_T_Ins'],1)
  L = len(df_norm)
  LL = int((L/3)-1) # ME ASEGURO DE CUBRIR MENOS DEL 100% DE LOS DATOS 
  an_train_data, an_test_data = Sequential_Input_LSTM(df_anorm['PowF_T_Ins'],1)
  x_t, y_t = gen_split(X, Y, 0,LL)
  x_v, y_v = gen_split(X, Y,LL,LL*2)
  x_ts, y_ts = gen_split(X, Y, LL*2,LL*3)
  n_features = 1
  model1 = Sequential() 
  model1.add(layers.InputLayer((32,n_features)))
  unidades = [32,16,1]
  reti = [1,0,0]
  activ = [1,1]
  func = ['tanh','linear']
  #cfg_lstm(model1,unidades,reti, activ, func)    
  model1.add(layers.LSTM(32,return_sequences = True))
  model1.add(layers.LSTM(16))
  model1.add(layers.Dense(1, activation='linear'))
  early_stop = callbacks.EarlyStopping(monitor = 'val_loss', patience = 200)
  model1.compile(loss = losses.MeanSquaredError(), optimizer = optimizers.Adam(learning_rate = 0.0001), metrics=[metrics.RootMeanSquaredError()])
  model1.fit(x_t, y_t, validation_data = (x_v, y_v), epochs = 45, callbacks = [early_stop])
  losses_df1 = pd.DataFrame(model1.history.history)
  losses_df1.plot(figsize = (10,6))
  test_predictions1 = model1.predict(x_ts).flatten()
  X_test_list = []
  for i in range(len(x_ts)):
      X_test_list.append(x_ts[i][0])
  test_predictions_df1 = pd.DataFrame({'X_test':list(X_test_list), 'LSTM Prediction':list(test_predictions1)})
  print(test_predictions_df1.head())
  return test_predictions_df1, an_test_data

######## Sección 7 - Evaluación de Predicción ##########
 
def evaluar_prediccion(df_st_norm, df_st_anom, visualizar_prediccion=True):
    pred_norm, pred_anom = correr_prediccion(df_st_norm, df_st_anom)
    L = len(pred_norm)

    if visualizar_prediccion:
        fig, axes = plt.subplots(2, 1, figsize=(16, 16))
        axes[0].set_title('Predicción y test')
        axes[0].plot(pred_norm)
        axes[0].set_ylabel('Amplitud')

        axes[1].set_title('Datos anómalos')
        axes[1].plot(pred_anom[:L])
        axes[1].set_xlabel('Tiempo')
        axes[1].set_ylabel('Amplitud')

        plt.tight_layout()
        plt.show()

    mae_normal = mean_absolute_error(pred_norm['X_test'], pred_norm['LSTM Prediction'])
    logger.info(f"Mean Absolute Error de test y predicción: {mae_normal}")

    mae_anom = None
    if len(pred_anom) > 0:
        mae_anom = mean_absolute_error(pred_anom[:L], pred_norm['LSTM Prediction'])
        logger.info(f"Mean Absolute Error de predicción y anormal: {mae_anom}")

    return mae_normal, mae_anom, pred_norm, pred_anom
  