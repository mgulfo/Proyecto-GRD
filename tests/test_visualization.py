# tests/test_visualization.py

'''
🧪 Test Visualization

Verifica que las funciones:
-> plot_time_series
-> plot_boxplot
-> plot_histogram

devuelvan objetos matplotlib.figure.Figure, como corresponde'
'''

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import matplotlib
matplotlib.use('Agg')  # Fuerza backend que no necesita GUI

import pandas as pd
from visualization import plot_time_series, plot_boxplot, plot_histogram
import matplotlib.pyplot as plt

def test_plot_time_series_returns_figure():
    df = pd.DataFrame({
        "time": pd.date_range(start="2023-01-01", periods=10, freq="H"),
        "EA_I_IV_T": range(10)
    })
    fig = plot_time_series(df, "time", ["EA_I_IV_T"])
    assert isinstance(fig, plt.Figure), "Debe devolver un objeto matplotlib.figure.Figure"

def test_plot_boxplot_returns_figure():
    df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
    fig = plot_boxplot(df, ["x", "y"])
    assert isinstance(fig, plt.Figure), "Debe devolver un objeto matplotlib.figure.Figure"

def test_plot_histogram_returns_figure():
    df = pd.DataFrame({"x": [1, 1, 2, 2, 3, 3, 4]})
    fig = plot_histogram(df, "x")
    assert isinstance(fig, plt.Figure), "Debe devolver un objeto matplotlib.figure.Figure"
