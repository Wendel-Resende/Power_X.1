"""
Módulo de estratégia preditiva usando Machine Learning.
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor

class MLPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        
    def prepare_features(self, df):
        """Prepara features para o modelo."""
        features = pd.DataFrame(index=df.index)
        
        # Features técnicas
        features['STOCH_K'] = df['STOCH_K'] / 100  # Normalizar
        features['STOCH_D'] = df['STOCH_D'] / 100
        features['RSI'] = df['RSI'] / 100
        features['MACD'] = (df['MACD'] - df['MACD'].min()) / (df['MACD'].max() - df['MACD'].min())
        features['MACD_SIGNAL'] = (df['MACD_SIGNAL'] - df['MACD_SIGNAL'].min()) / (df['MACD_SIGNAL'].max() - df['MACD_SIGNAL'].min())
        
        # Features de preço
        features['Close_Norm'] = (df['Close'] - df['Close'].min()) / (df['Close'].max() - df['Close'].min())
        features['Volume_Norm'] = (df['Volume'] - df['Volume'].min()) / (df['Volume'].max() - df['Volume'].min())
        
        # Features defasadas
        for i in range(1, 4):
            features[f'Close_{i}'] = features['Close_Norm'].shift(i)
            features[f'Volume_{i}'] = features['Volume_Norm'].shift(i)
        
        return features.dropna()
    
    def prepare_target(self, df):
        """Prepara o target (retorno futuro)."""
        return df['Close'].pct_change().shift(-1).dropna()
    
    def train(self, df):
        """Treina o modelo preditivo."""
        # Preparar dados
        X = self.prepare_features(df)
        y = self.prepare_target(df)
        
        # Alinhar índices
        common_index = X.index.intersection(y.index)
        X = X.loc[common_index]
        y = y.loc[common_index]
        
        # Dividir dados
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )
        
        # Treinar modelo
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.model.fit(X_train, y_train)
        
        # Calcular métricas
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        return {
            'train_score': train_score,
            'test_score': test_score,
            'feature_importance': pd.DataFrame({
                'feature': X.columns,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
        }
    
    def predict(self, df):
        """Faz previsões com o modelo treinado."""
        if self.model is None:
            raise ValueError("Modelo não treinado")
        
        X = self.prepare_features(df)
        predictions = self.model.predict(X)
        
        return pd.Series(predictions, index=X.index)
    
    def get_trading_signals(self, df):
        """Gera sinais de trading combinando ML com análise técnica."""
        if self.model is None:
            return pd.Series(index=df.index, data='black')
        
        # Previsões do modelo
        predictions = self.predict(df)
        
        # Combinar com sinais técnicos
        signals = pd.Series(index=df.index, data='black')
        
        for i in range(len(df)):
            if i >= len(df) - 1:  # Último dia
                continue
                
            # Condições técnicas
            stoch_condition = (df['STOCH_K'].iloc[i] > 50) and (df['STOCH_K'].iloc[i] > df['STOCH_K'].iloc[i-1])
            rsi_condition = (df['RSI'].iloc[i] > 50) and (df['RSI'].iloc[i] > df['RSI'].iloc[i-1])
            macd_condition = (df['MACD'].iloc[i] > df['MACD_SIGNAL'].iloc[i]) and (df['MACD'].iloc[i] > df['MACD'].iloc[i-1])
            
            # Previsão ML
            ml_signal = predictions.iloc[i] > 0
            
            # Combinar sinais
            conditions_met = sum([stoch_condition, rsi_condition, macd_condition])
            
            if conditions_met >= 2 and ml_signal:
                signals.iloc[i] = 'green'
            elif conditions_met <= 1 and not ml_signal:
                signals.iloc[i] = 'red'
        
        return signals