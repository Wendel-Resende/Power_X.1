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
            # Construir features usando o FeatureBuilder
            features = self.feature_builder.build_features(df)
            self.feature_names = features.columns
            
            # Target (retorno futuro ajustado por volatilidade)
            returns = df['Close'].pct_change()
            volatility = returns.rolling(20).std()
            target = ((returns.shift(-1) / volatility) > returns.mean()).astype(int)
            target = target[features.index]
            
            # Remover valores ausentes
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
            
            # Split temporal com 3 folds
            tscv = TimeSeriesSplit(n_splits=3, test_size=int(len(X)*0.2))
            splits = list(tscv.split(X))
            train_idx, test_idx = splits[-1]
            
            # Separar dados de treino e teste
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
            
            # Treinar modelo
            self.model.fit(X_train, y_train, X_test, y_test)
            
            # Calcular métricas
            train_pred = self.model.predict_proba(X_train)
            test_pred = self.model.predict_proba(X_test)
            
            train_score = ((train_pred > 0.5) == y_train).mean()
            test_score = ((test_pred > 0.5) == y_test).mean()
            
            # Feature importance
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
        """Gera sinais de trading combinando XGBoost com indicadores técnicos."""
        try:
            # Obter probabilidades do modelo
            probabilities = self.predict(df)
            
            # Inicializar série de sinais
            signals = pd.Series(index=df.index, data='black')
            
            # Calcular tendência
            sma_20 = df['Close'].rolling(20).mean()
            sma_50 = df['Close'].rolling(50).mean()
            trend = sma_20 > sma_50
            
            # Calcular volatilidade
            volatility = df['Close'].pct_change().rolling(20).std()
            vol_percentile = volatility.rolling(100).apply(
                lambda x: pd.Series(x).rank(pct=True).iloc[-1]
            )
            
            for i in range(len(df)):
                if i >= len(probabilities):
                    continue
                    
                # Condições técnicas
                stoch_ok = (df['STOCH_K'].iloc[i] > 50 and 
                           df['STOCH_K'].iloc[i] > df['STOCH_K_PREV'].iloc[i])
                rsi_ok = (df['RSI'].iloc[i] > 50 and 
                         df['RSI'].iloc[i] > df['RSI_PREV'].iloc[i])
                macd_ok = (df['MACD'].iloc[i] > df['MACD_SIGNAL'].iloc[i] and 
                          df['MACD'].iloc[i] > df['MACD_PREV'].iloc[i])
                
                # Contagem de sinais técnicos positivos
                tech_signals = sum([stoch_ok, rsi_ok, macd_ok])
                
                # Combinar XGBoost com sinais técnicos
                if (probabilities[i] > 0.7 and tech_signals >= 2 and 
                    trend.iloc[i] and vol_percentile.iloc[i] < 0.8):
                    signals.iloc[i] = 'green'
                elif (probabilities[i] < 0.3 and tech_signals <= 1):
                    signals.iloc[i] = 'red'
            
            return signals
            
        except Exception as e:
            raise Exception(f"Erro ao gerar sinais: {str(e)}")