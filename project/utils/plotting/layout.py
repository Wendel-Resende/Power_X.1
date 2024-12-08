def update_layout(fig):
    """Update the figure layout and styling."""
    # Configuração básica do layout
    fig.update_layout(
        height=1200,  # Altura aumentada para melhor espaçamento
        showlegend=True,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor='gray',
            borderwidth=1,
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,  # Movida para a direita do gráfico principal
            font=dict(size=10)
        ),
        margin=dict(t=30, l=60, r=60, b=30)
    )
    
    # Configurar eixos Y com domínios ajustados para melhor espaçamento
    fig.update_yaxes(
        title_text="Preço", 
        row=1, col=1, 
        gridcolor='rgba(128,128,128,0.2)',
        title_standoff=20,
        domain=[0.70, 1.0]  # Mais espaço para o gráfico principal
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
        domain=[0.48, 0.65]  # Maior separação
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
        domain=[0.26, 0.43]  # Maior separação
    )
    
    fig.update_yaxes(
        title_text="MACD", 
        row=4, col=1, 
        gridcolor='rgba(128,128,128,0.2)',
        title_standoff=20,
        domain=[0.04, 0.21]  # Maior separação
    )
    
    # Configurar eixos X
    fig.update_xaxes(
        gridcolor='rgba(128,128,128,0.2)', 
        showgrid=True,
        rangeslider=dict(visible=False)
    )
    
    # Ajustar posição dos títulos dos subplots
    for i in range(len(fig.layout.annotations)):
        fig.layout.annotations[i].update(
            font=dict(size=14, color='white'),
            y=fig.layout.annotations[i].y + 0.03
        )
    
    return fig