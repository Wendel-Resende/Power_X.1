import yfinance as yf
import pandas as pd
from typing import Dict, Optional
from datetime import datetime, timedelta

class StockDataManager:
    """Gerenciador de dados usando yfinance."""
    
    def __init__(self):
        """Inicializa o gerenciador com configurações padrão."""
        self._default_symbol = 'BBDC4.SA'
        self._valid_periods = {
            "1mo": "1 mês",
            "3mo": "3 meses", 
            "6mo": "6 meses",
            "1y": "1 ano",
            "2y": "2 anos",
            "5y": "5 anos"
        }
        self._valid_intervals = {
            "1d": "1d",
            "1h": "1h",
            "15m": "15m",
            "5m": "5m",
            "1m": "1m"
        }
    
    @property
    def default_symbol(self) -> str:
        """Retorna o símbolo padrão."""
        return self._default_symbol
    
    @property
    def valid_periods(self) -> Dict[str, str]:
        """Retorna os períodos válidos."""
        return self._valid_periods
    
    @property
    def valid_intervals(self) -> Dict[str, str]:
        """Retorna os intervalos válidos."""
        return self._valid_intervals
    
    def fetch_stock_data(self, symbol: str, period: str = '1y', interval: str = '1d') -> pd.DataFrame:
        """
        Busca dados históricos usando yfinance.
        
        Args:
            symbol: Símbolo do ativo
            period: Período de dados ('1mo', '3mo', '6mo', '1y', '2y', '5y')
            interval: Intervalo dos dados ('1d', '1h', '15m', '5m', '1m')
            
        Returns:
            DataFrame com os dados históricos
        """
        try:
            # Validar período e intervalo
            if period not in self._valid_periods:
                raise ValueError(f"Período inválido: {period}")
            if interval not in self._valid_intervals:
                raise ValueError(f"Intervalo inválido: {interval}")
            
            # Buscar dados do yfinance
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                raise ValueError(f"Não há dados disponíveis para {symbol}")
            
            return df
        
        except Exception as e:
            raise Exception(f"Erro ao buscar dados para {symbol}: {str(e)}")
    
    def get_symbol_info(self, symbol: str) -> Dict:
        """
        Retorna informações detalhadas sobre um símbolo específico.
        
        Args:
            symbol: Símbolo do ativo
            
        Returns:
            Dicionário com informações do ativo
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'name': symbol,
                'description': info.get('longName', 'N/A'),
                'currency': info.get('currency', 'BRL'),
                'market_price': info.get('regularMarketPrice', 0.0),
                'volume': info.get('regularMarketVolume', 0),
                'sector': info.get('sector', 'N/A')
            }
        except Exception:
            return {
                'name': symbol,
                'description': 'N/A',
                'currency': 'BRL',
                'market_price': 0.0,
                'volume': 0,
                'sector': 'N/A'
            }