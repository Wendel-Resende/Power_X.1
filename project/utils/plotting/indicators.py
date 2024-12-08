import plotly.graph_objects as go

def add_stochastic(fig, df, row=2, col=1):
    """Add Stochastic indicator to the figure."""
    fig.add_trace(go.Scatter(x=df.index, y=df['STOCH_K'], name='Stoch %K', 
                            line=dict(color='#00B5F0', width=1.5)), row=row, col=col)
    fig.add_trace(go.Scatter(x=df.index, y=df['STOCH_D'], name='Stoch %D', 
                            line=dict(color='#FFA500', width=1.5)), row=row, col=col)
    fig.add_hline(y=50, line_dash="dash", line_color="gray", row=row, col=col)
    fig.add_hline(y=80, line_dash="dash", line_color="rgba(128, 128, 128, 0.3)", row=row, col=col)
    fig.add_hline(y=20, line_dash="dash", line_color="rgba(128, 128, 128, 0.3)", row=row, col=col)
    return fig

def add_rsi(fig, df, row=3, col=1):
    """Add RSI indicator to the figure."""
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', 
                            line=dict(color='#E066FF', width=1.5)), row=row, col=col)
    fig.add_hline(y=50, line_dash="dash", line_color="gray", row=row, col=col)
    fig.add_hline(y=70, line_dash="dash", line_color="rgba(128, 128, 128, 0.3)", row=row, col=col)
    fig.add_hline(y=30, line_dash="dash", line_color="rgba(128, 128, 128, 0.3)", row=row, col=col)
    return fig

def add_macd(fig, df, row=4, col=1):
    """Add MACD indicator to the figure."""
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD', 
                            line=dict(color='#00B5F0', width=1.5)), row=row, col=col)
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD_SIGNAL'], name='Sinal MACD', 
                            line=dict(color='#FFA500', width=1.5)), row=row, col=col)
    
    macd_diff = df['MACD'] - df['MACD_SIGNAL']
    colors = ['#FF4444' if val < 0 else '#00CC00' for val in macd_diff]
    fig.add_trace(go.Bar(
        x=df.index, 
        y=macd_diff,
        name='MACD Histograma',
        marker_color=colors,
        opacity=0.7
    ), row=row, col=col)
    return fig