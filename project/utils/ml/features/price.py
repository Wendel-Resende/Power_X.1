"""
Módulo para features baseadas em preço.
"""
import pandas as pd
import numpy as np

def create_returns_features(df, periods=[1, 3, 5, 10, 20]):
    """Cria features de retornos."""
    features = pd.DataFrame(index=df.index)
    
    for period in periods:
        # Retornos
        features[f'Returns_{period}d'] = df['Close'].pct_change(period)
        # Volume
        features[f'Volume_{period}d'] = df['Volume'].pct_change(period)
        # Volatilidade
        features[f'Volatility_{period}d'] = df['Close'].pct_change().rolling(period).std()
    
    return features

def create_moving_averages(df, periods=[5, 10, 20, 50]):
    """Cria features de médias móveis."""
    features = pd.DataFrame(index=df.index)
    
    for period in periods:
        # Preço
        features[f'SMA_{period}'] = df['Close'].rolling(period).mean()
        # Volume
        features[f'Volume_SMA_{period}'] = df['Volume'].rolling(period).mean()
        # Cruzamentos
        features[f'Price_Above_SMA_{period}'] = (df['Close'] > features[f'SMA_{period}']).astype(int)
    
    return features