import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional

class StockDataManager:
    def __init__(self):
        self._symbols_cache: Optional[pd.DataFrame] = None
        self._default_symbol = 'PETR4.SA'
    
    def get_b3_symbols(self) -> pd.DataFrame:
        """Retorna uma lista de símbolos de ações da B3 disponíveis no Yahoo Finance."""
        if self._symbols_cache is not None:
            return self._symbols_cache
        
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
        
        symbols_data = []
        for symbol in common_symbols:
            for suffix in suffixes:
                full_symbol = symbol + suffix
                try:
                    ticker = yf.Ticker(full_symbol)
                    info = ticker.info
                    if info and 'regularMarketPrice' in info and info['regularMarketPrice'] is not None:
                        symbols_data.append({
                            'symbol': full_symbol,
                            'name': info.get('longName', full_symbol),
                            'sector': info.get('sector', 'N/A'),
                            'market_price': info['regularMarketPrice']
                        })
                except Exception:
                    continue
        
        if not symbols_data:
            # Fallback para garantir que pelo menos o símbolo padrão esteja disponível
            symbols_data.append({
                'symbol': self._default_symbol,
                'name': 'Petrobras PN',
                'sector': 'Oil & Gas',
                'market_price': 0.0
            })
        
        self._symbols_cache = pd.DataFrame(symbols_data)
        return self._symbols_cache
    
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