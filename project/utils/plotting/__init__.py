"""
Módulo de plotagem para o dashboard financeiro.
"""

from plotly.subplots import make_subplots
from .candlestick import add_candlestick_chart
from .indicators import add_stochastic, add_rsi, add_macd
from .layout import update_layout

def create_dashboard_plot(df):
    """Create the main dashboard plot with candlesticks and indicators."""
    # Aumentar o espaçamento vertical e ajustar as alturas dos subplots
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.12,  # Aumentado de 0.08 para 0.12
        row_heights=[0.5, 0.15, 0.15, 0.2],  # Ajustado para dar mais espaço ao gráfico principal
        subplot_titles=('Preço', 'Stochastic', 'RSI', 'MACD')
    )
    
    fig = add_candlestick_chart(fig, df)
    fig = add_stochastic(fig, df)
    fig = add_rsi(fig, df)
    fig = add_macd(fig, df)
    fig = update_layout(fig)
    
    return fig

__all__ = ['create_dashboard_plot']