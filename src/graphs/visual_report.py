#Config iniciales
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from visualization import (
    plot_fp_total_line,
    plot_fp_y_potencia,
    plot_fp_y_tension,
    plot_fp_total_line,
    plot_fp_vs_variable_separados,
    plot_thd_vs_variable_separados,
    filtrar_por_rango_fecha
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

# 🔎 Definí el rango que querés estudiar
fecha_inicio = '2024-02-01T00:00:00'
fecha_fin = '2024-02-29T23:00:00'

# 🔹 Filtrar el DataFrame
df_zoom = filtrar_por_rango_fecha(df_clean, fecha_inicio, fecha_fin)

if EXECUTE_VISUALIZATION:
    logger.info("Ejecutando visualizaciones...")

# 🔹 FP total
fig = plot_fp_total_line(df_zoom)
fig.savefig(os.path.join(IMAGES_DIR, "fp_total.png")) if SAVE_OUTPUTS else None
fig.show() if SHOW_GRAPHS else plt.close(fig)

# 🔹 FP + Potencia y FP + Tensión por fase
for fase in ["L1", "L2", "L3"]:
    fig = plot_fp_y_potencia(df_zoom, fase)
    fig.savefig(os.path.join(IMAGES_DIR, f"fp_y_potencia_{fase}.png")) if SAVE_OUTPUTS else None
    fig.show() if SHOW_GRAPHS else plt.close(fig)

    fig = plot_fp_y_tension(df_zoom, fase)
    fig.savefig(os.path.join(IMAGES_DIR, f"fp_y_tension_{fase}.png")) if SAVE_OUTPUTS else None
    fig.show() if SHOW_GRAPHS else plt.close(fig)

# 🔹 FP vs Potencia Activa por fase
figs_fp_potencia = plot_fp_vs_variable_separados(df_zoom, 'PowA', 'Potencia Activa', 'Potencia (W)', ['L1', 'L2', 'L3'])
for fase, fig in figs_fp_potencia:
    fig.savefig(os.path.join(IMAGES_DIR, f"fp_vs_potencia_{fase.lower()}.png"))

# 🔹 FP vs Tensión por fase
figs_fp_tension = plot_fp_vs_variable_separados(df_zoom, 'Vrms', 'Tensión RMS', 'Tensión (V)', ['L1', 'L2', 'L3'])
for fase, fig in figs_fp_tension:
    fig.savefig(os.path.join(IMAGES_DIR, f"fp_vs_tension_{fase.lower()}.png"))

# 🔹 THDI vs Corriente (L1 y L3)
figs_thdi_corriente = plot_thd_vs_variable_separados(df_zoom, 'THDI', 'Irms', 'Corriente RMS', 'Corriente (A)', ['L1', 'L3'])
for fase, fig in figs_thdi_corriente:
    fig.savefig(os.path.join(IMAGES_DIR, f"thdi_vs_corriente_{fase.lower()}.png"))

# 🔹 THDV vs Tensión (L1 y L3)
figs_thdv_tension = plot_thd_vs_variable_separados(df_zoom, 'THDV', 'Vrms', 'Tensión RMS', 'Tensión (V)', ['L1', 'L3'])
for fase, fig in figs_thdv_tension:
    fig.savefig(os.path.join(IMAGES_DIR, f"thdv_vs_tension_{fase.lower()}.png"))


if SHOW_GRAPHS:
    print("Mostrando gráficos. Cerrá la ventana para continuar...")
    plt.show(block=True)

