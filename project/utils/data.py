"""
Módulo de gerenciamento de dados com suporte a múltiplas fontes.
"""
import yfinance as yf
import pandas as pd
from typing import Dict, Optional
from datetime import datetime, timedelta
from .alpha_vantage import AlphaVantageClient

class StockDataManager:
    """Gerenciador de dados com suporte a múltiplas fontes."""
    
    def __init__(self, alpha_vantage_key: Optional[str] = None):
        """
        Inicializa o gerenciador com configurações padrão.
        
        Args:
            alpha_vantage_key: Chave da API Alpha Vantage (opcional)
        """
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
        
        self.alpha_vantage = AlphaVantageClient(alpha_vantage_key) if alpha_vantage_key else None
    
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
    
    def fetch_stock_data(self, symbol: str, period: str = '1y', interval: str = '1d', 
                        use_alpha_vantage: bool = False) -> pd.DataFrame:
        """
        Busca dados históricos usando a fonte especificada.
        
        Args:
            symbol: Símbolo do ativo
            period: Período de dados
            interval: Intervalo dos dados
            use_alpha_vantage: Se True, usa Alpha Vantage em vez do yfinance
        """
        try:
            if use_alpha_vantage and self.alpha_vantage:
                # Para dados intraday, usar Alpha Vantage
                if interval in ['1min', '5min', '15min', '30min', '60min']:
                    return self.alpha_vantage.get_intraday_data(symbol, interval)
            
            # Caso contrário, usar yfinance
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                raise ValueError(f"Não há dados disponíveis para {symbol}")
            
            return df
            
        except Exception as e:
            raise Exception(f"Erro ao buscar dados para {symbol}: {str(e)}")
    
    def get_symbol_info(self, symbol: str, use_alpha_vantage: bool = False) -> Dict:
        """
        Retorna informações detalhadas sobre um símbolo específico.
        
        Args:
            symbol: Símbolo do ativo
            use_alpha_vantage: Se True, inclui dados fundamentalistas da Alpha Vantage
        """
        info = {}
        
        try:
            # Dados básicos do yfinance
            ticker = yf.Ticker(symbol)
            yf_info = ticker.info
            
            info.update({
                'name': symbol,
                'description': yf_info.get('longName', 'N/A'),
                'currency': yf_info.get('currency', 'BRL'),
                'market_price': yf_info.get('regularMarketPrice', 0.0),
                'volume': yf_info.get('regularMarketVolume', 0),
                'sector': yf_info.get('sector', 'N/A')
            })
            
            # Adicionar dados da Alpha Vantage se disponível
            if use_alpha_vantage and self.alpha_vantage:
                av_info = self.alpha_vantage.get_fundamental_data(symbol)
                if av_info:
                    info.update({
                        'pe_ratio': av_info.get('PERatio', 'N/A'),
                        'eps': av_info.get('EPS', 'N/A'),
                        'dividend_yield': av_info.get('DividendYield', 'N/A'),
                        'market_cap': av_info.get('MarketCapitalization', 'N/A'),
                        'profit_margin': av_info.get('ProfitMargin', 'N/A'),
                        'quarterly_earnings_growth': av_info.get('QuarterlyEarningsGrowthYOY', 'N/A')
                    })
            
            return info
            
        except Exception:
            return {
                'name': symbol,
                'description': 'N/A',
                'currency': 'BRL',
                'market_price': 0.0,
                'volume': 0,
                'sector': 'N/A'
            }