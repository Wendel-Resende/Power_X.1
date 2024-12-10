"""
Módulo para integração com a API Alpha Vantage.
"""
import requests
import pandas as pd
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

class AlphaVantageClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.request_limit = 5  # Limite de requisições por minuto
        self.last_request = datetime.now()
    
    def _rate_limit(self):
        """Implementa rate limiting para respeitar limites da API."""
        now = datetime.now()
        if (now - self.last_request).seconds < (60 / self.request_limit):
            wait_time = (60 / self.request_limit) - (now - self.last_request).seconds
            if wait_time > 0:
                time.sleep(wait_time)
        self.last_request = now
    
    def get_intraday_data(self, symbol: str, interval: str = '5min') -> pd.DataFrame:
        """
        Obtém dados intraday com maior granularidade.
        
        Args:
            symbol: Símbolo do ativo (ex: BBDC4.SA -> BBDC4.SAO)
            interval: Intervalo ('1min', '5min', '15min', '30min', '60min')
        """
        self._rate_limit()
        
        # Converter símbolo para formato Alpha Vantage
        symbol = self._convert_symbol(symbol)
        
        params = {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': symbol,
            'interval': interval,
            'apikey': self.api_key,
            'outputsize': 'full',
            'datatype': 'json'
        }
        
        data = self._make_request(params)
        if data and f'Time Series ({interval})' in data:
            time_series = data[f'Time Series ({interval})']
            df = pd.DataFrame.from_dict(time_series, orient='index')
            
            # Renomear colunas para manter padrão
            df.columns = [col.split('. ')[1].capitalize() for col in df.columns]
            df.index = pd.to_datetime(df.index)
            df = df.astype(float)
            
            # Reordenar colunas para manter consistência com yfinance
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
            return df.sort_index()
        return pd.DataFrame()
    
    def get_fundamental_data(self, symbol: str) -> Dict[str, Any]:
        """
        Obtém dados fundamentalistas da empresa.
        
        Args:
            symbol: Símbolo do ativo
        """
        self._rate_limit()
        symbol = self._convert_symbol(symbol)
        
        params = {
            'function': 'OVERVIEW',
            'symbol': symbol,
            'apikey': self.api_key
        }
        
        data = self._make_request(params)
        if data:
            return {
                'pe_ratio': float(data.get('PERatio', 0)) if data.get('PERatio') else None,
                'eps': float(data.get('EPS', 0)) if data.get('EPS') else None,
                'dividend_yield': float(data.get('DividendYield', 0)) if data.get('DividendYield') else None,
                'market_cap': float(data.get('MarketCapitalization', 0)) if data.get('MarketCapitalization') else None,
                'sector': data.get('Sector', 'N/A'),
                'industry': data.get('Industry', 'N/A')
            }
        return {}
    
    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Obtém cotação atual do ativo.
        
        Args:
            symbol: Símbolo do ativo
        """
        self._rate_limit()
        symbol = self._convert_symbol(symbol)
        
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': self.api_key
        }
        
        data = self._make_request(params)
        if data and 'Global Quote' in data:
            quote = data['Global Quote']
            return {
                'price': float(quote.get('05. price', 0)),
                'volume': int(quote.get('06. volume', 0)),
                'change_percent': float(quote.get('10. change percent', '0').strip('%')),
                'high': float(quote.get('03. high', 0)),
                'low': float(quote.get('04. low', 0))
            }
        return {}
    
    def _convert_symbol(self, symbol: str) -> str:
        """Converte símbolo do formato B3 para Alpha Vantage."""
        if '.SA' in symbol:
            return symbol.replace('.SA', '.SAO')
        return symbol
    
    def _make_request(self, params: Dict[str, str]) -> Optional[Dict]:
        """
        Realiza requisição à API com tratamento de erros.
        
        Args:
            params: Parâmetros da requisição
        """
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'Error Message' in data:
                raise ValueError(data['Error Message'])
            if 'Note' in data:  # Limite de API atingido
                raise ValueError("Limite de requisições da API atingido")
                
            return data
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição à API: {str(e)}")
            return None
        except ValueError as e:
            print(f"Erro nos dados da API: {str(e)}")
            return None
        except Exception as e:
            print(f"Erro inesperado: {str(e)}")
            return None