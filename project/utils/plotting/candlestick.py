import plotly.graph_objects as go

def add_candlestick_chart(fig, df, row=1, col=1):
    """Add candlestick chart with entry/exit markers to the figure."""
    # Adicionar gráfico de candlestick por cor
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
                    increasing_line_color=color,
                    decreasing_line_color=color,
                    showlegend=True
                ),
                row=row, col=col
            )
    
    # Identificar pontos de entrada (candle verde após não-verde)
    entries = []
    for i in range(1, len(df)):
        if df['signal_color'].iloc[i] == 'green' and df['signal_color'].iloc[i-1] != 'green':
            entries.append(i)
    
    # Identificar pontos de saída (após entrada quando candle fica preto ou vermelho)
    exits = []
    in_position = False
    for i in range(1, len(df)):
        if i in entries:
            in_position = True
        elif in_position and df['signal_color'].iloc[i] in ['black', 'red']:
            exits.append(i)
            in_position = False
    
    # Adicionar marcadores de entrada
    if entries:
        fig.add_trace(
            go.Scatter(
                x=df.index[entries],
                y=df['Low'].iloc[entries] * 0.995,  # Ligeiramente abaixo do candle
                mode='markers',
                marker=dict(
                    symbol='triangle-up',
                    size=12,
                    color='lime',
                    line=dict(color='darkgreen', width=1)
                ),
                name='Entrada',
                showlegend=True
            ),
            row=row, col=col
        )
    
    # Adicionar marcadores de saída
    if exits:
        fig.add_trace(
            go.Scatter(
                x=df.index[exits],
                y=df['High'].iloc[exits] * 1.005,  # Ligeiramente acima do candle
                mode='markers',
                marker=dict(
                    symbol='triangle-down',
                    size=12,
                    color='red',
                    line=dict(color='darkred', width=1)
                ),
                name='Saída',
                showlegend=True
            ),
            row=row, col=col
        )
    
    return fig