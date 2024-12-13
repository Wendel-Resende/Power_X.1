"""
Módulo para processamento de features.
"""
import pandas as pd
import numpy as np

class FeatureProcessor:
    def __init__(self):
        """Inicializa o processador de features."""
        self.price_windows = [1, 3, 5, 10, 20]
        self.volume_windows = [5, 10, 20, 50]
        
    def create_returns_features(self, df):
        """Cria features de retorno."""
        features = pd.DataFrame(index=df.index)
        
        for window in self.price_windows:
            features[f'Returns_{window}d'] = df['Close'].pct_change(window)
            features[f'Volatility_{window}d'] = df['Close'].pct_change().rolling(window).std()
            
        return features
        
    def create_volume_features(self, df):
        """Cria features de volume."""
        features = pd.DataFrame(index=df.index)
        
        for window in self.volume_windows:
            features[f'Volume_SMA_{window}'] = df['Volume'].rolling(window).mean()
            features[f'Volume_Ratio_{window}'] = df['Volume'] / features[f'Volume_SMA_{window}']
            
        return features
        
    def create_technical_features(self, df):
        """Cria features técnicas."""
        features = pd.DataFrame(index=df.index)
        
        # RSI e suas variações
        features['RSI'] = df['RSI']
        features['RSI_MA'] = df['RSI'].rolling(10).mean()
        
        # MACD e suas variações
        features['MACD_Hist'] = df['MACD'] - df['MACD_SIGNAL']
        features['MACD_Hist_MA'] = features['MACD_Hist'].rolling(5).mean()
        
        # Stochastic e suas variações
        features['STOCH_Diff'] = df['STOCH_K'] - df['STOCH_D']
        features['STOCH_MA'] = features['STOCH_Diff'].rolling(5).mean()
        
        return features
        
    def process_features(self, df):
        """Processa todas as features."""
        returns_features = self.create_returns_features(df)
        volume_features = self.create_volume_features(df)
        technical_features = self.create_technical_features(df)
        
        features = pd.concat([
            returns_features,
            volume_features,
            technical_features
        ], axis=1)
        
        return features.fillna(method='bfill').fillna(method='ffill')