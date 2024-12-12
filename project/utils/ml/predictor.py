"""
Módulo principal de predição usando Machine Learning.
"""
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from .features.builder import FeatureBuilder
import pandas as pd
import numpy as np

class MLPredictor:
    def __init__(self):
        """Inicializa o preditor com modelo ensemble."""
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=10,
            class_weight='balanced',
            random_state=42
        )
        self.scaler = StandardScaler()
        self.feature_builder = FeatureBuilder()
        self.feature_names = None
    
    def prepare_data(self, df):
        """Prepara dados para treinamento."""
        try:
            # Usar o FeatureBuilder para criar features
            features = self.feature_builder.build_features(df)
            self.feature_names = features.columns
            
            # Target (retorno futuro ajustado por volatilidade)
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
            tscv = TimeSeriesSplit(n_splits=3, test_size=int(len(X)*0.2))
            splits = list(tscv.split(X))
            train_idx, test_idx = splits[-1]
            
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
            
            # Normalizar features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Treinar modelo
            self.model.fit(X_train_scaled, y_train)
            
            # Calcular métricas
            train_score = self.model.score(X_train_scaled, y_train)
            test_score = self.model.score(X_test_scaled, y_test)
            
            # Feature importance
            importance_df = pd.DataFrame({
                'feature': self.feature_names,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            return {
                'train_score': train_score,
                'test_score': test_score,
                'feature_importance': importance_df,
                'test_rmse': np.sqrt(((y_test - self.model.predict(X_test_scaled)) ** 2).mean())
            }
            
        except Exception as e:
            raise Exception(f"Erro no treinamento: {str(e)}")
    
    def predict(self, df):
        """Faz previsões com o modelo treinado."""
        try:
            X, _ = self.prepare_data(df)
            X_scaled = self.scaler.transform(X)
            return self.model.predict_proba(X_scaled)[:, 1]
        except Exception as e:
            raise Exception(f"Erro na previsão: {str(e)}")
    
    def get_trading_signals(self, df):
        """Gera sinais de trading combinando ML com indicadores técnicos."""
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
                
                # Combinar ML com sinais técnicos
                if (probabilities[i] > 0.7 and tech_signals >= 2 and 
                    trend.iloc[i] and vol_percentile.iloc[i] < 0.8):
                    signals.iloc[i] = 'green'
                elif (probabilities[i] < 0.3 and tech_signals <= 1):
                    signals.iloc[i] = 'red'
            
            return signals
            
        except Exception as e:
            raise Exception(f"Erro ao gerar sinais: {str(e)}")