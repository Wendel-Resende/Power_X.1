"""
Módulo para construção do conjunto completo de features.
"""
from .price import create_returns_features, create_moving_averages
from .technical import create_momentum_features, create_volume_features
import pandas as pd

class FeatureBuilder:
    def __init__(self):
        """Inicializa o construtor de features."""
        self.features = {}
    
    def build_features(self, df):
        """Constrói todas as features."""
        # Features de preço
        self.features['returns'] = create_returns_features(df)
        self.features['moving_averages'] = create_moving_averages(df)
        
        # Features técnicas
        self.features['momentum'] = create_momentum_features(df)
        self.features['volume'] = create_volume_features(df)
        
        # Combinar todas as features
        features_df = pd.concat([v for v in self.features.values()], axis=1)
        
        # Remover valores ausentes
        features_df = features_df.fillna(method='bfill').fillna(method='ffill')
        
        return features_df