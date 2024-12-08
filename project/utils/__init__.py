"""
Módulo de utilitários para o dashboard financeiro.
Inclui funções para busca de dados, cálculo de indicadores, visualização e backtesting.
"""

from .data import StockDataManager
from .mt5_data import MT5DataManager
from .indicators import calculate_indicators
from .plotting import create_dashboard_plot
from .backtest import Strategy

__all__ = ['StockDataManager', 'MT5DataManager', 'calculate_indicators', 'create_dashboard_plot', 'Strategy']