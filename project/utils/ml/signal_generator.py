"""
Módulo para geração de sinais de trading.
"""
import pandas as pd

class SignalGenerator:
    def __init__(self, ml_threshold=0.55, score_threshold=2):
        self.ml_threshold = ml_threshold
        self.score_threshold = score_threshold
        
    def check_rsi(self, current, previous):
        """Verifica condição do RSI."""
        return current > 40 and current > previous
        
    def check_macd(self, current, signal, previous):
        """Verifica condição do MACD."""
        return current > signal or current > previous
        
    def check_stochastic(self, k_current, d_current, k_previous):
        """Verifica condição do Stochastic."""
        return k_current > d_current or k_current > k_previous
        
    def calculate_score(self, indicators):
        """Calcula pontuação dos indicadores técnicos."""
        score = 0
        if self.check_rsi(indicators['rsi'], indicators['rsi_prev']):
            score += 1
        if self.check_macd(indicators['macd'], indicators['macd_signal'], indicators['macd_prev']):
            score += 1
        if self.check_stochastic(indicators['stoch_k'], indicators['stoch_d'], indicators['stoch_k_prev']):
            score += 1
        return score
        
    def generate_signal(self, indicators, ml_probability):
        """Gera sinal de trading baseado nos indicadores e ML."""
        score = self.calculate_score(indicators)
        
        if ml_probability > self.ml_threshold and score >= self.score_threshold:
            return 'green'
        elif ml_probability < (1 - self.ml_threshold) and score <= 1:
            return 'red'
        return 'black'