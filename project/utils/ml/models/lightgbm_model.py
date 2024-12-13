"""
Módulo do modelo LightGBM para previsão de mercado.
"""
import lightgbm as lgb
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd

class LightGBMModel:
    def __init__(self):
        """Inicializa o modelo LightGBM com hiperparâmetros otimizados."""
        self.params = {
            'objective': 'binary',
            'metric': 'auc',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.01,
            'feature_fraction': 0.8,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1,
            'random_state': 42
        }
        self.model = None
        self.scaler = StandardScaler()
        
    def fit(self, X_train, y_train, X_val=None, y_val=None):
        """
        Treina o modelo com early stopping se dados de validação forem fornecidos.
        """
        X_train_scaled = self.scaler.fit_transform(X_train)
        train_data = lgb.Dataset(X_train_scaled, label=y_train)
        
        if X_val is not None and y_val is not None:
            X_val_scaled = self.scaler.transform(X_val)
            val_data = lgb.Dataset(X_val_scaled, label=y_val)
            
            self.model = lgb.train(
                self.params,
                train_data,
                num_boost_round=1000,
                valid_sets=[train_data, val_data],
                valid_names=['train', 'valid'],
                early_stopping_rounds=50,
                verbose_eval=False
            )
        else:
            self.model = lgb.train(
                self.params,
                train_data,
                num_boost_round=1000
            )
            
        return self
        
    def predict_proba(self, X):
        """Retorna probabilidades de previsão."""
        if self.model is None:
            raise ValueError("Modelo não treinado")
            
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def get_feature_importance(self, feature_names):
        """Retorna importância das features."""
        if self.model is None:
            raise ValueError("Modelo não treinado")
            
        importance = self.model.feature_importance(importance_type='gain')
        return pd.DataFrame({
            'feature': feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)