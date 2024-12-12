"""
Módulo principal de predição usando Machine Learning.
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import RandomForestClassifier
from .features import FeatureEngineering
from .evaluation import ModelEvaluation

class MLPredictor:
    def __init__(self):
        """Inicializa o preditor com configurações padrão."""
        self.feature_engineering = FeatureEngineering()
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=10,
            random_state=42
        )
        self.evaluator = ModelEvaluation()
        
    def prepare_data(self, df):
        """Prepara dados para treinamento."""
        try:
            # Criar features técnicas e de preço
            tech_features = self.feature_engineering.create_technical_features(df)
            price_features = self.feature_engineering.create_price_features(df)
            
            # Combinar features
            features = pd.concat([tech_features, price_features], axis=1)
            features = features.dropna()
            
            # Criar target (1 se preço subiu, 0 se caiu)
            target = (df['Close'].shift(-1) > df['Close']).astype(int)
            target = target[features.index]
            
            return features, target
            
        except Exception as e:
            raise Exception(f"Erro na preparação dos dados: {str(e)}")
    
    def train(self, df):
        """Treina o modelo preditivo."""
        try:
            # Preparar dados
            X, y = self.prepare_data(df)
            
            if len(X) < 50:
                raise ValueError("Dados insuficientes para treinamento")
            
            # Dividir em treino e teste preservando ordem temporal
            train_size = int(len(X) * 0.8)
            X_train, X_test = X[:train_size], X[train_size:]
            y_train, y_test = y[:train_size], y[train_size:]
            
            # Treinar modelo
            self.model.fit(X_train, y_train)
            
            # Avaliar modelo
            metrics = self.evaluator.evaluate_model(
                self.model, X_train, y_train, X_test, y_test, X.columns
            )
            
            # Validação cruzada temporal
            tscv = TimeSeriesSplit(n_splits=5, test_size=int(len(X)*0.2))
            cv_scores = []
            
            for train_idx, val_idx in tscv.split(X):
                X_t, X_v = X.iloc[train_idx], X.iloc[val_idx]
                y_t, y_v = y.iloc[train_idx], y.iloc[val_idx]
                
                self.model.fit(X_t, y_t)
                score = self.model.score(X_v, y_v)
                cv_scores.append(score)
            
            metrics['cv_scores'] = cv_scores
            metrics['cv_mean'] = np.mean(cv_scores)
            metrics['cv_std'] = np.std(cv_scores)
            
            return metrics
            
        except Exception as e:
            raise Exception(f"Erro no treinamento: {str(e)}")
    
    def predict(self, df):
        """Faz previsões com o modelo treinado."""
        try:
            X, _ = self.prepare_data(df)
            return self.model.predict_proba(X)[:, 1]
        except Exception as e:
            raise Exception(f"Erro na previsão: {str(e)}")
    
    def get_trading_signals(self, df):
        """Gera sinais de trading combinando ML com análise técnica."""
        try:
            # Obter probabilidades de alta
            predictions = self.predict(df)
            
            # Inicializar série de sinais
            signals = pd.Series(index=df.index, data='black')
            
            # Calcular médias móveis para tendência
            sma_20 = df['Close'].rolling(20).mean()
            sma_50 = df['Close'].rolling(50).mean()
            trend = sma_20 > sma_50
            
            for i in range(len(df)):
                if i >= len(predictions):
                    continue
                    
                # Condições técnicas
                stoch_ok = (df['STOCH_K'].iloc[i] > 50 and 
                           df['STOCH_K'].iloc[i] > df['STOCH_K_PREV'].iloc[i])
                
                rsi_ok = (df['RSI'].iloc[i] > 50 and 
                         df['RSI'].iloc[i] > df['RSI_PREV'].iloc[i])
                
                macd_ok = (df['MACD'].iloc[i] > df['MACD_SIGNAL'].iloc[i] and 
                          df['MACD'].iloc[i] > df['MACD_PREV'].iloc[i])
                
                # Probabilidade ML
                ml_confidence = predictions[i]
                
                # Tendência
                trend_ok = trend.iloc[i]
                
                # Sinal de compra mais conservador
                if (ml_confidence > 0.7 and  # Alta confiança ML
                    all([stoch_ok, rsi_ok, macd_ok]) and  # Todos indicadores positivos
                    trend_ok):  # Tendência de alta
                    signals.iloc[i] = 'green'
                
                # Sinal de venda mais conservador
                elif (ml_confidence < 0.3 and  # Baixa confiança ML
                      not any([stoch_ok, rsi_ok, macd_ok]) and  # Todos indicadores negativos
                      not trend_ok):  # Tendência de baixa
                    signals.iloc[i] = 'red'
            
            return signals
                
        except Exception as e:
            raise Exception(f"Erro ao gerar sinais: {str(e)}")