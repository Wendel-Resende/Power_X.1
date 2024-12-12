"""
Módulo para indicadores de volatilidade.
"""
import pandas as pd
import pandas_ta as ta
from .base import validate_dataframe

def calculate_bollinger_bands(df, length=20, std=2):
    """Calcula as Bandas de Bollinger."""
    df = validate_dataframe(df)
    
    try:
        # Calcular Bandas de Bollinger usando pandas_ta
        bbands = df.ta.bbands(close='Close', length=length, std=std)
        
        # Obter nomes corretos das colunas
        upper_col = f'BBU_{length}_{std}.0'
        middle_col = f'BBM_{length}_{std}.0'
        lower_col = f'BBL_{length}_{std}.0'
        
        # Adicionar ao DataFrame com nomes simplificados
        df['BB_UPPER'] = bbands[upper_col]
        df['BB_MIDDLE'] = bbands[middle_col]
        df['BB_LOWER'] = bbands[lower_col]
        
        # Calcular largura das bandas
        df['BB_WIDTH'] = (df['BB_UPPER'] - df['BB_LOWER']) / df['BB_MIDDLE']
        
        # Calcular %B (posição do preço em relação às bandas)
        df['BB_PCT'] = (df['Close'] - df['BB_LOWER']) / (df['BB_UPPER'] - df['BB_LOWER'])
        
        return df
        
    except Exception as e:
        raise Exception(f"Erro ao calcular Bandas de Bollinger: {str(e)}")

def calculate_atr(df, length=14):
    """Calcula o Average True Range."""
    df = validate_dataframe(df)
    
    try:
        df['ATR'] = df.ta.atr(high='High', low='Low', close='Close', length=length)
        
        # Normalizar ATR pelo preço
        df['ATR_PCT'] = df['ATR'] / df['Close'] * 100
        
        # Média móvel do ATR
        df['ATR_MA'] = df['ATR'].rolling(window=length).mean()
        
        return df
        
    except Exception as e:
        raise Exception(f"Erro ao calcular ATR: {str(e)}")