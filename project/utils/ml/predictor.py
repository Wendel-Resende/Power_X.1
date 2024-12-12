"""
Módulo principal de predição usando XGBoost.
"""
from sklearn.model_selection import TimeSeriesSplit
import pandas as pd
import numpy as np
from .models.xgboost_model import XGBoostModel
from .features.builder import FeatureBuilder

class MLPredictor:
    def __init__(self):
        """Inicializa o preditor com XGBoost."""
        self.model = XGBoostModel()
        self.feature_builder = FeatureBuilder()
        self.feature_names = None
    
    def prepare_data(self, df):
        """Prepara dados para treinamento."""
        try:
            features = self.feature_builder.build_features(df)
            self.feature_names = features.columns
            
            returns = df['Close'].pct_change()
            volatility = returns.rolling(20).std()
            target = ((returns.shift(-1) / volatility) > returns.mean()).astype(int)
            target = target[features.index]
            
            features = features.fillna(method='bfill').fillna(method='ffill')
            target = target.fillna(method='bfill').fillna(0)
            
            return features, target
            
        except Exception as e:
            raise Exception(f"Erro na preparação dos dados: {str(e)}")
    
    def train(self, df):
        """Treina o modelo com validação temporal."""
        try:
            X, y = self.prepare_data(df)
            
            if len(X) < 50:
                raise ValueError("Dados insuficientes para treinamento")
            
            tscv = TimeSeriesSplit(n_splits=3, test_size=int(len(X)*0.2))
            splits = list(tscv.split(X))
            train_idx, test_idx = splits[-1]
            
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
            
            self.model.fit(X_train, y_train, X_test, y_test)
            
            train_pred = self.model.predict_proba(X_train)
            test_pred = self.model.predict_proba(X_test)
            
            train_score = ((train_pred > 0.5) == y_train).mean()
            test_score = ((test_pred > 0.5) == y_test).mean()
            
            importance_df = self.model.get_feature_importance(self.feature_names)
            
            return {
                'train_score': train_score,
                'test_score': test_score,
                'feature_importance': importance_df,
                'test_rmse': np.sqrt(((y_test - (test_pred > 0.5)) ** 2).mean())
            }
            
        except Exception as e:
            raise Exception(f"Erro no treinamento: {str(e)}")
    
    def predict(self, df):
        """Faz previsões com o modelo treinado."""
        try:
            X, _ = self.prepare_data(df)
            return self.model.predict_proba(X)
        except Exception as e:
            raise Exception(f"Erro na previsão: {str(e)}")
    
    def get_trading_signals(self, df):
        """Gera sinais de trading com regras mais flexíveis."""
        try:
            probabilities = self.predict(df)
            signals = pd.Series(index=df.index, data='black')
            
            for i in range(len(df)):
                if i >= len(probabilities):
                    continue
                
                # Indicadores técnicos
                rsi = df['RSI'].iloc[i]
                rsi_prev = df['RSI_PREV'].iloc[i]
                macd = df['MACD'].iloc[i]
                macd_signal = df['MACD_SIGNAL'].iloc[i]
                macd_prev = df['MACD_PREV'].iloc[i]
                stoch_k = df['STOCH_K'].iloc[i]
                stoch_d = df['STOCH_D'].iloc[i]
                stoch_k_prev = df['STOCH_K_PREV'].iloc[i]
                
                # Condições mais flexíveis
                rsi_ok = (rsi > 40 and rsi_prev < rsi)  # RSI subindo e acima de 40
                macd_ok = (macd > macd_signal or macd > macd_prev)  # MACD cruzando ou subindo
                stoch_ok = (stoch_k > stoch_d or stoch_k > stoch_k_prev)  # Stoch cruzando ou subindo
                
                # Sistema de pontuação
                score = 0
                if rsi_ok: score += 1
                if macd_ok: score += 1
                if stoch_ok: score += 1
                
                # Probabilidade do modelo ML
                ml_prob = probabilities[i]
                
                # Regras de sinalização mais flexíveis
                if ml_prob > 0.55:  # Reduzido threshold
                    if score >= 2:  # Apenas 2 indicadores precisam confirmar
                        signals.iloc[i] = 'green'
                elif ml_prob < 0.45:  # Aumentado threshold
                    if score <= 1:  # Apenas 1 indicador negativo já sinaliza
                        signals.iloc[i] = 'red'
            
            return signals
            
        except Exception as e:
            raise Exception(f"Erro ao gerar sinais: {str(e)}")