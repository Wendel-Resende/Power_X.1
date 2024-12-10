"""
Módulo para criação de gráficos de análise.
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_analysis_charts(df, trades_df=None):
    """
    Cria gráficos avançados de análise.
    
    Args:
        df: DataFrame com dados e indicadores
        trades_df: DataFrame com histórico de trades (opcional)
    """
    # Criar figura com subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Distribuição de Retornos',
            'Curva de Capital',
            'Drawdown',
            'Volume Profile'
        ),
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    # Distribuição de Retornos
    if trades_df is not None:
        returns = trades_df[trades_df['type'] == 'sell']['profit_pct']
        fig.add_trace(
            go.Histogram(
                x=returns,
                nbinsx=30,
                name='Retornos',
                showlegend=False
            ),
            row=1, col=1
        )
    
    # Curva de Capital
    if trades_df is not None:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['equity_curve'],
                name='Capital',
                showlegend=False
            ),
            row=1, col=2
        )
    
    # Drawdown
    if trades_df is not None:
        drawdown = calculate_drawdown_series(df['equity_curve'])
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=drawdown,
                fill='tozeroy',
                name='Drawdown',
                showlegend=False
            ),
            row=2, col=1
        )
    
    # Volume Profile
    fig.add_trace(
        go.Histogram(
            y=df['Close'],
            nbinsy=50,
            name='Volume Profile',
            showlegend=False,
            orientation='h'
        ),
        row=2, col=2
    )
    
    # Atualizar layout
    fig.update_layout(
        height=800,
        showlegend=False,
        template='plotly_dark',
        title_text="Análise Detalhada",
        title_x=0.5
    )
    
    return fig

def calculate_drawdown_series(equity_curve):
    """Calcula série temporal de drawdown."""
    rolling_max = equity_curve.expanding().max()
    drawdown = (equity_curve - rolling_max) / rolling_max * 100
    return drawdown