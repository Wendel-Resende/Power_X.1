"""
Módulo principal de predição usando Machine Learning.
"""
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
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
        self.feature_names = None
    
    def prepare_data(self, df):
        """Prepara dados para treinamento."""
        try:
            features = pd.DataFrame(index=df.index)
            
            # Features de preço
            for period in [1, 3, 5, 10, 20]:
                features[f'Returns_{period}d'] = df['Close'].pct_change(period)
                features[f'Volume_{period}d'] = df['Volume'].pct_change(period)
            
            # Features técnicas
            features['STOCH_K'] = df['STOCH_K']
            features['STOCH_D'] = df['STOCH_D']
            features['RSI'] = df['RSI']
            features['MACD'] = df['MACD']
            features['MACD_SIGNAL'] = df['MACD_SIGNAL']
            
            # Features de volatilidade
            features['ATR'] = df['ATR']
            features['BB_Width'] = (df['BB_UPPER'] - df['BB_LOWER']) / df['BB_MIDDLE']
            
            # Features de volume
            features['OBV'] = df['OBV']
            features['MFI'] = df['MFI']
            
            # Remover valores ausentes
            features = features.dropna()
            
            # Target (retorno futuro ajustado por volatilidade)
            returns = df['Close'].pct_change()
            volatility = returns.rolling(20).std()
            target = ((returns.shift(-1) / volatility) > returns.mean()).astype(int)
            target = target[features.index]
            
            self.feature_names = features.columns
            
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