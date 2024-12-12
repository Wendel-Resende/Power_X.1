"""
Módulo para engenharia de features.
"""
import pandas as pd
import numpy as np

class FeatureEngineering:
    @staticmethod
    def create_technical_features(df):
        """Cria features baseadas em indicadores técnicos."""
        features = pd.DataFrame(index=df.index)
        
        # Normalizar indicadores
        features['STOCH_K'] = df['STOCH_K'] / 100
        features['STOCH_D'] = df['STOCH_D'] / 100
        features['RSI'] = df['RSI'] / 100
        
        # Normalizar MACD
        macd_range = df['MACD'].max() - df['MACD'].min()
        if macd_range > 0:
            features['MACD'] = (df['MACD'] - df['MACD'].min()) / macd_range
            features['MACD_SIGNAL'] = (df['MACD_SIGNAL'] - df['MACD_SIGNAL'].min()) / macd_range
        
        # Adicionar diferenças
        features['STOCH_DIFF'] = features['STOCH_K'] - features['STOCH_K'].shift(1)
        features['RSI_DIFF'] = features['RSI'] - features['RSI'].shift(1)
        features['MACD_DIFF'] = features['MACD'] - features['MACD_SIGNAL']
        
        return features
    
    @staticmethod
    def create_price_features(df):
        """Cria features baseadas em preço e volume."""
        features = pd.DataFrame(index=df.index)
        
        # Normalizar preço
        close_min = df['Close'].rolling(window=20).min()
        close_max = df['Close'].rolling(window=20).max()
        features['Close_Norm'] = (df['Close'] - close_min) / (close_max - close_min)
        
        # Normalizar volume
        volume_min = df['Volume'].rolling(window=20).min()
        volume_max = df['Volume'].rolling(window=20).max()
        features['Volume_Norm'] = (df['Volume'] - volume_min) / (volume_max - volume_min)
        
        # Retornos
        features['Returns'] = df['Close'].pct_change()
        features['Returns_Vol'] = features['Returns'].rolling(window=20).std()
        
        return features
    
    @staticmethod
    def create_lagged_features(df, columns, lags=3):
        """Cria features defasadas."""
        features = pd.DataFrame(index=df.index)
        
        for col in columns:
            if col in df.columns:
                # Usar rolling mean para suavizar
                smoothed = df[col].rolling(window=3).mean()
                for lag in range(1, lags + 1):
                    features[f'{col}_lag_{lag}'] = smoothed.shift(lag)
        
        return features

    @staticmethod
    def align_features_target(features, target):
        """Alinha features e target e remove NaN."""
        # Encontrar índices comuns
        common_index = features.index.intersection(target.index)
        
        if len(common_index) == 0:
            raise ValueError("Sem dados suficientes após alinhamento")
        
        # Alinhar dados
        features = features.loc[common_index]
        target = target.loc[common_index]
        
        # Remover NaN
        valid_idx = ~(features.isna().any(axis=1) | target.isna())
        features = features[valid_idx]
        target = target[valid_idx]
        
        return features, target