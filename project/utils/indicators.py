import pandas as pd
import pandas_ta as ta

def calculate_indicators(df):
    """Calculate technical indicators for the given dataframe."""
    # Stochastic (14,3,3)
    stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3, smooth_k=3)
    df['STOCH_K'] = stoch['STOCHk_14_3_3']
    df['STOCH_D'] = stoch['STOCHd_14_3_3']
    
    # RSI (7)
    df['RSI'] = ta.rsi(df['Close'], length=7)
    
    # MACD (12,26,9)
    macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
    df['MACD'] = macd['MACD_12_26_9']
    df['MACD_SIGNAL'] = macd['MACDs_12_26_9']
    
    return df

def get_signal_color(row):
    """Determine candle color based on indicator conditions."""
    stoch_condition = (row['STOCH_K'] > 50) and (row['STOCH_K'] > row['STOCH_K_PREV'])
    rsi_condition = (row['RSI'] > 50) and (row['RSI'] > row['RSI_PREV'])
    macd_condition = (row['MACD'] > row['MACD_SIGNAL']) and (row['MACD'] > row['MACD_PREV'])
    
    conditions_met = sum([stoch_condition, rsi_condition, macd_condition])
    
    if conditions_met == 3:
        return 'green'
    elif conditions_met == 0:
        return 'red'
    else:
        return 'black'