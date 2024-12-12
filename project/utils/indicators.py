"""
Módulo para cálculo de indicadores técnicos usando pandas_ta.
"""
import pandas as pd
import pandas_ta as ta

def calculate_indicators(df):
    """Calcula todos os indicadores técnicos."""
    if df is None or df.empty:
        raise ValueError("DataFrame está vazio ou None")
    
    try:
        df = df.copy()
        
        # Stochastic
        stoch = df.ta.stoch(high='High', low='Low', close='Close', k=14, d=3, smooth_k=3)
        df['STOCH_K'] = stoch['STOCHk_14_3_3']
        df['STOCH_D'] = stoch['STOCHd_14_3_3']
        df['STOCH_K_PREV'] = df['STOCH_K'].shift(1)
        df['STOCH_D_PREV'] = df['STOCH_D'].shift(1)
        
        # RSI
        df['RSI'] = df.ta.rsi(close='Close', length=7)
        df['RSI_PREV'] = df['RSI'].shift(1)
        
        # MACD
        macd = df.ta.macd(close='Close', fast=12, slow=26, signal=9)
        df['MACD'] = macd['MACD_12_26_9']
        df['MACD_SIGNAL'] = macd['MACDs_12_26_9']
        df['MACD_HIST'] = macd['MACDh_12_26_9']
        df['MACD_PREV'] = df['MACD'].shift(1)
        
        # Bollinger Bands
        bbands = df.ta.bbands(close='Close', length=20)
        df['BB_UPPER'] = bbands['BBU_20_2.0']
        df['BB_MIDDLE'] = bbands['BBM_20_2.0']
        df['BB_LOWER'] = bbands['BBL_20_2.0']
        
        # Médias Móveis
        df['SMA_20'] = df.ta.sma(close='Close', length=20)
        df['EMA_20'] = df.ta.ema(close='Close', length=20)
        
        # Volatilidade
        df['ATR'] = df.ta.atr(high='High', low='Low', close='Close', length=14)
        
        # Volume
        df['OBV'] = df.ta.obv(close='Close', volume='Volume')
        df['MFI'] = df.ta.mfi(high='High', low='Low', close='Close', volume='Volume')
        
        # Preencher valores NaN
        df = df.fillna(method='bfill').fillna(method='ffill')
        
        return df
        
    except Exception as e:
        raise Exception(f"Erro ao calcular indicadores: {str(e)}")