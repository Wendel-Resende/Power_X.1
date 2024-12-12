"""
Módulo para engenharia de features.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import RobustScaler
import pandas_ta as ta

class FeatureEngineering:
    def __init__(self):
        self.scaler = RobustScaler()
        self.feature_names = []
    
    def create_price_features(self, df):
        """Cria features baseadas em preço."""
        features = pd.DataFrame(index=df.index)
        
        # Retornos em diferentes períodos
        periods = [1, 3, 5, 10, 20]
        for period in periods:
            features[f'Returns_{period}d'] = df['Close'].pct_change(period)
            features[f'Volume_{period}d'] = df['Volume'].pct_change(period)
        
        # Volatilidade
        features['Volatility'] = df['Close'].pct_change().rolling(20).std()
        
        # Médias móveis
        for period in [5, 10, 20, 50]:
            features[f'SMA_{period}'] = df.ta.sma(close='Close', length=period)
            features[f'SMA_Volume_{period}'] = df['Volume'].rolling(period).mean()
        
        return features
    
    def create_technical_features(self, df):
        """Cria features técnicas avançadas."""
        features = pd.DataFrame(index=df.index)
        
        # Momentum
        features['ROC'] = df.ta.roc(close='Close', length=10)
        features['MFI'] = df.ta.mfi(high='High', low='Low', close='Close', volume='Volume')
        
        # Volatilidade
        features['ATR'] = df.ta.atr(high='High', low='Low', close='Close')
        features['BB_Width'] = df.ta.bbands(close='Close')['BBB_MIDDLE'] - df.ta.bbands(close='Close')['BBB_LOWER']
        
        # Volume
        features['OBV'] = df.ta.obv(close='Close', volume='Volume')
        features['Volume_Delta'] = df['Volume'].diff()
        
        return features