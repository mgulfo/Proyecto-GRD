# src/main.py

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from query_engine import busqueda_influx1, busqueda_influx2, merge_data
from data_processing.data_cleaning import preprocess_data, normalize_all_numeric
from visualization import (
    plot_time_series,
    plot_boxplot,
    plot_histogram,
    plot_multiple_series
)

# from event_detection import detect_anomalies          # ← A implementar más adelante
# from models.modeling import predict_consumption       # ← A implementar más adelante

import matplotlib.pyplot as plt
import os

# CONFIGURACIÓN GENERAL
EXECUTE_VISUALIZATION = True  # Cambiar a False para evitar gráficos
SHOW_GRAPHS = False           # Mostrar gráficos en pantalla
SAVE_OUTPUTS = True           # Guardar archivos generados
OUTPUT_DIR = os.path.join("data", "raw")      # Ruta de guardado de datos CSV
IMAGES_DIR = os.path.join("data", "images")    # Ruta de guardado de gráficos

def main():
    
    # ---------------------------------------------
    # 1. PARÁMETROS DE CONSULTA
    # ---------------------------------------------
    fecha_inicio_v1 = '2023-08-01T00:00:00Z'
    fecha_fin_v1 = '2023-08-11T23:59:50Z'
    fecha_inicio_v2 = "2025-01-20T00:00:00Z"
    fecha_fin_v2 = "2025-01-21T23:59:50Z"
    location = "MEDIA"

    if SAVE_OUTPUTS:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        os.makedirs(IMAGES_DIR, exist_ok=True)

    # ---------------------------------------------
    # 2. CONSULTA A LAS BASES DE DATOS
    # ---------------------------------------------
    print("Consultando InfluxDB 1.8 ...")
    data_v1 = busqueda_influx1(fecha_inicio_v1, fecha_fin_v1, location)
    df_v1 = merge_data(data_v1)

    print("Consultando InfluxDB 2.7 ...")
    data_v2 = busqueda_influx2(fecha_inicio_v2, fecha_fin_v2, location)
    df_v2 = merge_data(data_v2)

    # Verificación básica
    if df_v1.empty:
        print("⚠️ Consulta a InfluxDB 1.8 no trajo datos")
    if df_v2.empty:
        print("⚠️ Consulta a InfluxDB 2.7 no trajo datos")
    if 'time' not in df_v1.columns:
        print("⚠️ 'time' no está en las columnas de df_v1")

    # Mostrar previews
    print("\n📥 InfluxDB 1 - Preview:")
    print(df_v1.head())
    print(df_v1.tail())

    print("\n📥 InfluxDB 2 - Preview:")
    print(df_v2.head())
    print(df_v2.tail())

    # Guardar datos crudos antes de limpieza
    if SAVE_OUTPUTS:
        raw_v1_path = os.path.join(OUTPUT_DIR, "df_v1_raw.csv")
        raw_v2_path = os.path.join(OUTPUT_DIR, "df_v2_raw.csv")
        df_v1.to_csv(raw_v1_path, index=False)
        df_v2.to_csv(raw_v2_path, index=False)
        print(f"✅ Datos crudos InfluxDB 1 guardados en {os.path.abspath(raw_v1_path)}")
        print(f"✅ Datos crudos InfluxDB 2 guardados en {os.path.abspath(raw_v2_path)}")

    # ---------------------------------------------
    # 3. LIMPIEZA DE DATOS
    # ---------------------------------------------
    print("Limpieza básica ...")
    df_clean_v1 = preprocess_data(df_v1)
    df_clean_v2 = preprocess_data(df_v2)

    if SAVE_OUTPUTS:
        clean_path_v1 = os.path.join(OUTPUT_DIR, "df_clean_v1.csv")
        df_clean_v1.to_csv(clean_path_v1, index=False)
        print(f"✅ Datos limpios InfluxDB 1 guardados en {os.path.abspath(clean_path_v1)}")

        clean_path_v2 = os.path.join(OUTPUT_DIR, "df_clean_v2.csv")
        df_clean_v2.to_csv(clean_path_v2, index=False)
        print(f"✅ Datos limpios InfluxDB 2 guardados en {os.path.abspath(clean_path_v2)}")

    # ---------------------------------------------
    # 4. NORMALIZACIÓN (para futuros modelos)
    # ---------------------------------------------
    df_norm_v1 = normalize_all_numeric(df_clean_v1)

    if SAVE_OUTPUTS:
        norm_path_v1 = os.path.join(OUTPUT_DIR, "df_norm_v1.csv")
        df_norm_v1.to_csv(norm_path_v1, index=False)
        print(f"✅ Datos normalizados InfluxDB 1 guardados en {os.path.abspath(norm_path_v1)}")

    # ---------------------------------------------
    # 5. VISUALIZACIONES
    # ---------------------------------------------
    if EXECUTE_VISUALIZATION:
        if 'time' in df_clean_v1.columns and 'EA_I_IV_T' in df_clean_v1.columns:
            fig = plot_time_series(df_clean_v1, 'time', ['EA_I_IV_T'],
                                   title='Energía Consumida',
                                   ylabel='Energía (unidades originales)')
            if fig and SAVE_OUTPUTS:
                fig.savefig(os.path.join(IMAGES_DIR, "energia_consumida.png"))
            if SHOW_GRAPHS and fig:
                fig.show()
            else:
                plt.close(fig)

        # Boxplot de tensiones
        fig = plot_boxplot(df_clean_v1, ['Vrms_L1_Ins', 'Vrms_L2_Ins', 'Vrms_L3_Ins'], title='Tensión por Fase')
        if fig and SAVE_OUTPUTS:
            fig.savefig(os.path.join(IMAGES_DIR, "boxplot_tension.png"))
        if SHOW_GRAPHS and fig:
            fig.show()
        else:
            plt.close(fig)

        # Histogramas de corrientes
        for col in ['Irms_L1_Ins', 'Irms_L2_Ins', 'Irms_L3_Ins']:
            fig = plot_histogram(df_clean_v1, col)
            if fig and SAVE_OUTPUTS:
                fig.savefig(os.path.join(IMAGES_DIR, f"hist_{col}.png"))
            if SHOW_GRAPHS and fig:
                fig.show()
            else:
                plt.close(fig)

        # Comparativa de series por grupo
        figuras = plot_multiple_series(df_clean_v1, 'time', {
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

    # ---------------------------------------------
    # 6. DETECCIÓN DE PERTURBACIONES (próxima etapa)
    # ---------------------------------------------
    # perturbaciones = detect_anomalies(df_norm_v1)
    # print(f"Se detectaron {len(perturbaciones)} eventos anómalos.")

    # ---------------------------------------------
    # 7. PREDICCIÓN DE CONSUMO (próxima etapa)
    # ---------------------------------------------
    # predicciones = predict_consumption(df_norm_v1)
    # print(predicciones.head())

if __name__ == "__main__":
    main()
