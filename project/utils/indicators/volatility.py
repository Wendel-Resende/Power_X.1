"""
Módulo para indicadores de volatilidade.
"""
import pandas as pd
import pandas_ta as ta
from .base import validate_dataframe

def calculate_bollinger_bands(df, length=20, std=2):
    """Calcula as Bandas de Bollinger."""
    df = validate_dataframe(df)
    bbands = df.ta.bbands(close='Close', length=length, std=std)
    df['BB_UPPER'] = bbands[f'BBU_{length}_{std}']
    df['BB_MIDDLE'] = bbands[f'BBM_{length}_{std}']
    df['BB_LOWER'] = bbands[f'BBL_{length}_{std}']
    df['BB_WIDTH'] = (df['BB_UPPER'] - df['BB_LOWER']) / df['BB_MIDDLE']
    return df

def calculate_atr(df, length=14):
    """Calcula o Average True Range."""
    df = validate_dataframe(df)
    df['ATR'] = df.ta.atr(high='High', low='Low', close='Close', length=length)
    return df