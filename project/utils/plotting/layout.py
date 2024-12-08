def update_layout(fig):
    """Update the figure layout and styling."""
    fig.update_layout(
        height=1200,  # Ajustado para melhor proporção
        showlegend=True,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor='gray',
            borderwidth=1,
            y=1.0,  # Movido para o topo
            x=1.0,
            xanchor='right'
        ),
        margin=dict(t=50, l=60, r=60, b=30)  # Aumentado margem superior
    )
    
    # Update Y axes com mais espaço entre os gráficos
    fig.update_yaxes(
        title_text="Preço", 
        row=1, col=1, 
        gridcolor='rgba(128,128,128,0.2)',
        title_standoff=20,
        domain=[0.70, 1.0]  # Aumentado espaço para o gráfico principal
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
        domain=[0.48, 0.65]  # Ajustado para maior separação do gráfico principal
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
        domain=[0.26, 0.43]  # Ajustado para manter espaçamento consistente
    )
    
    fig.update_yaxes(
        title_text="MACD", 
        row=4, col=1, 
        gridcolor='rgba(128,128,128,0.2)',
        title_standoff=20,
        domain=[0.04, 0.21]  # Ajustado para manter espaçamento consistente
    )
    
    # Update X axes
    fig.update_xaxes(
        gridcolor='rgba(128,128,128,0.2)', 
        showgrid=True,
        rangeslider=dict(visible=False)  # Removido o rangeslider para mais espaço
    )
    
    # Adjust subplot titles
    for i in range(len(fig.layout.annotations)):
        fig.layout.annotations[i].update(
            font=dict(size=14, color='white'),
            y=fig.layout.annotations[i].y + 0.05  # Aumentado o deslocamento do título
        )
    
    return fig