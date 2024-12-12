"""
Módulo principal do preditor ML.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
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
        """Prepara os dados para treinamento."""
        try:
            # Criar features técnicas
            tech_features = self.feature_engineering.create_technical_features(df)
            
            # Criar features de preço
            price_features = self.feature_engineering.create_price_features(df)
            
            # Combinar features
            X = pd.concat([tech_features, price_features], axis=1)
            
            # Target: direção do movimento (classificação binária)
            returns = df['Close'].pct_change()
            y = (returns.shift(-1) > 0).astype(int)  # 1 se subiu, 0 se caiu
            
            # Remover dados incompletos
            valid_idx = ~(X.isna().any(axis=1) | y.isna())
            X = X[valid_idx]
            y = y[valid_idx]
            
            return X, y
            
        except Exception as e:
            raise Exception(f"Erro ao preparar dados: {str(e)}")
    
    def train(self, df):
        """Treina o modelo preditivo."""
        try:
            # Preparar dados
            X, y = self.prepare_data(df)
            
            if len(X) < 50:
                raise ValueError("Dados insuficientes para treinar o modelo")
            
            # Usar janela móvel para treinamento (últimos 6 meses)
            window_size = min(126, len(X) // 2)  # ~6 meses de trading ou metade dos dados
            X = X.iloc[-window_size:]
            y = y.iloc[-window_size:]
            
            # Dividir em treino/teste (80/20)
            train_size = int(len(X) * 0.8)
            X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
            y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]
            
            # Escalar features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Treinar modelo de classificação
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=4,  # Reduzido para evitar overfitting
                min_samples_split=10,
                min_samples_leaf=5,
                class_weight='balanced',  # Lidar com desbalanceamento
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
    
    def get_trading_signals(self, df):
        """Gera sinais de trading."""
        try:
            if self.model is None:
                raise ValueError("Modelo não treinado")
            
            # Preparar dados
            X, _ = self.prepare_data(df)
            
            # Fazer previsões
            X_scaled = self.scaler.transform(X)
            predictions = self.model.predict_proba(X_scaled)[:, 1]  # Probabilidade de subida
            
            # Criar sinais
            signals = pd.Series(index=df.index, data='black')
            
            for i in range(len(df)):
                if i >= len(predictions):
                    continue
                    
                # Condições técnicas
                stoch_ok = (df['STOCH_K'].iloc[i] > 50) and (df['STOCH_K'].iloc[i] > df['STOCH_K_PREV'].iloc[i])
                rsi_ok = (df['RSI'].iloc[i] > 50) and (df['RSI'].iloc[i] > df['RSI_PREV'].iloc[i])
                macd_ok = (df['MACD'].iloc[i] > df['MACD_SIGNAL'].iloc[i]) and (df['MACD'].iloc[i] > df['MACD_PREV'].iloc[i])
                
                # Combinar sinais técnicos com previsão ML
                ml_confidence = predictions[i]
                
                if ml_confidence > 0.6 and all([stoch_ok, rsi_ok, macd_ok]):
                    signals.iloc[i] = 'green'
                elif ml_confidence < 0.4 and not any([stoch_ok, rsi_ok, macd_ok]):
                    signals.iloc[i] = 'red'
            
            return signals
            
        except Exception as e:
            raise Exception(f"Erro ao gerar sinais: {str(e)}")