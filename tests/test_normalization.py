# tests/test_normalization.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pandas as pd
import numpy as np
from data_processing.data_cleaning import normalize_all_numeric

def test_normalization_range():
    df = pd.DataFrame({
        "x": [10, 20, 30, 40],
        "y": [100, 200, 300, 400]
    })
    norm_df = normalize_all_numeric(df)

    assert (norm_df >= 0).all().all(), "Todos los valores deben ser >= 0"
    assert (norm_df <= 1).all().all(), "Todos los valores deben ser <= 1"
    assert norm_df.shape == df.shape, "El shape debe mantenerse tras la normalización"