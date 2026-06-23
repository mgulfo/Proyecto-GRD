import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from notebooks.visual_validation import graficar_ejemplos_series
import pandas as pd

# Cargar series ya guardadas
df_anom = pd.read_csv("data/raw/serie_anomala_AutoReg.csv")
df_norm = pd.read_csv("data/raw/serie_normal_AutoReg.csv")

graficar_ejemplos_series(df_anom, df_norm, rango=300)
