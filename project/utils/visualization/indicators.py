"""
Módulo para criação de gráficos de indicadores.
"""
import plotly.graph_objects as go

def create_indicator_charts(df):
    """
    Cria gráficos detalhados dos indicadores.
    
    Args:
        df: DataFrame com dados e indicadores
    """
    # Criar figura com subplots para cada indicador
    fig = go.Figure()
    
    # Adicionar Stochastic
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['STOCH_K'],
        name='Stochastic %K',
        line=dict(color='#00B5F0', width=1.5)
    ))
    
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['STOCH_D'],
        name='Stochastic %D',
        line=dict(color='#FFA500', width=1.5)
    ))
    
    # Adicionar RSI
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['RSI'],
        name='RSI',
        line=dict(color='#E066FF', width=1.5),
        visible='legendonly'
    ))
    
    # Adicionar MACD
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['MACD'],
        name='MACD',
        line=dict(color='#00B5F0', width=1.5),
        visible='legendonly'
    ))
    
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['MACD_SIGNAL'],
        name='Sinal MACD',
        line=dict(color='#FFA500', width=1.5),
        visible='legendonly'
    ))
    
    # Atualizar layout
    fig.update_layout(
        height=600,
        template='plotly_dark',
        title_text="Análise de Indicadores",
        title_x=0.5,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig