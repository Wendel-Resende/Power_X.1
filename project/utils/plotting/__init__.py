"""
Módulo de plotagem para o dashboard financeiro.
"""

from plotly.subplots import make_subplots
from .candlestick import add_candlestick_chart
from .indicators import add_stochastic, add_rsi, add_macd
from .layout import update_layout

def create_dashboard_plot(df):
    """Create the main dashboard plot with candlesticks and indicators."""
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.009,  # Aumentado para criar mais espaço entre os subplots
        row_heights=[0.35, 0.20, 0.20, 0.25],  # Ajustado para melhor distribuição
        subplot_titles=('Preço', 'Stochastic', 'RSI', 'MACD')
    )
    
    fig = add_candlestick_chart(fig, df)
    fig = add_stochastic(fig, df)
    fig = add_rsi(fig, df)
    fig = add_macd(fig, df)
    fig = update_layout(fig)
    
    return fig

__all__ = ['create_dashboard_plot']
