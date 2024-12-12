"""
Módulo do modelo XGBoost para previsão de mercado.
"""
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd

class XGBoostModel:
    def __init__(self):
        """Inicializa o modelo XGBoost com hiperparâmetros otimizados."""
        self.model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.01,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=1,
            gamma=0,
            objective='binary:logistic',
            eval_metric='auc',
            random_state=42,
            use_label_encoder=False
        )
        self.scaler = StandardScaler()
        
    def fit(self, X_train, y_train, X_val=None, y_val=None):
        """
        Treina o modelo com early stopping se dados de validação forem fornecidos.
        """
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        if X_val is not None and y_val is not None:
            X_val_scaled = self.scaler.transform(X_val)
            eval_set = [(X_train_scaled, y_train), (X_val_scaled, y_val)]
            self.model.fit(
                X_train_scaled, 
                y_train,
                eval_set=eval_set,
                early_stopping_rounds=20,
                verbose=False
            )
        else:
            self.model.fit(X_train_scaled, y_train)
            
        return self
        
    def predict_proba(self, X):
        """Retorna probabilidades de previsão."""
        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)[:, 1]
    
    def get_feature_importance(self, feature_names):
        """Retorna importância das features."""
        importance = self.model.feature_importances_
        return pd.DataFrame({
            'feature': feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)