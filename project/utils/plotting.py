import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_dashboard_plot(df):
    """Criar o gráfico principal do dashboard com candlesticks e indicadores."""
    fig = make_subplots(rows=4, cols=1, 
                       shared_xaxes=True,
                       vertical_spacing=0.12,  # Aumentado ainda mais o espaçamento vertical
                       row_heights=[0.4, 0.2, 0.2, 0.2],  # Proporções mais equilibradas
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
                            line=dict(color='#00B5F0', width=1.5)), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['STOCH_D'], name='Stoch %D', 
                            line=dict(color='#FFA500', width=1.5)), row=2, col=1)
    fig.add_hline(y=50, line_dash="dash", line_color="gray", row=2, col=1)
    fig.add_hline(y=80, line_dash="dash", line_color="rgba(128, 128, 128, 0.3)", row=2, col=1)
    fig.add_hline(y=20, line_dash="dash", line_color="rgba(128, 128, 128, 0.3)", row=2, col=1)

    # RSI
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', 
                            line=dict(color='#E066FF', width=1.5)), row=3, col=1)
    fig.add_hline(y=50, line_dash="dash", line_color="gray", row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="rgba(128, 128, 128, 0.3)", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="rgba(128, 128, 128, 0.3)", row=3, col=1)

    # MACD
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD', 
                            line=dict(color='#00B5F0', width=1.5)), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD_SIGNAL'], name='Sinal MACD', 
                            line=dict(color='#FFA500', width=1.5)), row=4, col=1)
    
    # Histograma MACD com cores diferentes para valores positivos e negativos
    colors = ['#FF4444' if val < 0 else '#00CC00' for val in (df['MACD'] - df['MACD_SIGNAL'])]
    fig.add_trace(go.Bar(
        x=df.index, 
        y=df['MACD'] - df['MACD_SIGNAL'], 
        name='MACD Histograma',
        marker_color=colors,
        opacity=0.7
    ), row=4, col=1)

    # Atualizar layout
    fig.update_layout(
        height=1200,  # Aumentado ainda mais a altura total
        showlegend=True,
        xaxis4_rangeslider_visible=False,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor='gray',
            borderwidth=1,
            x=1.02,  # Movido a legenda para fora do gráfico
            y=1
        ),
        margin=dict(t=30, l=60, r=100, b=30)  # Ajustado margem direita para a legenda
    )

    # Atualizar eixos Y com melhor formatação
    fig.update_yaxes(title_text="Preço", row=1, col=1, gridcolor='rgba(128,128,128,0.2)')
    fig.update_yaxes(title_text="Stochastic", row=2, col=1, gridcolor='rgba(128,128,128,0.2)', 
                     range=[0, 100], tickmode='linear', tick0=0, dtick=20)
    fig.update_yaxes(title_text="RSI", row=3, col=1, gridcolor='rgba(128,128,128,0.2)', 
                     range=[0, 100], tickmode='linear', tick0=0, dtick=20)
    fig.update_yaxes(title_text="MACD", row=4, col=1, gridcolor='rgba(128,128,128,0.2)')
    
    # Atualizar eixos X
    fig.update_xaxes(gridcolor='rgba(128,128,128,0.2)', showgrid=True)

    # Adicionar títulos mais visíveis para cada subplot
    for i in range(len(fig.layout.annotations)):
        fig.layout.annotations[i].update(
            font=dict(size=14, color='white'),
            y=fig.layout.annotations[i].y + 0.02  # Ajuste fino da posição vertical
        )

    return fig