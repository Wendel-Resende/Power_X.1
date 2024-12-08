import yfinance as yf

def fetch_stock_data(symbol, period='1y', interval='1d'):
    """Fetch stock data from Yahoo Finance."""
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period=period, interval=interval)
        return df
    except Exception as e:
        raise Exception(f"Error fetching data for {symbol}: {str(e)}")