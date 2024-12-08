import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_dashboard_plot(df):
    """Criar o gráfico principal do dashboard com candlesticks e indicadores."""
    fig = make_subplots(rows=4, cols=1, 
                       shared_xaxes=True,
                       vertical_spacing=0.05,
                       row_heights=[0.4, 0.2, 0.2, 0.2],
                       subplot_titles=('Preço', 'Stochastic', 'RSI', 'MACD'))

    # Gráfico de Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC',
            increasing_line_color=df['signal_color'].map({'green': 'green', 'red': 'red', 'black': 'black'}),
            decreasing_line_color=df['signal_color'].map({'green': 'green', 'red': 'red', 'black': 'black'})
        ),
        row=1, col=1
    )

    # Stochastic
    fig.add_trace(go.Scatter(x=df.index, y=df['STOCH_K'], name='Stoch %K', line=dict(color='blue')), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['STOCH_D'], name='Stoch %D', line=dict(color='orange')), row=2, col=1)
    fig.add_hline(y=50, line_dash="dash", line_color="gray", row=2, col=1)

    # RSI
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')), row=3, col=1)
    fig.add_hline(y=50, line_dash="dash", line_color="gray", row=3, col=1)

    # MACD
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD', line=dict(color='blue')), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD_SIGNAL'], name='Sinal MACD', line=dict(color='orange')), row=4, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df['MACD'] - df['MACD_SIGNAL'], name='MACD Histograma'), row=4, col=1)

    # Atualizar layout
    fig.update_layout(
        height=900,
        showlegend=True,
        xaxis4_rangeslider_visible=False,
        template='plotly_white'
    )

    # Atualizar eixos Y
    fig.update_yaxes(title_text="Preço", row=1, col=1)
    fig.update_yaxes(title_text="Stochastic", row=2, col=1)
    fig.update_yaxes(title_text="RSI", row=3, col=1)
    fig.update_yaxes(title_text="MACD", row=4, col=1)

    return fig