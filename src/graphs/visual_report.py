# src/main.py

#Config iniciales
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from visualization import (
    plot_time_series,
    plot_boxplot,
    plot_histogram,
    plot_multiple_series
)

from config import (
    EXECUTE_VISUALIZATION,
    SHOW_GRAPHS,
    SAVE_OUTPUTS,
    IMAGES_DIR,
)

#imp de librerías externas 
import pandas as pd
import matplotlib.pyplot as plt
from adtk.visualization import plot
import pandas as pd
from utils.logger import logger
import matplotlib.pyplot as plt

# 🔹 Carga de datos limpios
clean_path = os.path.join("data", "raw", "df_clean.csv")
df_clean = pd.read_csv(clean_path, parse_dates=['time'])
print("Datos limpios cargados:")
print(df_clean.head())
print(df_clean.tail())

if EXECUTE_VISUALIZATION:
    logger.info("Ejecutando visualizaciones...")

    if 'time' in df_clean.columns and 'EA_I_IV_T' in df_clean.columns:
        fig = plot_time_series(df_clean, 'time', ['EA_I_IV_T'], title='Energía Consumida', ylabel='Energía')
        if fig and SAVE_OUTPUTS:
            fig.savefig(os.path.join(IMAGES_DIR, "energia_consumida.png"))
        if SHOW_GRAPHS and fig:
            fig.show()
        else:
            plt.close(fig)

    fig = plot_boxplot(df_clean, ['Vrms_L1_Ins', 'Vrms_L2_Ins', 'Vrms_L3_Ins'], title='Tensión por Fase')
    if fig and SAVE_OUTPUTS:
        fig.savefig(os.path.join(IMAGES_DIR, "boxplot_tension.png"))
    if SHOW_GRAPHS and fig:
        fig.show()
    else:
        plt.close(fig)

    for col in ['Irms_L1_Ins', 'Irms_L2_Ins', 'Irms_L3_Ins']:
        fig = plot_histogram(df_clean, col)
        if fig and SAVE_OUTPUTS:
            fig.savefig(os.path.join(IMAGES_DIR, f"hist_{col}.png"))
        if SHOW_GRAPHS and fig:
            fig.show()
        else:
            plt.close(fig)

    figuras = plot_multiple_series(df_clean, 'time', {
        'Tensión': ['Vrms_L1_Ins', 'Vrms_L2_Ins', 'Vrms_L3_Ins'],
        'Corriente': ['Irms_L1_Ins', 'Irms_L2_Ins', 'Irms_L3_Ins'],
        'Potencia Activa': ['PowA_L1_Ins', 'PowA_L2_Ins', 'PowA_L3_Ins']
    })
    for grupo, fig in figuras:
        if fig and SAVE_OUTPUTS:
            fig.savefig(os.path.join(IMAGES_DIR, f"grupo_{grupo.lower().replace(' ', '_')}.png"))
        if SHOW_GRAPHS and fig:
            fig.show()
        else:
            plt.close(fig)

if SHOW_GRAPHS:
    print("Mostrando gráficos. Cerrá la ventana para continuar...")
    plt.show(block=True)

