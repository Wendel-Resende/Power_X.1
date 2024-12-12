"""
Módulo de gerenciamento de dados com suporte a múltiplas fontes.
"""
import yfinance as yf
import pandas as pd
from typing import Dict, Optional
from datetime import datetime, date
from .alpha_vantage import AlphaVantageClient

class StockDataManager:
    """Gerenciador de dados com suporte a múltiplas fontes."""
    
    def __init__(self, alpha_vantage_key: Optional[str] = None):
        """
        Inicializa o gerenciador com configurações padrão.
        
        Args:
            alpha_vantage_key: Chave da API Alpha Vantage (opcional)
        """
        self._default_symbol = 'PETR4.SA'
        
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
    
    def fetch_stock_data(self, symbol: str, start_date: date, end_date: date,
                        use_alpha_vantage: bool = False) -> pd.DataFrame:
        """
        Busca dados históricos usando a fonte especificada.
        
        Args:
            symbol: Símbolo do ativo
            start_date: Data inicial
            end_date: Data final
            use_alpha_vantage: Se True, usa Alpha Vantage como fonte primária
        """
        try:
            df = None
            
            # Usar Alpha Vantage se selecionado e disponível
            if use_alpha_vantage and self.alpha_vantage:
                print("Buscando dados via Alpha Vantage...")
                df = self.alpha_vantage.get_daily_data(symbol)
                
                if not df.empty:
                    # Filtrar período solicitado
                    df = df[(df.index >= pd.Timestamp(start_date)) & 
                           (df.index <= pd.Timestamp(end_date))]
                    print(f"Dados Alpha Vantage obtidos: {len(df)} registros")
                    return df
                else:
                    print("Nenhum dado encontrado via Alpha Vantage")
            
            # Fallback para yfinance
            print("Buscando dados via Yahoo Finance...")
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date, interval='1d')
            
            if df.empty:
                raise ValueError(f"Não há dados disponíveis para {symbol}")
            
            print(f"Dados Yahoo Finance obtidos: {len(df)} registros")
            return df
            
        except Exception as e:
            raise Exception(f"Erro ao buscar dados para {symbol}: {str(e)}")
    
    def get_symbol_info(self, symbol: str, use_alpha_vantage: bool = False) -> Dict:
        """
        Retorna informações detalhadas sobre um símbolo específico.
        
        Args:
            symbol: Símbolo do ativo
            use_alpha_vantage: Se True, usa Alpha Vantage como fonte primária
        """
        try:
            if use_alpha_vantage and self.alpha_vantage:
                print("Buscando informações via Alpha Vantage...")
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
            print("Buscando informações via Yahoo Finance...")
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