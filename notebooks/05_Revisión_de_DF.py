import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from notebooks.calidad_datos import revisar_calidad_datos

df = pd.read_csv("data/raw/df_norm.csv")
revisar_calidad_datos(df)