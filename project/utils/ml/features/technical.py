"""
Módulo para features técnicas.
"""
import pandas as pd
import pandas_ta as ta

def create_momentum_features(df):
    """Cria features de momentum."""
    features = pd.DataFrame(index=df.index)
    
    # ROC (Rate of Change)
    features['ROC'] = df.ta.roc(close='Close', length=10)
    
    # MFI (Money Flow Index)
    features['MFI'] = df.ta.mfi(high='High', low='Low', close='Close', volume='Volume')
    
    # RSI (Relative Strength Index)
    features['RSI'] = df.ta.rsi(close='Close', length=14)
    features['RSI_MA'] = features['RSI'].rolling(10).mean()
    
    return features

def create_volume_features(df):
    """Cria features baseadas em volume."""
    features = pd.DataFrame(index=df.index)
    
    # OBV (On Balance Volume)
    features['OBV'] = df.ta.obv(close='Close', volume='Volume')
    features['OBV_ROC'] = features['OBV'].pct_change()
    
    # Volume Force
    close_change = df['Close'].diff()
    features['Volume_Force'] = close_change * df['Volume']
    
    # Volume Trend
    features['Volume_MA_Ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
    
    return features