"""
Módulo para avaliação de modelos.
"""
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score

class ModelEvaluation:
    def evaluate_model(self, model, X_train, y_train, X_test, y_test, feature_names=None):
        """Avalia o modelo com múltiplas métricas."""
        # Métricas básicas
        train_score = model.score(X_train, y_train)
        test_score = model.score(X_test, y_test)
        
        # Previsões
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)
        
        # Métricas detalhadas
        metrics = {
            'train_score': train_score,
            'test_score': test_score,
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_train_pred)),
            'test_rmse': np.sqrt(mean_squared_error(y_test, y_test_pred)),
            'train_r2': r2_score(y_train, y_train_pred),
            'test_r2': r2_score(y_test, y_test_pred)
        }
        
        # Importância das features
        if feature_names is not None:
            metrics['feature_importance'] = pd.DataFrame({
                'feature': feature_names,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
        
        return metrics