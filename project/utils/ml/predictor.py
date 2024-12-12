"""
Módulo principal do preditor ML.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
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
    
    def train(self, df):
        """Treina o modelo preditivo."""
        try:
            # Preparar dados
            X, y = self.prepare_data(df)
            
            if len(X) < 50:
                raise ValueError("Dados insuficientes para treinar o modelo")
            
            # Usar validação cruzada temporal
            tscv = TimeSeriesSplit(n_splits=5, test_size=int(len(X) * 0.2))
            
            best_model = None
            best_score = float('-inf')
            
            for train_idx, test_idx in tscv.split(X):
                X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
                y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
                
                # Escalar features
                X_train_scaled = self.scaler.fit_transform(X_train)
                X_test_scaled = self.scaler.transform(X_test)
                
                # Treinar modelo com parâmetros otimizados
                model = RandomForestRegressor(
                    n_estimators=200,
                    max_depth=8,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    random_state=42
                )
                model.fit(X_train_scaled, y_train)
                
                # Avaliar modelo
                score = model.score(X_test_scaled, y_test)
                if score > best_score:
                    best_score = score
                    best_model = model
            
            self.model = best_model
            
            # Avaliar modelo final
            metrics = self.evaluation.evaluate_model(
                self.model,
                X_train_scaled, y_train,
                X_test_scaled, y_test,
                feature_names=X.columns
            )
            
            return metrics
            
        except Exception as e:
            raise Exception(f"Erro no treinamento: {str(e)}")