"""
Módulo para indicadores de momentum.
"""
import pandas as pd
import pandas_ta as ta
from .base import validate_dataframe

def calculate_rsi(df, length=7):
    """Calcula o RSI (Relative Strength Index)."""
    df = validate_dataframe(df)
    df['RSI'] = df.ta.rsi(close='Close', length=length)
    df['RSI_PREV'] = df['RSI'].shift(1)
    return df

def calculate_stochastic(df, k=14, d=3, smooth_k=3):
    """Calcula o Stochastic Oscillator."""
    df = validate_dataframe(df)
    stoch = df.ta.stoch(high='High', low='Low', close='Close', 
                       k=k, d=d, smooth_k=smooth_k)
    df['STOCH_K'] = stoch[f'STOCHk_{k}_{d}_{smooth_k}']
    df['STOCH_D'] = stoch[f'STOCHd_{k}_{d}_{smooth_k}']
    df['STOCH_K_PREV'] = df['STOCH_K'].shift(1)
    df['STOCH_D_PREV'] = df['STOCH_D'].shift(1)
    return df

def calculate_macd(df, fast=12, slow=26, signal=9):
    """Calcula o MACD (Moving Average Convergence Divergence)."""
    df = validate_dataframe(df)
    macd = df.ta.macd(close='Close', fast=fast, slow=slow, signal=signal)
    df['MACD'] = macd[f'MACD_{fast}_{slow}_{signal}']
    df['MACD_SIGNAL'] = macd[f'MACDs_{fast}_{slow}_{signal}']
    df['MACD_HIST'] = macd[f'MACDh_{fast}_{slow}_{signal}']
    df['MACD_PREV'] = df['MACD'].shift(1)
    return df