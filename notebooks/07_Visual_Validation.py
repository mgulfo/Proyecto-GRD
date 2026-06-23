import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import matplotlib.pyplot as plt
import numpy as np
import os

def graficar_ejemplos_series(df_anom, df_norm, rango=300, output_path="data/images/comparacion_series_detectadas.png"):
    """
    Grafica 3 ejemplos aleatorios de series anómalas y 3 normales y guarda el resultado como imagen.
    """

    if df_anom.empty or df_norm.empty:
        print("[!] Los DataFrames están vacíos. No se puede graficar.")
        return

    try:
        # Calcular la cantidad total de ventanas disponibles
        n_anom = len(df_anom) // (rango + 1)
        n_norm = len(df_norm) // (rango + 1)

        # Verificamos que haya al menos 3 de cada una
        if n_anom < 3 or n_norm < 3:
            print("[!] No hay suficientes ventanas para graficar (se necesitan al menos 3 de cada tipo).")
            return

        # Selección aleatoria de 3 índices distintos
        idx_anom = np.random.choice(n_anom, size=3, replace=False)
        idx_norm = np.random.choice(n_norm, size=3, replace=False)

        # Crear subplots
        fig, axs = plt.subplots(2, 3, figsize=(15, 6), sharex=True)

        for i, idx in enumerate(idx_anom):
            ini = idx * (rango + 1)
            fin = ini + rango + 1
            axs[0, i].plot(df_anom['PowF_T_Ins'].iloc[ini:fin], color='red', label='FP')
            axs[0, i].plot(df_anom['THDI_L1_Ins'].iloc[ini:fin], color='green', label='THD')
            axs[0, i].set_title(f"Anómala #{idx + 1}")
            axs[0, i].grid(True)

        for i, idx in enumerate(idx_norm):
            ini = idx * (rango + 1)
            fin = ini + rango + 1
            axs[1, i].plot(df_norm['PowF_T_Ins'].iloc[ini:fin], color='blue', label='FP')
            axs[1, i].plot(df_norm['THDI_L1_Ins'].iloc[ini:fin], color='purple', label='THD')
            axs[1, i].set_title(f"Normal #{idx + 1}")
            axs[1, i].grid(True)

        axs[0, 0].set_ylabel("Anómalas")
        axs[1, 0].set_ylabel("Normales")

        for ax in axs.flat:
            ax.legend()

        plt.tight_layout()

        # Crear carpeta si no existe
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path)
        plt.show()
        print(f"[✔] Imagen guardada en: {output_path}")

    except Exception as e:
        print(f"[!] Error al graficar ejemplos: {e}")