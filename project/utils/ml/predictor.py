"""
Módulo principal de predição usando Machine Learning.
"""
from .models import EnsembleModel
from .features import FeatureEngineering
from .evaluation import ModelEvaluation
import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit

class MLPredictor:
    def __init__(self):
        """Inicializa o preditor com modelo ensemble."""
        self.model = EnsembleModel()
        self.feature_engineering = FeatureEngineering()
        self.evaluator = ModelEvaluation()
    
    def prepare_data(self, df):
        """Prepara dados para treinamento com features avançadas."""
        try:
            # Criar features
            price_features = self.feature_engineering.create_price_features(df)
            tech_features = self.feature_engineering.create_technical_features(df)
            
            # Combinar features
            features = pd.concat([price_features, tech_features], axis=1)
            features = features.dropna()
            
            # Target mais sofisticado (considera retorno ajustado por volatilidade)
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
            
            # Split temporal
            tscv = TimeSeriesSplit(n_splits=5, test_size=int(len(X)*0.2))
            splits = list(tscv.split(X))
            train_idx, test_idx = splits[-1]
            
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
            
            # Treinar modelo
            self.model.fit(X_train, y_train)
            
            # Avaliar modelo
            metrics = self.evaluator.evaluate_model(
                self.model, X_train, y_train, X_test, y_test, X.columns
            )
            
            # Adicionar métricas de trading
            predictions = self.model.predict(X_test)
            returns = df['Close'].pct_change().iloc[test_idx]
            trading_metrics = self.evaluator.calculate_trading_metrics(predictions, returns)
            metrics.update(trading_metrics)
            
            return metrics
            
        except Exception as e:
            raise Exception(f"Erro no treinamento: {str(e)}")
    
    def predict(self, df):
        """Faz previsões com o modelo ensemble."""
        try:
            X, _ = self.prepare_data(df)
            return self.model.predict_proba(X)
        except Exception as e:
            raise Exception(f"Erro na previsão: {str(e)}")
    
    def get_trading_signals(self, df):
        """Gera sinais de trading com filtros de tendência e volatilidade."""
        try:
            predictions = self.predict(df)
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
                if i >= len(predictions):
                    continue
                
                # Condições técnicas e ML
                signal = self._get_combined_signal(df.iloc[i], predictions[i])
                
                # Filtros adicionais
                if trend.iloc[i] and vol_percentile.iloc[i] < 0.8:  # Tendência de alta e volatilidade controlada
                    signals.iloc[i] = signal
            
            return signals
            
        except Exception as e:
            raise Exception(f"Erro ao gerar sinais: {str(e)}")
    
    def _get_combined_signal(self, row, ml_prob):
        """Combina sinais técnicos com previsão ML."""
        # Condições técnicas
        stoch_ok = (row['STOCH_K'] > 50 and row['STOCH_K'] > row['STOCH_K_PREV'])
        rsi_ok = (row['RSI'] > 50 and row['RSI'] > row['RSI_PREV'])
        macd_ok = (row['MACD'] > row['MACD_SIGNAL'] and row['MACD'] > row['MACD_PREV'])
        
        # Contagem de sinais positivos
        tech_signals = sum([stoch_ok, rsi_ok, macd_ok])
        
        # Combinar com ML
        if ml_prob > 0.7 and tech_signals >= 2:
            return 'green'
        elif ml_prob < 0.3 and tech_signals <= 1:
            return 'red'
        return 'black'