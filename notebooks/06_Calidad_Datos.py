# revisar_calidad_datos.py

"""
Auditar rápidamente cualquier archivo CSV o DataFrame
"""

import pandas as pd

def revisar_calidad_datos(df, columnas_clave=None):
    """
    Revisa la calidad de los datos en un DataFrame:
    - Muestra tipo de dato por columna
    - Muestra cantidad de valores nulos
    - Muestra valores no numéricos si hay columnas object
    - Si se especifican columnas_clave, se hace foco en ellas
    """

    print("\n=== Tipos de dato por columna ===")
    print(df.dtypes)

    print("\n=== Cantidad de valores nulos por columna ===")
    print(df.isnull().sum())

    # Si no se especifica, se usan todas las columnas tipo object
    if columnas_clave is None:
        columnas_clave = df.select_dtypes(include=['object']).columns.tolist()

    if columnas_clave:
        print(f"\n=== Revisión de columnas tipo texto o mixtas: {columnas_clave} ===")
        for col in columnas_clave:
            valores_unicos = df[col].unique()
            print(f"\nColumna: {col}")
            print(f"Cantidad de valores únicos: {len(valores_unicos)}")
            print(f"Ejemplos: {valores_unicos[:10]}")
    else:
        print("\n✅ No hay columnas tipo object sospechosas. Tipos numéricos consistentes.")

    print("\n=== Fin de revisión ===")
