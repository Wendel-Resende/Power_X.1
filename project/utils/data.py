import yfinance as yf
import pandas as pd

def get_b3_symbols():
    """Retorna uma lista de símbolos de ações da B3 disponíveis no Yahoo Finance."""
    # Lista base de sufixos comuns para ações brasileiras
    suffixes = ['.SA']
    
    # Lista de símbolos mais comuns da B3
    common_symbols = [
        'PETR4', 'VALE3', 'ITUB4', 'BBDC4', 'ABEV3', 'B3SA3', 'BBAS3',
        'WEGE3', 'RENT3', 'SUZB3', 'JBSS3', 'ITSA4', 'MGLU3', 'RAIL3',
        'CIEL3', 'RADL3', 'TOTS3', 'UGPA3', 'CCRO3', 'VIVT3', 'LREN3',
        'BRFS3', 'CPFE3', 'ELET3', 'ELET6', 'GGBR4', 'CSNA3', 'USIM5',
        'GOAU4', 'BRKM5', 'MRFG3', 'EMBR3', 'CVCB3', 'AZUL4', 'GOLL4'
    ]
    
    # Criar lista completa com sufixos
    symbols = []
    for symbol in common_symbols:
        for suffix in suffixes:
            full_symbol = symbol + suffix
            try:
                # Verificar se o símbolo existe no Yahoo Finance
                ticker = yf.Ticker(full_symbol)
                info = ticker.info
                if info and 'regularMarketPrice' in info and info['regularMarketPrice'] is not None:
                    symbols.append({
                        'symbol': full_symbol,
                        'name': info.get('longName', full_symbol),
                        'sector': info.get('sector', 'N/A')
                    })
            except:
                continue
    
    # Criar DataFrame e garantir que as colunas existam
    df = pd.DataFrame(symbols)
    required_columns = ['symbol', 'name', 'sector']
    for col in required_columns:
        if col not in df.columns:
            df[col] = ''
    
    return df

def fetch_stock_data(symbol, period='1y', interval='1d'):
    """Fetch stock data from Yahoo Finance."""
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period=period, interval=interval)
        if df.empty:
            raise Exception(f"No data available for {symbol}")
        return df
    except Exception as e:
        raise Exception(f"Error fetching data for {symbol}: {str(e)}")