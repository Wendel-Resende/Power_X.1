def update_layout(fig):
    """Update the figure layout and styling."""
    # Configuração básica do layout
    fig.update_layout(
        height=1000,  # Altura total aumentada
        showlegend=True,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor='gray',
            borderwidth=1,
            orientation="h",  # Orientação horizontal
            yanchor="bottom",
            y=1.02,  # Posiciona acima do gráfico
            xanchor="center",
            x=0.5,  # Centralizado
            font=dict(size=10)
        ),
        margin=dict(t=50, l=60, r=60, b=30)  # Aumentado margin top para acomodar a legenda
    )
    
    # Configurar eixos Y com domínios ajustados para melhor espaçamento
    fig.update_yaxes(
        title_text="Preço", 
        row=1, col=1, 
        gridcolor='rgba(128,128,128,0.2)',
        title_standoff=20,
        domain=[0.75, 1.0]  # Gráfico principal ocupa mais espaço
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
        domain=[0.52, 0.70]  # Maior separação do gráfico principal
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
        domain=[0.29, 0.47]  # Espaçamento consistente
    )
    
    fig.update_yaxes(
        title_text="MACD", 
        row=4, col=1, 
        gridcolor='rgba(128,128,128,0.2)',
        title_standoff=20,
        domain=[0.06, 0.24]  # Espaçamento consistente
    )
    
    # Configurar eixos X
    fig.update_xaxes(
        gridcolor='rgba(128,128,128,0.2)', 
        showgrid=True,
        rangeslider=dict(visible=False)  # Remove o slider para mais espaço
    )
    
    # Ajustar posição dos títulos dos subplots
    for i in range(len(fig.layout.annotations)):
        fig.layout.annotations[i].update(
            font=dict(size=14, color='white'),
            y=fig.layout.annotations[i].y + 0.03  # Ajuste fino da posição do título
        )
    
    return fig