import MetaTrader5 as mt5
import pandas as pd
from typing import Dict, Optional
from datetime import datetime, timedelta

class MT5DataManager:
    """Gerenciador de dados usando MetaTrader5."""
    
    def __init__(self):
        """Inicializa o gerenciador com configurações padrão."""
        self._default_symbol = 'BBDC4'  # Símbolo padrão sem .SA
        self._valid_periods = {
            "1mo": mt5.TIMEFRAME_D1,
            "3mo": mt5.TIMEFRAME_D1,
            "6mo": mt5.TIMEFRAME_D1,
            "1y": mt5.TIMEFRAME_D1,
            "2y": mt5.TIMEFRAME_D1,
            "5y": mt5.TIMEFRAME_D1
        }
        self._valid_intervals = {
            "1d": mt5.TIMEFRAME_D1,
            "1h": mt5.TIMEFRAME_H1,
            "15m": mt5.TIMEFRAME_M15,
            "5m": mt5.TIMEFRAME_M5,
            "1m": mt5.TIMEFRAME_M1
        }
        
        # Inicializar conexão com MT5
        if not mt5.initialize():
            raise Exception("Falha ao inicializar MetaTrader5")
    
    def __del__(self):
        """Finaliza conexão com MT5 ao destruir objeto."""
        mt5.shutdown()
    
    @property
    def default_symbol(self) -> str:
        """Retorna o símbolo padrão."""
        return self._default_symbol
    
    @property
    def valid_periods(self) -> Dict[str, str]:
        """Retorna os períodos válidos."""
        return {k: k for k in self._valid_periods.keys()}
    
    @property
    def valid_intervals(self) -> Dict[str, str]:
        """Retorna os intervalos válidos."""
        return {k: k for k in self._valid_intervals.keys()}
    
    def _get_rates_count(self, period: str) -> int:
        """Calcula quantidade de barras necessárias para o período."""
        periods = {
            "1mo": 30,
            "3mo": 90,
            "6mo": 180,
            "1y": 365,
            "2y": 730,
            "5y": 1825
        }
        return periods.get(period, 365)
    
    def fetch_stock_data(self, symbol: str, period: str = '1y', interval: str = '1d') -> pd.DataFrame:
        """
        Busca dados históricos usando MetaTrader5.
        
        Args:
            symbol: Símbolo do ativo (formato MT5, ex: BBDC4)
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
            
            # Calcular datas
            rates_count = self._get_rates_count(period)
            
            # Buscar dados do MT5
            rates = mt5.copy_rates_from_pos(symbol, 
                                          self._valid_intervals[interval],
                                          0, rates_count)
            
            if rates is None or len(rates) == 0:
                raise ValueError(f"Não há dados disponíveis para {symbol}")
            
            # Converter para DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            
            # Renomear colunas para manter compatibilidade
            df.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'tick_volume': 'Volume'
            }, inplace=True)
            
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
            symbol_info = mt5.symbol_info(symbol)
            
            if symbol_info is None:
                raise ValueError(f"Símbolo não encontrado: {symbol}")
            
            return {
                'name': symbol,
                'description': symbol_info.description,
                'currency': symbol_info.currency_profit,
                'market_price': symbol_info.last,
                'volume': symbol_info.volume,
                'sector': 'N/A'  # MT5 não fornece setor
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