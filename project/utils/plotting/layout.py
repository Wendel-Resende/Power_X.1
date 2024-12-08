def update_layout(fig):
    """Update the figure layout and styling."""
    fig.update_layout(
        height=1400,
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
    
    # Update Y axes com mais espaço entre os gráficos
    fig.update_yaxes(
        title_text="Preço", 
        row=1, col=1, 
        gridcolor='rgba(128,128,128,0.2)',
        title_standoff=20,
        domain=[0.65, 1]  # Reduzido para criar mais espaço entre os gráficos
    )
    
    fig.update_yaxes(
        title_text="Stochastic", 
        row=2, col=1, 
        gridcolor='rgba(128,128,128,0.2)', 
        range=[0, 100], 
        tickmode='linear', 
        tick0=0, 
        dtick=20,
        title_standoff=20,
        domain=[0.45, 0.60]  # Ajustado para criar mais espaço acima
    )
    
    fig.update_yaxes(
        title_text="RSI", 
        row=3, col=1, 
        gridcolor='rgba(128,128,128,0.2)', 
        range=[0, 100], 
        tickmode='linear', 
        tick0=0, 
        dtick=20,
        title_standoff=20,
        domain=[0.25, 0.40]  # Ajustado para manter o espaçamento consistente
    )
    
    fig.update_yaxes(
        title_text="MACD", 
        row=4, col=1, 
        gridcolor='rgba(128,128,128,0.2)',
        title_standoff=20,
        domain=[0.05, 0.20]  # Ajustado para manter o espaçamento consistente
    )
    
    # Update X axes
    fig.update_xaxes(gridcolor='rgba(128,128,128,0.2)', showgrid=True)
    
    # Adjust subplot titles
    for i in range(len(fig.layout.annotations)):
        fig.layout.annotations[i].update(
            font=dict(size=14, color='white'),
            y=fig.layout.annotations[i].y + 0.03
        )
    
    return fig