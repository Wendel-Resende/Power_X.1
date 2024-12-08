"""
Módulo de plotagem para o dashboard financeiro.
"""

from plotly.subplots import make_subplots
from .candlestick import add_candlestick_chart
from .indicators import add_stochastic, add_rsi, add_macd
from .layout import update_layout

def create_dashboard_plot(df):
    """Create the main dashboard plot with candlesticks and indicators."""
    # Criar subplots com maior espaçamento vertical e melhor distribuição de altura
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.15,  # Aumentado para maior separação entre gráficos
        row_heights=[0.55, 0.15, 0.15, 0.15],  # Gráfico principal maior, indicadores menores
        subplot_titles=('Preço', 'Stochastic', 'RSI', 'MACD')
    )
    
    # Adicionar componentes do gráfico
    fig = add_candlestick_chart(fig, df)
    fig = add_stochastic(fig, df)
    fig = add_rsi(fig, df)
    fig = add_macd(fig, df)
    
    # Atualizar layout com configurações melhoradas
    fig = update_layout(fig)
    
    return fig

__all__ = ['create_dashboard_plot']