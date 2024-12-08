"""
Este módulo contém utilitários para o dashboard financeiro.
Inclui funções para busca de dados, cálculo de indicadores e visualização.
"""

from .data import fetch_stock_data
from .indicators import calculate_indicators
from .plotting import create_dashboard_plot

__all__ = ['fetch_stock_data', 'calculate_indicators', 'create_dashboard_plot']