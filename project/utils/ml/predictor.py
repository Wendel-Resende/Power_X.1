"""
Módulo principal do preditor ML.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from .features import FeatureEngineering
from .evaluation import ModelEvaluation

class MLPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_engineering = FeatureEngineering()
        self.evaluation = ModelEvaluation()
    
    def prepare_data(self, df):
        """Prepara dados para o modelo."""
        # Criar diferentes tipos de features
        tech_features = self.feature_engineering.create_technical_features(df)
        price_features = self.feature_engineering.create_price_features(df)
        lagged_features = self.feature_engineering.create_lagged_features(
            df, ['Close', 'Volume'], lags=3
        )
        
        # Combinar todas as features
        features = pd.concat([tech_features, price_features, lagged_features], axis=1)
        
        # Preparar target (retorno futuro)
        target = df['Close'].pct_change().shift(-1)
        
        # Remover NaN de ambos
        features = features.dropna()
        target = target.dropna()
        
        # Garantir alinhamento dos índices
        common_index = features.index.intersection(target.index)
        if len(common_index) == 0:
            raise ValueError("Sem dados suficientes após alinhamento")
            
        features = features.loc[common_index]
        target = target.loc[common_index]
        
        # Verificação final
        if len(features) != len(target):
            raise ValueError(f"Inconsistência nos dados: features ({len(features)}) != target ({len(target)})")
            
        return features, target
    
    def train(self, df):
        """Treina o modelo preditivo."""
        try:
            # Preparar dados
            X, y = self.prepare_data(df)
            
            if len(X) < 50:
                raise ValueError("Dados insuficientes para treinar o modelo")
            
            # Dividir dados mantendo ordem temporal
            train_size = int(len(X) * 0.8)
            X_train = X[:train_size]
            X_test = X[train_size:]
            y_train = y[:train_size]
            y_test = y[train_size:]
            
            # Escalar features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Treinar modelo
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            self.model.fit(X_train_scaled, y_train)
            
            # Avaliar modelo
            metrics = self.evaluation.evaluate_model(
                self.model,
                X_train_scaled, y_train,
                X_test_scaled, y_test,
                feature_names=X.columns
            )
            
            return metrics
            
        except Exception as e:
            raise Exception(f"Erro no treinamento: {str(e)}")
    
    def predict(self, df):
        """Faz previsões com o modelo treinado."""
        if self.model is None:
            raise ValueError("Modelo não treinado")
        
        try:
            X, _ = self.prepare_data(df)
            X_scaled = self.scaler.transform(X)
            
            return pd.Series(
                self.model.predict(X_scaled),
                index=X.index
            )
        except Exception as e:
            raise Exception(f"Erro na previsão: {str(e)}")
    
    def get_trading_signals(self, df):
        """Gera sinais de trading combinando ML com análise técnica."""
        if self.model is None:
            return pd.Series(index=df.index, data='black')
        
        try:
            predictions = self.predict(df)
            signals = pd.Series(index=df.index, data='black')
            
            for i in range(1, len(df)):
                if i >= len(df.index):
                    continue
                    
                idx = df.index[i]
                if idx not in predictions.index:
                    continue
                
                # Condições técnicas
                tech_conditions = [
                    (df['STOCH_K'].iloc[i] > 50) and (df['STOCH_K'].iloc[i] > df['STOCH_K'].iloc[i-1]),
                    (df['RSI'].iloc[i] > 50) and (df['RSI'].iloc[i] > df['RSI'].iloc[i-1]),
                    (df['MACD'].iloc[i] > df['MACD_SIGNAL'].iloc[i]) and (df['MACD'].iloc[i] > df['MACD'].iloc[i-1])
                ]
                
                conditions_met = sum(tech_conditions)
                ml_signal = predictions.loc[idx] > 0
                
                if conditions_met >= 2 and ml_signal:
                    signals.iloc[i] = 'green'
                elif conditions_met <= 1 and not ml_signal:
                    signals.iloc[i] = 'red'
            
            return signals
            
        except Exception as e:
            print(f"Erro ao gerar sinais ML: {str(e)}")
            return pd.Series(index=df.index, data='black')