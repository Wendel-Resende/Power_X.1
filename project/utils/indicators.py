"""
Módulo para cálculo de indicadores técnicos usando pandas_ta.
"""
import pandas as pd
import pandas_ta as ta

def calculate_stochastic(df, k=14, d=3, smooth_k=3):
    """Calcula o oscilador Stochastic."""
    try:
        if df is None or df.empty:
            raise ValueError("DataFrame vazio")
            
        stoch = df.ta.stoch(high='High', low='Low', close='Close', k=k, d=d, smooth_k=smooth_k)
        df['STOCH_K'] = stoch[f'STOCHk_{k}_{d}_{smooth_k}']
        df['STOCH_D'] = stoch[f'STOCHd_{k}_{d}_{smooth_k}']
        df['STOCH_K_PREV'] = df['STOCH_K'].shift(1)
        df['STOCH_D_PREV'] = df['STOCH_D'].shift(1)
        return df
    except Exception as e:
        raise Exception(f"Erro ao calcular Stochastic: {str(e)}")

def calculate_rsi(df, length=7):
    """Calcula o indicador RSI."""
    try:
        if df is None or df.empty:
            raise ValueError("DataFrame vazio")
            
        df['RSI'] = df.ta.rsi(close='Close', length=length)
        df['RSI_PREV'] = df['RSI'].shift(1)
        return df
    except Exception as e:
        raise Exception(f"Erro ao calcular RSI: {str(e)}")

def calculate_macd(df, fast=12, slow=26, signal=9):
    """Calcula o indicador MACD."""
    try:
        if df is None or df.empty:
            raise ValueError("DataFrame vazio")
            
        macd = df.ta.macd(close='Close', fast=fast, slow=slow, signal=signal)
        df['MACD'] = macd[f'MACD_{fast}_{slow}_{signal}']
        df['MACD_SIGNAL'] = macd[f'MACDs_{fast}_{slow}_{signal}']
        df['MACD_HIST'] = macd[f'MACDh_{fast}_{slow}_{signal}']
        df['MACD_PREV'] = df['MACD'].shift(1)
        return df
    except Exception as e:
        raise Exception(f"Erro ao calcular MACD: {str(e)}")

def calculate_indicators(df):
    """Calcula todos os indicadores técnicos."""
    if df is None or df.empty:
        raise ValueError("DataFrame está vazio ou None")
    
    try:
        df = df.copy()
        
        # Calcular indicadores
        df = calculate_stochastic(df)
        df = calculate_rsi(df)
        df = calculate_macd(df)
        
        # Preencher valores NaN
        df = df.fillna(method='bfill').fillna(method='ffill')
        
        return df
    except Exception as e:
        raise Exception(f"Erro ao calcular indicadores: {str(e)}")