"""
Módulo de estratégia de trading usando Machine Learning.
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam

class MLStrategy:
    def __init__(self, lookback=60):
        self.lookback = lookback
        self.model = None
        self.scaler = MinMaxScaler()
        
    def prepare_data(self, df):
        """Prepara dados para o modelo."""
        # Features técnicas
        features = pd.DataFrame(index=df.index)
        
        # Preços e volumes normalizados
        price_cols = ['Open', 'High', 'Low', 'Close']
        features[price_cols] = self.scaler.fit_transform(df[price_cols])
        features['Volume'] = self.scaler.fit_transform(df[['Volume']])
        
        # Retornos
        features['Returns'] = df['Close'].pct_change()
        
        # Volatilidade
        features['Volatility'] = df['Close'].rolling(window=20).std()
        
        # Momentum
        features['RSI'] = df['RSI'] / 100  # Normalizar RSI
        features['STOCH_K'] = df['STOCH_K'] / 100  # Normalizar Stochastic
        features['MACD'] = (df['MACD'] - df['MACD'].min()) / (df['MACD'].max() - df['MACD'].min())
        
        # Tendência
        features['EMA9_Dist'] = (df['Close'] - df['EMA_9']) / df['Close']
        features['EMA21_Dist'] = (df['Close'] - df['EMA_21']) / df['Close']
        
        # Preencher valores NaN
        features = features.fillna(0)
        
        return features
    
    def create_sequences(self, features):
        """Cria sequências para LSTM."""
        X, y = [], []
        
        for i in range(self.lookback, len(features)):
            X.append(features.iloc[i-self.lookback:i].values)
            # Target: 1 se o preço subiu, 0 se caiu
            y.append(1 if features['Returns'].iloc[i] > 0 else 0)
            
        return np.array(X), np.array(y)
    
    def build_model(self, input_shape):
        """Constrói modelo LSTM."""
        model = Sequential([
            LSTM(100, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def train(self, df, validation_split=0.2):
        """Treina o modelo."""
        # Preparar dados
        features = self.prepare_data(df)
        X, y = self.create_sequences(features)
        
        # Construir e treinar modelo
        self.model = self.build_model((self.lookback, features.shape[1]))
        
        history = self.model.fit(
            X, y,
            validation_split=validation_split,
            epochs=50,
            batch_size=32,
            verbose=0
        )
        
        return history
    
    def predict(self, df):
        """Faz previsões com o modelo treinado."""
        if self.model is None:
            raise ValueError("Modelo não treinado")
            
        features = self.prepare_data(df)
        X, _ = self.create_sequences(features)
        
        predictions = self.model.predict(X)
        
        # Converter previsões para sinais
        signals = pd.Series(index=df.index, data=np.nan)
        signals.iloc[self.lookback:] = (predictions.flatten() > 0.5).astype(int)
        
        return signals
    
    def generate_trading_signals(self, df):
        """Gera sinais de trading combinando ML com análise técnica."""
        # Previsões do modelo
        ml_signals = self.predict(df)
        
        # Sinais técnicos
        tech_signals = pd.Series(index=df.index, data='black')
        
        for i in range(len(df)):
            # Condições técnicas
            rsi_ok = df['RSI'].iloc[i] > 50
            stoch_ok = df['STOCH_K'].iloc[i] > 50
            macd_ok = df['MACD'].iloc[i] > df['MACD_SIGNAL'].iloc[i]
            
            # Combinar sinais
            if i >= self.lookback:
                ml_signal = ml_signals.iloc[i]
                
                if ml_signal == 1 and (rsi_ok and stoch_ok and macd_ok):
                    tech_signals.iloc[i] = 'green'
                elif ml_signal == 0 and (not rsi_ok and not stoch_ok and not macd_ok):
                    tech_signals.iloc[i] = 'red'
        
        return tech_signals