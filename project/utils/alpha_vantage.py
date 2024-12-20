"""
Módulo para integração com a API Alpha Vantage.
"""
import requests
import pandas as pd
import time
from typing import Optional, Dict
from datetime import datetime, timedelta

class AlphaVantageClient:
    def __init__(self, api_key: str):
        """Inicializa o cliente Alpha Vantage."""
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
    
    def get_daily_data(self, symbol: str) -> pd.DataFrame:
        """
        Obtém dados diários do ativo.
        
        Args:
            symbol: Símbolo do ativo (ex: BBDC4.SA -> BBDC4.SAO)
            
        Returns:
            DataFrame com os dados históricos diários
        """
        self._rate_limit()
        
        # Converter símbolo para formato Alpha Vantage
        symbol = self._convert_symbol(symbol)
        
        params = {
            'function': 'TIME_SERIES_DAILY',  # Usando dados diários
            'symbol': symbol,
            'apikey': self.api_key,
            'outputsize': 'full',
            'datatype': 'json'
        }
        
        data = self._make_request(params)
        if data and 'Time Series (Daily)' in data:
            time_series = data['Time Series (Daily)']
            df = pd.DataFrame.from_dict(time_series, orient='index')
            
            # Renomear colunas para manter compatibilidade
            df.columns = [col.split('. ')[1].capitalize() for col in df.columns]
            df.index = pd.to_datetime(df.index)
            df = df.astype(float)
            
            # Reordenar colunas para manter consistência com yfinance
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
            return df.sort_index()
        return pd.DataFrame()
    
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