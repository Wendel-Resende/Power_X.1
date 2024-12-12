"""
Módulo para engenharia de features.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import RobustScaler

class FeatureEngineering:
    def __init__(self):
        self.scaler = RobustScaler()
    
    def create_technical_features(self, df):
        """Cria features baseadas em indicadores técnicos."""
        features = pd.DataFrame(index=df.index)
        
        # Usar RobustScaler para lidar com outliers
        tech_data = df[['STOCH_K', 'STOCH_D', 'RSI', 'MACD', 'MACD_SIGNAL']].copy()
        scaled_tech = self.scaler.fit_transform(tech_data)
        tech_data_scaled = pd.DataFrame(
            scaled_tech, 
            columns=tech_data.columns,
            index=tech_data.index
        )
        
        features = pd.concat([features, tech_data_scaled], axis=1)
        
        # Adicionar features de momentum
        features['STOCH_DIFF'] = features['STOCH_K'] - features['STOCH_K'].shift(1)
        features['RSI_DIFF'] = features['RSI'] - features['RSI'].shift(1)
        features['MACD_DIFF'] = features['MACD'] - features['MACD_SIGNAL']
        
        return features
    
    def create_price_features(self, df):
        """Cria features baseadas em preço e volume."""
        features = pd.DataFrame(index=df.index)
        
        # Calcular retornos em diferentes períodos
        for period in [1, 3, 5, 10, 20]:
            features[f'Returns_{period}d'] = df['Close'].pct_change(period)
            features[f'Volume_{period}d'] = df['Volume'].pct_change(period)
        
        # Adicionar volatilidade
        features['Volatility'] = df['Close'].pct_change().rolling(20).std()
        
        # Normalizar features
        return pd.DataFrame(
            self.scaler.fit_transform(features),
            columns=features.columns,
            index=features.index
        )