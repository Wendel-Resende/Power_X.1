import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_dashboard_plot(df):
    """Criar o gráfico principal do dashboard com candlesticks e indicadores."""
    fig = make_subplots(rows=4, cols=1, 
                       shared_xaxes=True,
                       vertical_spacing=0.08,  # Aumentado o espaçamento vertical
                       row_heights=[0.5, 0.2, 0.15, 0.15],  # Ajustado as proporções
                       subplot_titles=('Preço', 'Stochastic', 'RSI', 'MACD'))

    # Gráfico de Candlestick
    colors = {
        'green': {'increasing': 'green', 'decreasing': 'green'},
        'red': {'increasing': 'red', 'decreasing': 'red'},
        'black': {'increasing': 'black', 'decreasing': 'black'}
    }

    for color in ['green', 'red', 'black']:
        mask = df['signal_color'] == color
        if mask.any():
            fig.add_trace(
                go.Candlestick(
                    x=df[mask].index,
                    open=df[mask]['Open'],
                    high=df[mask]['High'],
                    low=df[mask]['Low'],
                    close=df[mask]['Close'],
                    name=f'OHLC ({color})',
                    increasing_line_color=colors[color]['increasing'],
                    decreasing_line_color=colors[color]['decreasing'],
                    showlegend=True
                ),
                row=1, col=1
            )

    # Stochastic
    fig.add_trace(go.Scatter(x=df.index, y=df['STOCH_K'], name='Stoch %K', 
                            line=dict(color='blue', width=1.5)), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['STOCH_D'], name='Stoch %D', 
                            line=dict(color='orange', width=1.5)), row=2, col=1)
    fig.add_hline(y=50, line_dash="dash", line_color="gray", row=2, col=1)
    fig.add_hline(y=80, line_dash="dash", line_color="rgba(128, 128, 128, 0.3)", row=2, col=1)
    fig.add_hline(y=20, line_dash="dash", line_color="rgba(128, 128, 128, 0.3)", row=2, col=1)

    # RSI
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', 
                            line=dict(color='purple', width=1.5)), row=3, col=1)
    fig.add_hline(y=50, line_dash="dash", line_color="gray", row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="rgba(128, 128, 128, 0.3)", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="rgba(128, 128, 128, 0.3)", row=3, col=1)

    # MACD
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD', 
                            line=dict(color='blue', width=1.5)), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD_SIGNAL'], name='Sinal MACD', 
                            line=dict(color='orange', width=1.5)), row=4, col=1)
    
    # Histograma MACD com cores diferentes para valores positivos e negativos
    colors = ['red' if val < 0 else 'green' for val in (df['MACD'] - df['MACD_SIGNAL'])]
    fig.add_trace(go.Bar(
        x=df.index, 
        y=df['MACD'] - df['MACD_SIGNAL'], 
        name='MACD Histograma',
        marker_color=colors,
        opacity=0.5
    ), row=4, col=1)

    # Atualizar layout
    fig.update_layout(
        height=1000,  # Aumentado a altura total
        showlegend=True,
        xaxis4_rangeslider_visible=False,
        template='plotly_dark',  # Mudado para tema escuro
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor='gray',
            borderwidth=1
        ),
        margin=dict(t=30, l=60, r=60, b=30)  # Ajustado as margens
    )

    # Atualizar eixos Y com melhor formatação
    fig.update_yaxes(title_text="Preço", row=1, col=1, gridcolor='rgba(128,128,128,0.2)')
    fig.update_yaxes(title_text="Stochastic", row=2, col=1, gridcolor='rgba(128,128,128,0.2)', range=[0, 100])
    fig.update_yaxes(title_text="RSI", row=3, col=1, gridcolor='rgba(128,128,128,0.2)', range=[0, 100])
    fig.update_yaxes(title_text="MACD", row=4, col=1, gridcolor='rgba(128,128,128,0.2)')
    
    # Atualizar eixos X
    fig.update_xaxes(gridcolor='rgba(128,128,128,0.2)', showgrid=True)

    return fig