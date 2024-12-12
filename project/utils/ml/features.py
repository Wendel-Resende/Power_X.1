"""
Módulo para engenharia de features.
"""
import pandas as pd

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
        if 'MACD' in df.columns:
            macd_range = df['MACD'].max() - df['MACD'].min()
            if macd_range > 0:
                features['MACD'] = (df['MACD'] - df['MACD'].min()) / macd_range
                features['MACD_SIGNAL'] = (df['MACD_SIGNAL'] - df['MACD_SIGNAL'].min()) / macd_range
        
        return features
    
    @staticmethod
    def create_price_features(df):
        """Cria features baseadas em preço e volume."""
        features = pd.DataFrame(index=df.index)
        
        # Normalizar preço e volume
        for col in ['Close', 'Volume']:
            if col in df.columns:
                col_range = df[col].max() - df[col].min()
                if col_range > 0:
                    features[f'{col}_Norm'] = (df[col] - df[col].min()) / col_range
        
        return features
    
    @staticmethod
    def create_lagged_features(df, columns, lags):
        """Cria features defasadas."""
        features = pd.DataFrame(index=df.index)
        
        for col in columns:
            if col in df.columns:
                for lag in range(1, lags + 1):
                    features[f'{col}_lag_{lag}'] = df[col].shift(lag)
        
        return features