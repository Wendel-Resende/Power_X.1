"""
Módulo base para cálculo de indicadores técnicos.
"""
import pandas as pd
import pandas_ta as ta

def validate_dataframe(df):
    """Valida o DataFrame de entrada."""
    if df is None or df.empty:
        raise ValueError("DataFrame está vazio ou None")
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Colunas ausentes: {missing}")
    return df.copy()

def fill_missing_values(df):
    """Preenche valores ausentes."""
    return df.fillna(method='bfill').fillna(method='ffill')