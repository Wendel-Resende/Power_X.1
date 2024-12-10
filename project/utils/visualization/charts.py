"""
Módulo para criação de gráficos de análise.
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

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
    if trades_df is not None and not trades_df.empty:
        returns = trades_df[trades_df['type'] == 'sell']['profit_pct'].dropna()
        if not returns.empty:
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
    if trades_df is not None and not trades_df.empty:
        # Reconstruir curva de capital
        capital_curve = pd.Series(index=df.index, dtype=float)
        capital_curve.iloc[0] = 10000.0  # Capital inicial
        
        for _, trade in trades_df.iterrows():
            if trade['type'] == 'sell':
                idx = df.index.get_loc(trade['date'])
                capital_curve.iloc[idx] = trade['capital']
        
        # Preencher valores intermediários
        capital_curve = capital_curve.fillna(method='ffill')
        capital_curve = capital_curve.fillna(method='bfill')
        
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=capital_curve,
                name='Capital',
                showlegend=False
            ),
            row=1, col=2
        )
        
        # Drawdown
        drawdown = calculate_drawdown_series(capital_curve)
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
        title_x=0.5,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    # Atualizar eixos
    fig.update_xaxes(gridcolor='rgba(128,128,128,0.2)', showgrid=True)
    fig.update_yaxes(gridcolor='rgba(128,128,128,0.2)', showgrid=True)
    
    return fig

def calculate_drawdown_series(equity_curve):
    """
    Calcula série temporal de drawdown.
    
    Args:
        equity_curve: Série temporal com valores de capital
    """
    rolling_max = equity_curve.expanding().max()
    drawdown = (equity_curve - rolling_max) / rolling_max * 100
    return drawdown