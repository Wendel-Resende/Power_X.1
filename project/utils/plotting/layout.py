def update_layout(fig):
    """Update the figure layout and styling."""
    fig.update_layout(
        height=1200,  # Aumentado para 1200px para dar mais espaço vertical
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
    
    # Update Y axes com mais espaço
    fig.update_yaxes(
        title_text="Preço", 
        row=1, col=1, 
        gridcolor='rgba(128,128,128,0.2)',
        title_standoff=20,
        domain=[0.6, 1]  # Ajustado para dar mais espaço ao gráfico principal
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
        domain=[0.4, 0.58]  # Espaço para o Stochastic
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
        domain=[0.22, 0.38]  # Espaço para o RSI
    )
    
    fig.update_yaxes(
        title_text="MACD", 
        row=4, col=1, 
        gridcolor='rgba(128,128,128,0.2)',
        title_standoff=20,
        domain=[0, 0.18]  # Espaço para o MACD
    )
    
    # Update X axes
    fig.update_xaxes(gridcolor='rgba(128,128,128,0.2)', showgrid=True)
    
    # Adjust subplot titles
    for i in range(len(fig.layout.annotations)):
        fig.layout.annotations[i].update(
            font=dict(size=14, color='white'),
            y=fig.layout.annotations[i].y + 0.07  # Aumentado para ajustar os títulos
        )
    
    return fig