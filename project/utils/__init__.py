"""
Módulo de utilidades para o dashboard financeiro.
"""

from .data import StockDataManager
from .indicators import calculate_indicators
from .plotting import create_dashboard_plot
from .backtest import Strategy

__all__ = ['StockDataManager', 'calculate_indicators', 'create_dashboard_plot', 'Strategy']