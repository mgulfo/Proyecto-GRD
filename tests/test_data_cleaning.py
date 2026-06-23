# tests/test_data_cleaning.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pandas as pd
import pytest
from data_processing.data_cleaning import preprocess_data

def test_preprocess_removes_nulls():
    df = pd.DataFrame({
        "a": [1, 2, None],
        "b": [None, 5, 6]
    })
    result = preprocess_data(df)
    assert result.isnull().sum().sum() == 0, "Debe eliminar filas con valores nulos"

def test_preprocess_removes_all_nulls():
    df = pd.DataFrame({
        "a": [None, None],
        "b": [None, None]
    })
    result = preprocess_data(df)
    assert result.empty, "Debe devolver un DataFrame vacío si todos los valores son nulos"

