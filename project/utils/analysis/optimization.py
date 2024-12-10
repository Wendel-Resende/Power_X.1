"""
Módulo para otimização de parâmetros da estratégia.
"""
import pandas as pd
import itertools
from ..indicators import calculate_indicators

def optimize_parameters(df, param_ranges):
    """
    Otimiza parâmetros dos indicadores.
    
    Args:
        df: DataFrame com dados históricos
        param_ranges: Dicionário com ranges de parâmetros para teste
    """
    results = []
    
    # Gerar todas as combinações de parâmetros
    param_combinations = list(itertools.product(
        param_ranges['stoch_k'],
        param_ranges['stoch_d'],
        param_ranges['rsi_length'],
        param_ranges['macd_fast'],
        param_ranges['macd_slow'],
        param_ranges['macd_signal']
    ))
    
    for params in param_combinations:
        stoch_k, stoch_d, rsi_length, macd_fast, macd_slow, macd_signal = params
        
        # Calcular indicadores com parâmetros atuais
        df_test = calculate_indicators(
            df.copy(),
            stoch_k=stoch_k,
            stoch_d=stoch_d,
            rsi_length=rsi_length,
            macd_fast=macd_fast,
            macd_slow=macd_slow,
            macd_signal=macd_signal
        )
        
        # Avaliar resultado
        metrics = evaluate_parameters(df_test)
        
        results.append({
            'stoch_k': stoch_k,
            'stoch_d': stoch_d,
            'rsi_length': rsi_length,
            'macd_fast': macd_fast,
            'macd_slow': macd_slow,
            'macd_signal': macd_signal,
            **metrics
        })
    
    return pd.DataFrame(results)

def evaluate_parameters(df):
    """
    Avalia o desempenho de um conjunto de parâmetros.
    
    Args:
        df: DataFrame com indicadores calculados
    """
    # Contar sinais
    total_signals = len(df)
    green_signals = (df['signal_color'] == 'green').sum()
    red_signals = (df['signal_color'] == 'red').sum()
    
    # Calcular consistência dos sinais
    signal_consistency = (green_signals + red_signals) / total_signals
    
    # Calcular tendência dos sinais
    price_changes = df['Close'].pct_change()
    correct_green = ((df['signal_color'] == 'green') & (price_changes > 0)).sum()
    correct_red = ((df['signal_color'] == 'red') & (price_changes < 0)).sum()
    
    accuracy = (correct_green + correct_red) / (green_signals + red_signals) if (green_signals + red_signals) > 0 else 0
    
    return {
        'signal_consistency': signal_consistency,
        'accuracy': accuracy,
        'green_signals': green_signals,
        'red_signals': red_signals
    }