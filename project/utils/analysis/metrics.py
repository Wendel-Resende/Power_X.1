"""
Módulo para cálculo de métricas avançadas de risco e correlação.
"""
import numpy as np
import pandas as pd

def calculate_risk_metrics(positions_df):
    """
    Calcula métricas avançadas de risco.
    
    Args:
        positions_df: DataFrame com posições e capital
    """
    returns = positions_df['capital'].pct_change()
    
    # Sharpe Ratio (considerando taxa livre de risco = 0 para simplicidade)
    sharpe = (returns.mean() * 252) / (returns.std() * np.sqrt(252))
    
    # Sortino Ratio
    negative_returns = returns[returns < 0]
    sortino = (returns.mean() * 252) / (negative_returns.std() * np.sqrt(252))
    
    # Caldermar Ratio
    max_dd = calculate_max_drawdown(positions_df['capital'])
    calmar = (returns.mean() * 252) / abs(max_dd)
    
    return {
        'sharpe_ratio': sharpe,
        'sortino_ratio': sortino,
        'calmar_ratio': calmar
    }

def calculate_correlation_metrics(df, market_returns):
    """
    Calcula métricas de correlação com o mercado.
    
    Args:
        df: DataFrame com dados do ativo
        market_returns: Série com retornos do mercado
    """
    asset_returns = df['Close'].pct_change()
    
    # Correlação
    correlation = asset_returns.corr(market_returns)
    
    # Beta
    covariance = asset_returns.cov(market_returns)
    market_variance = market_returns.var()
    beta = covariance / market_variance
    
    # R-squared
    r_squared = correlation ** 2
    
    return {
        'correlation': correlation,
        'beta': beta,
        'r_squared': r_squared
    }

def calculate_max_drawdown(series):
    """Calcula o máximo drawdown de uma série."""
    rolling_max = series.expanding().max()
    drawdowns = (series - rolling_max) / rolling_max
    return drawdowns.min()