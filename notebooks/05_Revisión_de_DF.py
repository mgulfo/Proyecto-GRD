import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from src.utils.calidad_datos import revisar_calidad_datos

df = pd.read_csv("data/raw/df_norm_v1.csv")
revisar_calidad_datos(df)