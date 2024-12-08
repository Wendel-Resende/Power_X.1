import pandas as pd
import pandas_ta as ta

def calculate_stochastic(df, k=14, d=3, smooth_k=3):
    """Calculate Stochastic oscillator."""
    stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=k, d=d, smooth_k=smooth_k)
    df['STOCH_K'] = stoch['STOCHk_14_3_3']
    df['STOCH_D'] = stoch['STOCHd_14_3_3']
    return df

def calculate_rsi(df, length=7):
    """Calculate RSI indicator."""
    df['RSI'] = ta.rsi(df['Close'], length=length)
    return df

def calculate_macd(df, fast=12, slow=26, signal=9):
    """Calculate MACD indicator."""
    macd = ta.macd(df['Close'], fast=fast, slow=slow, signal=signal)
    df['MACD'] = macd[f'MACD_{fast}_{slow}_{signal}']
    df['MACD_SIGNAL'] = macd[f'MACDs_{fast}_{slow}_{signal}']
    df['MACD_HIST'] = macd[f'MACDh_{fast}_{slow}_{signal}']
    return df

def calculate_indicators(df):
    """Calculate all technical indicators."""
    if df is None or df.empty:
        raise ValueError("DataFrame is empty or None")
    
    try:
        # Criar cópia para não modificar o DataFrame original
        df = df.copy()
        
        # Calcular indicadores
        df = calculate_stochastic(df)
        df = calculate_rsi(df)
        df = calculate_macd(df)
        
        # Preencher valores NaN
        df.fillna(method='bfill', inplace=True)
        
        return df
    except Exception as e:
        raise Exception(f"Erro ao calcular indicadores: {str(e)}")

def get_signal_conditions(row, prev_row):
    """
    Determina as condições de sinal com base nos indicadores.
    Retorna um dicionário com as condições individuais.
    """
    return {
        'stoch': (row['STOCH_K'] > 50) and (row['STOCH_K'] > prev_row['STOCH_K']),
        'rsi': (row['RSI'] > 50) and (row['RSI'] > prev_row['RSI']),
        'macd': (row['MACD'] > row['MACD_SIGNAL']) and (row['MACD'] > prev_row['MACD'])
    }

def determine_signal_color(conditions):
    """
    Determina a cor do sinal com base nas condições dos indicadores.
    """
    conditions_met = sum(conditions.values())
    if conditions_met == 3:
        return 'green'
    elif conditions_met == 0:
        return 'red'
    return 'black'