import plotly.graph_objects as go

def add_candlestick_chart(fig, df, row=1, col=1):
    """Add candlestick chart to the figure."""
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
    return fig