"""
Módulo principal do preditor ML.
"""
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from .features import FeatureEngineering
from .evaluation import ModelEvaluation

class MLPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_engineering = FeatureEngineering()
        self.evaluation = ModelEvaluation()
    
    def prepare_data(self, df):
        """Prepara dados para o modelo."""
        # Criar diferentes tipos de features
        tech_features = self.feature_engineering.create_technical_features(df)
        price_features = self.feature_engineering.create_price_features(df)
        lagged_features = self.feature_engineering.create_lagged_features(
            df, ['Close', 'Volume'], lags=3
        )
        
        # Combinar todas as features
        features = pd.concat([tech_features, price_features, lagged_features], axis=1)
        features = features.dropna()
        
        # Preparar target
        target = df['Close'].pct_change().shift(-1)
        target = target[features.index]
        
        return features, target.dropna()
    
    def train(self, df):
        """Treina o modelo preditivo."""
        # Preparar dados
        X, y = self.prepare_data(df)
        
        # Dividir dados
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )
        
        # Escalar features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Treinar modelo
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
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
    
    def predict(self, df):
        """Faz previsões com o modelo treinado."""
        if self.model is None:
            raise ValueError("Modelo não treinado")
        
        X, _ = self.prepare_data(df)
        X_scaled = self.scaler.transform(X)
        
        return pd.Series(
            self.model.predict(X_scaled),
            index=X.index
        )
    
    def get_trading_signals(self, df):
        """Gera sinais de trading combinando ML com análise técnica."""
        if self.model is None:
            return pd.Series(index=df.index, data='black')
        
        predictions = self.predict(df)
        signals = pd.Series(index=df.index, data='black')
        
        for i in range(len(df)):
            if i >= len(df) - 1:
                continue
            
            # Condições técnicas
            tech_conditions = [
                (df['STOCH_K'].iloc[i] > 50) and (df['STOCH_K'].iloc[i] > df['STOCH_K'].iloc[i-1]),
                (df['RSI'].iloc[i] > 50) and (df['RSI'].iloc[i] > df['RSI'].iloc[i-1]),
                (df['MACD'].iloc[i] > df['MACD_SIGNAL'].iloc[i]) and (df['MACD'].iloc[i] > df['MACD'].iloc[i-1])
            ]
            
            conditions_met = sum(tech_conditions)
            ml_signal = predictions.iloc[i] > 0
            
            if conditions_met >= 2 and ml_signal:
                signals.iloc[i] = 'green'
            elif conditions_met <= 1 and not ml_signal:
                signals.iloc[i] = 'red'
        
        return signals