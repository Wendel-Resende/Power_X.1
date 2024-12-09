import pandas as pd
import pandas_ta as ta

def calculate_stochastic(df, k=14, d=3, smooth_k=3):
    """Calculate Stochastic oscillator."""
    try:
        if df is None or df.empty:
            raise ValueError("DataFrame vazio")
            
        stoch = df.ta.stoch(high='High', low='Low', close='Close', k=k, d=d, smooth_k=smooth_k)
        df['STOCH_K'] = stoch[f'STOCHk_{k}_{d}_{smooth_k}']
        df['STOCH_D'] = stoch[f'STOCHd_{k}_{d}_{smooth_k}']
        
        # Calcular valores anteriores para comparação
        df['STOCH_K_PREV'] = df['STOCH_K'].shift(1)
        df['STOCH_D_PREV'] = df['STOCH_D'].shift(1)
        return df
    except Exception as e:
        raise Exception(f"Erro ao calcular Stochastic: {str(e)}")

def calculate_rsi(df, length=7):
    """Calculate RSI indicator."""
    try:
        if df is None or df.empty:
            raise ValueError("DataFrame vazio")
            
        df['RSI'] = df.ta.rsi(close='Close', length=length)
        df['RSI_PREV'] = df['RSI'].shift(1)
        return df
    except Exception as e:
        raise Exception(f"Erro ao calcular RSI: {str(e)}")

def calculate_macd(df, fast=12, slow=26, signal=9):
    """Calculate MACD indicator."""
    try:
        if df is None or df.empty:
            raise ValueError("DataFrame vazio")
            
        macd = df.ta.macd(close='Close', fast=fast, slow=slow, signal=signal)
        df['MACD'] = macd[f'MACD_{fast}_{slow}_{signal}']
        df['MACD_SIGNAL'] = macd[f'MACDs_{fast}_{slow}_{signal}']
        df['MACD_HIST'] = macd[f'MACDh_{fast}_{slow}_{signal}']
        df['MACD_PREV'] = df['MACD'].shift(1)
        return df
    except Exception as e:
        raise Exception(f"Erro ao calcular MACD: {str(e)}")

def calculate_indicators(df):
    """Calculate all technical indicators."""
    if df is None or df.empty:
        raise ValueError("DataFrame está vazio ou None")
    
    try:
        # Criar cópia para não modificar o DataFrame original
        df = df.copy()
        
        # Calcular indicadores
        df = calculate_stochastic(df)
        df = calculate_rsi(df)
        df = calculate_macd(df)
        
        # Calcular sinais
        df['signal_color'] = df.apply(get_signal_color, axis=1)
        
        # Preencher valores NaN
        df = df.fillna(method='bfill').fillna(method='ffill')
        
        return df
    except Exception as e:
        raise Exception(f"Erro ao calcular indicadores: {str(e)}")

def get_signal_color(row):
    """Determine candle color based on indicator conditions."""
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