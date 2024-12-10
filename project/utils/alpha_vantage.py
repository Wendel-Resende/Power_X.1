"""
Módulo para integração com a API Alpha Vantage.
"""
import requests
import pandas as pd
from typing import Optional, Dict, Any

class AlphaVantageClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        
    def get_intraday_data(self, symbol: str, interval: str = '5min') -> pd.DataFrame:
        """
        Obtém dados intraday com maior granularidade.
        
        Args:
            symbol: Símbolo do ativo
            interval: Intervalo ('1min', '5min', '15min', '30min', '60min')
        """
        params = {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': symbol,
            'interval': interval,
            'apikey': self.api_key,
            'outputsize': 'full'
        }
        
        data = self._make_request(params)
        if data:
            time_series = data[f'Time Series ({interval})']
            df = pd.DataFrame.from_dict(time_series, orient='index')
            df.index = pd.to_datetime(df.index)
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            df = df.astype(float)
            return df
        return pd.DataFrame()
    
    def get_fundamental_data(self, symbol: str) -> Dict[str, Any]:
        """
        Obtém dados fundamentalistas da empresa.
        """
        params = {
            'function': 'OVERVIEW',
            'symbol': symbol,
            'apikey': self.api_key
        }
        
        return self._make_request(params) or {}
    
    def get_earnings(self, symbol: str) -> Dict[str, Any]:
        """
        Obtém dados de resultados trimestrais.
        """
        params = {
            'function': 'EARNINGS',
            'symbol': symbol,
            'apikey': self.api_key
        }
        
        return self._make_request(params) or {}
    
    def get_global_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Obtém cotação em tempo real.
        """
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': self.api_key
        }
        
        return self._make_request(params) or {}
    
    def _make_request(self, params: Dict[str, str]) -> Optional[Dict]:
        """
        Realiza requisição à API.
        """
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'Error Message' in data:
                raise ValueError(data['Error Message'])
                
            return data
        except Exception as e:
            print(f"Erro na requisição à API: {str(e)}")
            return None