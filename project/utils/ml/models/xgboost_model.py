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
        self.params = {
            'objective': 'binary:logistic',
            'eval_metric': 'auc',
            'max_depth': 5,
            'learning_rate': 0.01,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'min_child_weight': 1,
            'gamma': 0,
            'random_state': 42,
            'use_label_encoder': False
        }
        self.model = None
        self.scaler = StandardScaler()
        
    def fit(self, X_train, y_train, X_val=None, y_val=None):
        """
        Treina o modelo com early stopping se dados de validação forem fornecidos.
        """
        X_train_scaled = self.scaler.fit_transform(X_train)
        dtrain = xgb.DMatrix(X_train_scaled, label=y_train)
        
        if X_val is not None and y_val is not None:
            X_val_scaled = self.scaler.transform(X_val)
            dval = xgb.DMatrix(X_val_scaled, label=y_val)
            
            watchlist = [(dtrain, 'train'), (dval, 'eval')]
            self.model = xgb.train(
                self.params,
                dtrain,
                num_boost_round=1000,
                evals=watchlist,
                early_stopping_rounds=50,
                verbose_eval=False
            )
        else:
            self.model = xgb.train(
                self.params,
                dtrain,
                num_boost_round=1000
            )
            
        return self
        
    def predict_proba(self, X):
        """Retorna probabilidades de previsão."""
        if self.model is None:
            raise ValueError("Modelo não treinado")
            
        X_scaled = self.scaler.transform(X)
        dtest = xgb.DMatrix(X_scaled)
        return self.model.predict(dtest)
    
    def get_feature_importance(self, feature_names):
        """Retorna importância das features."""
        if self.model is None:
            raise ValueError("Modelo não treinado")
            
        importance = self.model.get_score(importance_type='gain')
        importance_df = pd.DataFrame(
            [(k, v) for k, v in importance.items()],
            columns=['feature', 'importance']
        )
        return importance_df.sort_values('importance', ascending=False)