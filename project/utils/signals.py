"""
Módulo para geração de sinais de trading.
"""

def get_signal_color(row):
    """
    Determina a cor do sinal baseado nas condições dos indicadores.
    
    Args:
        row: Linha do DataFrame com indicadores
        
    Returns:
        str: Cor do sinal ('green', 'red', ou 'black')
    """
    try:
        # Stochastic condition
        stoch_condition = (row['STOCH_K'] > 50) and (row['STOCH_K'] > row['STOCH_K_PREV'])
        
        # RSI condition
        rsi_condition = (row['RSI'] > 50) and (row['RSI'] > row['RSI_PREV'])
        
        # MACD condition
        macd_condition = (row['MACD'] > row['MACD_SIGNAL']) and (row['MACD'] > row['MACD_PREV'])
        
        # Count conditions met
        conditions_met = sum([stoch_condition, rsi_condition, macd_condition])
        
        if conditions_met == 3:
            return 'green'
        elif conditions_met == 0:
            return 'red'
        else:
            return 'black'
    except Exception as e:
        raise Exception(f"Erro ao determinar cor do sinal: {str(e)}")