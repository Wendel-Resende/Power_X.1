"""
Módulo principal do preditor ML.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from .features import FeatureEngineering
from .evaluation import ModelEvaluation

class MLPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_engineering = FeatureEngineering()
        self.evaluation = ModelEvaluation()
    
    def prepare_data(self, df):
        """
        Prepara os dados para treinamento.
        
        Args:
            df: DataFrame com dados históricos e indicadores
            
        Returns:
            tuple: (X, y) com features e target
        """
        try:
            # Criar features técnicas
            tech_features = self.feature_engineering.create_technical_features(df)
            
            # Criar features de preço
            price_features = self.feature_engineering.create_price_features(df)
            
            # Combinar todas as features
            X = pd.concat([tech_features, price_features], axis=1)
            
            # Target: retorno futuro
            y = df['Close'].pct_change().shift(-1)
            
            # Remover dados incompletos
            valid_idx = ~(X.isna().any(axis=1) | y.isna())
            X = X[valid_idx]
            y = y[valid_idx]
            
            return X, y
            
        except Exception as e:
            raise Exception(f"Erro ao preparar dados: {str(e)}")
    
    def train(self, df):
        """
        Treina o modelo preditivo.
        
        Args:
            df: DataFrame com dados históricos e indicadores
            
        Returns:
            dict: Métricas de avaliação do modelo
        """
        try:
            # Preparar dados
            X, y = self.prepare_data(df)
            
            if len(X) < 50:
                raise ValueError("Dados insuficientes para treinar o modelo")
            
            # Usar validação cruzada temporal
            tscv = TimeSeriesSplit(n_splits=5, test_size=int(len(X) * 0.2))
            
            best_model = None
            best_score = float('-inf')
            
            for train_idx, test_idx in tscv.split(X):
                X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
                y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
                
                # Escalar features
                X_train_scaled = self.scaler.fit_transform(X_train)
                X_test_scaled = self.scaler.transform(X_test)
                
                # Treinar modelo
                model = RandomForestRegressor(
                    n_estimators=200,
                    max_depth=8,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    random_state=42
                )
                model.fit(X_train_scaled, y_train)
                
                # Avaliar modelo
                score = model.score(X_test_scaled, y_test)
                if score > best_score:
                    best_score = score
                    best_model = model
            
            self.model = best_model
            
            # Avaliar modelo final
            metrics = self.evaluation.evaluate_model(
                self.model,
                X_train_scaled, y_train,
                X_test_scaled, y_test,
                feature_names=X.columns
            )
            
            return metrics
            
        except Exception as e:
            raise Exception(f"Erro no treinamento: {str(e)}")
    
    def get_trading_signals(self, df):
        """
        Gera sinais de trading combinando análise técnica e ML.
        
        Args:
            df: DataFrame com dados e indicadores
            
        Returns:
            pd.Series: Sinais de trading ('green', 'red', 'black')
        """
        try:
            if self.model is None:
                raise ValueError("Modelo não treinado")
            
            # Preparar dados
            X, _ = self.prepare_data(df)
            
            # Fazer previsões
            X_scaled = self.scaler.transform(X)
            predictions = self.model.predict(X_scaled)
            
            # Criar sinais baseados nas previsões e indicadores técnicos
            signals = pd.Series(index=df.index, data='black')
            
            for i in range(len(df)):
                if i >= len(predictions):
                    continue
                    
                # Condições técnicas
                stoch_ok = (df['STOCH_K'].iloc[i] > 50) and (df['STOCH_K'].iloc[i] > df['STOCH_K_PREV'].iloc[i])
                rsi_ok = (df['RSI'].iloc[i] > 50) and (df['RSI'].iloc[i] > df['RSI_PREV'].iloc[i])
                macd_ok = (df['MACD'].iloc[i] > df['MACD_SIGNAL'].iloc[i]) and (df['MACD'].iloc[i] > df['MACD_PREV'].iloc[i])
                
                # Combinar sinais técnicos com previsão ML
                if predictions[i] > 0 and all([stoch_ok, rsi_ok, macd_ok]):
                    signals.iloc[i] = 'green'
                elif predictions[i] < 0 and not any([stoch_ok, rsi_ok, macd_ok]):
                    signals.iloc[i] = 'red'
            
            return signals
            
        except Exception as e:
            raise Exception(f"Erro ao gerar sinais: {str(e)}")