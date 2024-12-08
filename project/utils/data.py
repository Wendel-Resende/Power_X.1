import yfinance as yf
import pandas as pd
from typing import Dict, Optional

class StockDataManager:
    def __init__(self):
        self._default_symbol = 'PETR4.SA'
    
    def get_default_symbol(self) -> str:
        """Retorna o símbolo padrão."""
        return self._default_symbol
    
    def fetch_stock_data(self, symbol: str, period: str = '1y', interval: str = '1d') -> pd.DataFrame:
        """Busca dados históricos de uma ação."""
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(period=period, interval=interval)
            if df.empty:
                raise ValueError(f"No data available for {symbol}")
            return df
        except Exception as e:
            raise Exception(f"Error fetching data for {symbol}: {str(e)}")
    
    def get_symbol_info(self, symbol: str) -> Dict:
        """Retorna informações detalhadas sobre um símbolo específico."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return {
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'N/A'),
                'market_price': info.get('regularMarketPrice', 0.0),
                'currency': info.get('currency', 'BRL'),
                'exchange': info.get('exchange', 'B3'),
                'market_cap': info.get('marketCap', 0.0)
            }
        except Exception:
            return {
                'name': symbol,
                'sector': 'N/A',
                'market_price': 0.0,
                'currency': 'BRL',
                'exchange': 'B3',
                'market_cap': 0.0
            }