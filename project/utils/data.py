import yfinance as yf
import pandas as pd
from typing import Dict, Optional

class StockDataManager:
    def __init__(self):
        self._default_symbol = 'PETR4.SA'
        self._valid_periods = {
            "1mo": "1 mês",
            "3mo": "3 meses",
            "6mo": "6 meses",
            "1y": "1 ano",
            "2y": "2 anos",
            "5y": "5 anos"
        }
        self._valid_intervals = {
            "1d": "Diário",
            "1wk": "Semanal",
            "1mo": "Mensal"
        }
    
    def get_default_symbol(self) -> str:
        """Retorna o símbolo padrão."""
        return self._default_symbol
    
    def get_valid_periods(self) -> Dict[str, str]:
        """Retorna os períodos válidos."""
        return self._valid_periods
    
    def get_valid_intervals(self) -> Dict[str, str]:
        """Retorna os intervalos válidos."""
        return self._valid_intervals
    
    def fetch_stock_data(self, symbol: str, period: str = '1y', interval: str = '1d') -> pd.DataFrame:
        """Busca dados históricos de uma ação."""
        try:
            # Validar período e intervalo
            if period not in self._valid_periods:
                raise ValueError(f"Período inválido: {period}")
            if interval not in self._valid_intervals:
                raise ValueError(f"Intervalo inválido: {interval}")
            
            # Validar símbolo
            if not symbol or not isinstance(symbol, str):
                raise ValueError("Símbolo inválido")
            
            # Buscar dados
            stock = yf.Ticker(symbol)
            df = stock.history(period=period, interval=interval)
            
            # Verificar se há dados
            if df.empty:
                raise ValueError(f"Não há dados disponíveis para {symbol}")
            
            # Garantir que o índice está no formato correto
            df.index = pd.to_datetime(df.index)
            
            return df
        
        except Exception as e:
            raise Exception(f"Erro ao buscar dados para {symbol}: {str(e)}")
    
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