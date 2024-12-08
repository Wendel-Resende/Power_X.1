import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_dashboard_plot(df):
    """Create the main dashboard plot with candlesticks and indicators."""
    fig = make_subplots(rows=4, cols=1, 
                       shared_xaxes=True,
                       vertical_spacing=0.08,
                       row_heights=[0.4, 0.2, 0.2, 0.2],
                       subplot_titles=('Preço', 'Stochastic', 'RSI', 'MACD'))

    # Candlestick chart
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
    
    # MACD Histogram
    macd_diff = df['MACD'] - df['MACD_SIGNAL']
    colors = ['#FF4444' if val < 0 else '#00CC00' for val in macd_diff]
    fig.add_trace(go.Bar(
        x=df.index, 
        y=macd_diff,
        name='MACD Histograma',
        marker_color=colors,
        opacity=0.7
    ), row=4, col=1)

    # Update layout
    fig.update_layout(
        height=900,
        showlegend=True,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor='gray',
            borderwidth=1
        ),
        margin=dict(t=30, l=60, r=60, b=30)
    )

    # Update Y axes
    fig.update_yaxes(title_text="Preço", row=1, col=1, gridcolor='rgba(128,128,128,0.2)',
                     title_standoff=20)
    fig.update_yaxes(title_text="Stochastic", row=2, col=1, gridcolor='rgba(128,128,128,0.2)', 
                     range=[0, 100], tickmode='linear', tick0=0, dtick=20,
                     title_standoff=20)
    fig.update_yaxes(title_text="RSI", row=3, col=1, gridcolor='rgba(128,128,128,0.2)', 
                     range=[0, 100], tickmode='linear', tick0=0, dtick=20,
                     title_standoff=20)
    fig.update_yaxes(title_text="MACD", row=4, col=1, gridcolor='rgba(128,128,128,0.2)',
                     title_standoff=20)
    
    # Update X axes
    fig.update_xaxes(gridcolor='rgba(128,128,128,0.2)', showgrid=True)

    # Adjust subplot titles position and style
    for i in range(len(fig.layout.annotations)):
        fig.layout.annotations[i].update(
            font=dict(size=14, color='white'),
            y=fig.layout.annotations[i].y + 0.03
        )

    return fig