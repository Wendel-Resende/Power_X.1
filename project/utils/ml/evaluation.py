"""
Módulo para avaliação de modelos.
"""
import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score, mean_squared_error
)

class ModelEvaluation:
    def evaluate_model(self, model, X_train, y_train, X_test, y_test, feature_names=None):
        """Avalia o modelo com métricas avançadas."""
        # Previsões
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)
        
        # Probabilidades
        y_train_proba = model.predict_proba(X_train)[:, 1]
        y_test_proba = model.predict_proba(X_test)[:, 1]
        
        # Métricas básicas
        metrics = {
            'train_accuracy': accuracy_score(y_train, y_train_pred),
            'test_accuracy': accuracy_score(y_test, y_test_pred),
            'train_precision': precision_score(y_train, y_train_pred),
            'test_precision': precision_score(y_test, y_test_pred),
            'train_recall': recall_score(y_train, y_train_pred),
            'test_recall': recall_score(y_test, y_test_pred),
            'train_f1': f1_score(y_train, y_train_pred),
            'test_f1': f1_score(y_test, y_test_pred),
            'train_auc': roc_auc_score(y_train, y_train_proba),
            'test_auc': roc_auc_score(y_test, y_test_proba),
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_train_pred)),
            'test_rmse': np.sqrt(mean_squared_error(y_test, y_test_pred))
        }
        
        # Matriz de confusão
        conf_matrix = confusion_matrix(y_test, y_test_pred)
        metrics['confusion_matrix'] = conf_matrix
        
        # Importância das features
        if hasattr(model, 'feature_importances_') and feature_names is not None:
            feature_importance = pd.DataFrame({
                'feature': feature_names,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            metrics['feature_importance'] = feature_importance
        
        return metrics
    
    def calculate_trading_metrics(self, predictions, returns):
        """Calcula métricas específicas de trading."""
        # Retorno da estratégia
        strategy_returns = predictions * returns
        
        metrics = {
            'total_return': np.sum(strategy_returns),
            'annualized_return': np.mean(strategy_returns) * 252,
            'volatility': np.std(strategy_returns) * np.sqrt(252),
            'sharpe_ratio': np.mean(strategy_returns) / np.std(strategy_returns) * np.sqrt(252),
            'max_drawdown': self._calculate_max_drawdown(strategy_returns),
            'win_rate': np.mean(strategy_returns > 0)
        }
        
        return metrics
    
    def _calculate_max_drawdown(self, returns):
        """Calcula o máximo drawdown."""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()