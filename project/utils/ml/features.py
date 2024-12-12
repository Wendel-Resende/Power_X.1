"""
Módulo para engenharia de features.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import RobustScaler
from talib import RSI, MACD, STOCH

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
            features[f'SMA_{period}'] = df['Close'].rolling(period).mean()
            features[f'SMA_Volume_{period}'] = df['Volume'].rolling(period).mean()
        
        return features
    
    def create_technical_features(self, df):
        """Cria features técnicas avançadas."""
        features = pd.DataFrame(index=df.index)
        
        # Momentum
        features['ROC'] = df['Close'].pct_change(10)
        features['MFI'] = self._money_flow_index(df)
        
        # Volatilidade
        features['ATR'] = self._average_true_range(df)
        features['BB_Width'] = self._bollinger_bandwidth(df)
        
        # Volume
        features['OBV'] = self._on_balance_volume(df)
        features['Volume_Delta'] = df['Volume'].diff()
        
        return features
    
    def _money_flow_index(self, df, period=14):
        """Calcula Money Flow Index."""
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        money_flow = typical_price * df['Volume']
        
        positive_flow = pd.Series(0.0, index=df.index)
        negative_flow = pd.Series(0.0, index=df.index)
        
        # Calcula fluxos positivos e negativos
        flow_mask = typical_price.diff() > 0
        positive_flow[flow_mask] = money_flow[flow_mask]
        negative_flow[~flow_mask] = money_flow[~flow_mask]
        
        positive_mf = positive_flow.rolling(period).sum()
        negative_mf = negative_flow.rolling(period).sum()
        
        # Evita divisão por zero
        mfi = 100 - (100 / (1 + positive_mf / negative_mf.replace(0, 1e-9)))
        
        return mfi
    
    def _average_true_range(self, df, period=14):
        """Calcula Average True Range."""
        high_low = df['High'] - df['Low']
        high_close = (df['High'] - df['Close'].shift()).abs()
        low_close = (df['Low'] - df['Close'].shift()).abs()
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        
        return true_range.rolling(period).mean()
    
    def _bollinger_bandwidth(self, df, period=20):
        """Calcula Bollinger Bandwidth."""
        sma = df['Close'].rolling(period).mean()
        std = df['Close'].rolling(period).std()
        
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)
        
        return (upper_band - lower_band) / sma
    
    def _on_balance_volume(self, df):
        """Calcula On Balance Volume."""
        obv = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()
        return obv