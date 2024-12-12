"""
Módulo de modelos de Machine Learning.
"""
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
import numpy as np

class BaseModel:
    """Classe base para modelos ML."""
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
    
    def preprocess(self, X):
        """Pré-processamento dos dados."""
        return self.scaler.fit_transform(X)

class RandomForestModel(BaseModel):
    """Implementação do Random Forest."""
    def __init__(self):
        super().__init__()
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=10,
            class_weight='balanced',
            random_state=42
        )

class GradientBoostingModel(BaseModel):
    """Implementação do Gradient Boosting."""
    def __init__(self):
        super().__init__()
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )

class NeuralNetworkModel(BaseModel):
    """Implementação da Rede Neural."""
    def __init__(self):
        super().__init__()
        self.model = MLPClassifier(
            hidden_layer_sizes=(100, 50),
            activation='relu',
            solver='adam',
            alpha=0.0001,
            learning_rate='adaptive',
            max_iter=1000,
            random_state=42
        )

class EnsembleModel(BaseModel):
    """Modelo ensemble combinando múltiplos classificadores."""
    def __init__(self):
        super().__init__()
        self.models = [
            RandomForestModel(),
            GradientBoostingModel(),
            NeuralNetworkModel()
        ]
    
    def fit(self, X, y):
        """Treina todos os modelos do ensemble."""
        X_scaled = self.preprocess(X)
        for model in self.models:
            model.model.fit(X_scaled, y)
    
    def predict_proba(self, X):
        """Faz previsões combinando todos os modelos."""
        X_scaled = self.preprocess(X)
        predictions = []
        for model in self.models:
            pred = model.model.predict_proba(X_scaled)[:, 1]
            predictions.append(pred)
        return np.mean(predictions, axis=0)