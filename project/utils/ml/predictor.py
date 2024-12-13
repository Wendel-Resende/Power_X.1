"""
Módulo principal de predição usando XGBoost.
"""
from sklearn.model_selection import TimeSeriesSplit
import pandas as pd
import numpy as np
from .models.xgboost_model import XGBoostModel
from .feature_processor import FeatureProcessor
from .signal_generator import SignalGenerator

class MLPredictor:
    def __init__(self):
        """Inicializa o preditor com XGBoost."""
        self.model = XGBoostModel()
        self.feature_processor = FeatureProcessor()
        self.signal_generator = SignalGenerator()
        self.feature_names = None
    
    def prepare_data(self, df):
        """Prepara dados para treinamento."""
        try:
            features = self.feature_processor.process_features(df)
            self.feature_names = features.columns
            
            # Target mais suave usando retornos normalizados
            returns = df['Close'].pct_change()
            volatility = returns.rolling(20).std()
            target = ((returns.shift(-1) / volatility) > returns.mean()).astype(int)
            target = target[features.index]
            
            return features, target
            
        except Exception as e:
            raise Exception(f"Erro na preparação dos dados: {str(e)}")
    
    def train(self, df):
        """Treina o modelo com validação temporal."""
        try:
            X, y = self.prepare_data(df)
            
            if len(X) < 50:
                raise ValueError("Dados insuficientes para treinamento")
            
            # Validação temporal
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
    
    def get_trading_signals(self, df):
        """Gera sinais de trading."""
        try:
            probabilities = self.model.predict_proba(
                self.feature_processor.process_features(df)
            )
            
            signals = pd.Series(index=df.index, data='black')
            
            for i in range(len(df)):
                if i >= len(probabilities):
                    continue
                
                indicators = {
                    'rsi': df['RSI'].iloc[i],
                    'rsi_prev': df['RSI_PREV'].iloc[i],
                    'macd': df['MACD'].iloc[i],
                    'macd_signal': df['MACD_SIGNAL'].iloc[i],
                    'macd_prev': df['MACD_PREV'].iloc[i],
                    'stoch_k': df['STOCH_K'].iloc[i],
                    'stoch_d': df['STOCH_D'].iloc[i],
                    'stoch_k_prev': df['STOCH_K_PREV'].iloc[i]
                }
                
                signals.iloc[i] = self.signal_generator.generate_signal(
                    indicators,
                    probabilities[i]
                )
            
            return signals
            
        except Exception as e:
            raise Exception(f"Erro ao gerar sinais: {str(e)}")