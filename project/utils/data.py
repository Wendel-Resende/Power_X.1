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
        
        # Inicializar cliente Alpha Vantage se a chave estiver disponível
        self.alpha_vantage = None
        if alpha_vantage_key:
            try:
                self.alpha_vantage = AlphaVantageClient(alpha_vantage_key)
            except Exception as e:
                print(f"Erro ao inicializar Alpha Vantage: {str(e)}")
    
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
            use_alpha_vantage: Se True, tenta usar Alpha Vantage primeiro
        """
        try:
            df = None
            # Tentar Alpha Vantage primeiro se solicitado e disponível
            if use_alpha_vantage and self.alpha_vantage:
                df = self.alpha_vantage.get_daily_data(symbol)  # Sempre usar dados diários do Alpha Vantage
                
                if not df.empty:
                    # Filtrar período solicitado
                    end_date = datetime.now()
                    if period in self._valid_periods:
                        if period == "1mo":
                            start_date = end_date - timedelta(days=30)
                        elif period == "3mo":
                            start_date = end_date - timedelta(days=90)
                        elif period == "6mo":
                            start_date = end_date - timedelta(days=180)
                        elif period == "1y":
                            start_date = end_date - timedelta(days=365)
                        elif period == "2y":
                            start_date = end_date - timedelta(days=730)
                        else:  # 5y
                            start_date = end_date - timedelta(days=1825)
                        
                        df = df[df.index >= start_date]
                    return df
            
            # Fallback para yfinance
            if df is None or df.empty:
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
            use_alpha_vantage: Se True, tenta usar Alpha Vantage primeiro
        """
        try:
            # Tentar Alpha Vantage primeiro se solicitado e disponível
            if use_alpha_vantage and self.alpha_vantage:
                df = self.alpha_vantage.get_daily_data(symbol)
                if not df.empty:
                    last_price = df['Close'].iloc[-1]
                    last_volume = df['Volume'].iloc[-1]
                    return {
                        'name': symbol,
                        'description': symbol,
                        'currency': 'BRL',
                        'market_price': last_price,
                        'volume': last_volume,
                        'sector': 'N/A'
                    }
            
            # Fallback para yfinance
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'name': symbol,
                'description': info.get('longName', 'N/A'),
                'currency': info.get('currency', 'BRL'),
                'market_price': info.get('regularMarketPrice', 0.0),
                'volume': info.get('regularMarketVolume', 0),
                'sector': info.get('sector', 'N/A'),
                'pe_ratio': info.get('forwardPE', None)
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