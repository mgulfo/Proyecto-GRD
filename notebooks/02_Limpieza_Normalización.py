# notebooks/02_limpieza_normalizacion.ipynb

# 📓 Limpieza y Normalización de Datos (Notebook demostrativo)
# Este notebook ilustra cómo cargar, limpiar y normalizar datos paso a paso

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','src')))

import pandas as pd
from data_processing.data_cleaning import preprocess_data, preprocess_data2, normalize_all_numeric
import matplotlib.pyplot as plt
import seaborn as sns

# 🔹 Carga de datos crudos
raw_path = os.path.join("data", "raw", "df_raw.csv")
df_raw = pd.read_csv(raw_path, parse_dates=['time'])
print("Datos crudos cargados:")
print(df_raw.head())
print(df_raw.tail())

# 🔹 Eliminación de valores nulos y columnas duplicadas
df_clean = preprocess_data2(df_raw)
print("\nDatos después de limpieza:")
print(df_clean.head())

# 🔹 Estadísticas antes de normalizar
print("\nResumen estadístico antes de normalizar:")
print(df_clean.describe())

# 🔹 Normalización Min-Max de columnas numéricas
df_norm = normalize_all_numeric(df_clean)
print("\nDatos normalizados (primeras filas):")
print(df_norm.head())

# 🔹 Gráfico comparativo antes vs después (columna ejemplo si existe)
columna = 'EA_I_IV_T'
if columna in df_clean.columns:
    fig, axs = plt.subplots(1, 2, figsize=(14, 5))
    sns.histplot(df_clean[columna], ax=axs[0], kde=True)
    axs[0].set_title("Original")
    sns.histplot(df_norm[columna], ax=axs[1], kde=True)
    axs[1].set_title("Normalizado")
    plt.suptitle(f"Distribución de {columna}")
    plt.tight_layout()
    plt.show()
else:
    print(f"La columna '{columna}' no está en el DataFrame.")
