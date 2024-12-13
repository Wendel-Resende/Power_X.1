"""
Módulo para processamento de features simplificado.
"""
import pandas as pd
import numpy as np

class FeatureProcessor:
    def __init__(self):
        """Inicializa o processador com features simplificadas."""
        self.windows = [5, 10, 20]  # Janelas temporais reduzidas
        
    def create_price_features(self, df):
        """Cria features básicas de preço."""
        features = pd.DataFrame(index=df.index)
        
        # Retornos
        features['Daily_Return'] = df['Close'].pct_change()
        
        for window in self.windows:
            # Retornos por período
            features[f'Returns_{window}d'] = df['Close'].pct_change(window)
            
            # Média móvel de preço
            features[f'Price_MA_{window}'] = df['Close'].rolling(window).mean()
            
            # Volatilidade
            features[f'Volatility_{window}d'] = features['Daily_Return'].rolling(window).std()
        
        return features
        
    def create_volume_features(self, df):
        """Cria features básicas de volume."""
        features = pd.DataFrame(index=df.index)
        
        # Volume diário
        features['Daily_Volume_Change'] = df['Volume'].pct_change()
        
        for window in self.windows:
            # Média móvel de volume
            features[f'Volume_MA_{window}'] = df['Volume'].rolling(window).mean()
            
            # Volume relativo
            features[f'Volume_Ratio_{window}'] = df['Volume'] / features[f'Volume_MA_{window}']
        
        return features
    
    def process_features(self, df):
        """Processa features simplificadas."""
        try:
            # Criar features básicas
            price_features = self.create_price_features(df)
            volume_features = self.create_volume_features(df)
            
            # Combinar features
            features = pd.concat([price_features, volume_features], axis=1)
            
            # Preencher valores ausentes
            features = features.fillna(method='bfill').fillna(method='ffill')
            
            return features
            
        except Exception as e:
            raise Exception(f"Erro ao processar features: {str(e)}")