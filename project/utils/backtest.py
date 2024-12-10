"""
Módulo de backtesting usando pandas_ta para indicadores.
"""
import pandas as pd
import pandas_ta as ta
from datetime import datetime
import numpy as np

class Strategy:
    def __init__(self, df, initial_capital=10000.0):
        """
        Inicializa a estratégia de backtest.
        
        Args:
            df: DataFrame com dados históricos
            initial_capital: Capital inicial para simulação
        """
        self.df = df.copy()
        self.initial_capital = float(initial_capital)
        self.positions = pd.DataFrame(index=df.index)
        self.positions['position'] = 0
        self.positions['capital'] = initial_capital
        self.positions['equity'] = initial_capital  # Renomeado de equity_curve para equity
        self.current_capital = initial_capital
        self.max_capital = initial_capital
    
    def _calculate_indicators(self, df):
        """Calcula indicadores usando pandas_ta."""
        # Stochastic (14,3,3)
        stoch = df.ta.stoch(high='High', low='Low', close='Close', k=14, d=3, smooth_k=3)
        df['STOCH_K'] = stoch[f'STOCHk_14_3_3']
        df['STOCH_D'] = stoch[f'STOCHd_14_3_3']
        df['STOCH_K_PREV'] = df['STOCH_K'].shift(1)
        
        # RSI (7)
        df['RSI'] = df.ta.rsi(close='Close', length=7)
        df['RSI_PREV'] = df['RSI'].shift(1)
        
        # MACD (12,26,9)
        macd = df.ta.macd(close='Close', fast=12, slow=26, signal=9)
        df['MACD'] = macd[f'MACD_12_26_9']
        df['MACD_SIGNAL'] = macd[f'MACDs_12_26_9']
        df['MACD_PREV'] = df['MACD'].shift(1)
        
        return df
    
    def _check_entry_conditions(self, row):
        """Verifica condições de entrada."""
        # Stochastic acima de 50 e subindo
        stoch_condition = (row['STOCH_K'] > 50) and (row['STOCH_K'] > row['STOCH_K_PREV'])
        
        # RSI acima de 50 e subindo
        rsi_condition = (row['RSI'] > 50) and (row['RSI'] > row['RSI_PREV'])
        
        # MACD acima da linha de sinal e subindo
        macd_condition = (row['MACD'] > row['MACD_SIGNAL']) and (row['MACD'] > row['MACD_PREV'])
        
        return all([stoch_condition, rsi_condition, macd_condition])
    
    def _check_exit_conditions(self, row):
        """Verifica condições de saída."""
        # Stochastic abaixo de 50 ou caindo
        stoch_condition = (row['STOCH_K'] <= 50) or (row['STOCH_K'] <= row['STOCH_K_PREV'])
        
        # RSI abaixo de 50 ou caindo
        rsi_condition = (row['RSI'] <= 50) or (row['RSI'] <= row['RSI_PREV'])
        
        # MACD abaixo da linha de sinal ou caindo
        macd_condition = (row['MACD'] <= row['MACD_SIGNAL']) or (row['MACD'] <= row['MACD_PREV'])
        
        return any([stoch_condition, rsi_condition, macd_condition])
    
    def run_backtest(self):
        """Executa o backtest da estratégia."""
        # Calcular indicadores
        self.df = self._calculate_indicators(self.df)
        
        position = 0
        trades = []
        self.current_capital = self.initial_capital
        
        # Inicializar curva de capital
        self.positions['equity'] = self.initial_capital
        
        for i in range(1, len(self.df)):
            current_price = float(self.df['Close'].iloc[i])
            current_date = self.df.index[i]
            row = self.df.iloc[i]
            
            # Verificar saída se houver posição
            if position > 0:
                if self._check_exit_conditions(row):
                    # Calcular resultado do trade
                    last_buy = next((t for t in reversed(trades) if t['type'] == 'buy'), None)
                    if last_buy:
                        revenue = position * current_price * 0.998  # Considerando custos
                        cost = last_buy['cost']
                        profit = revenue - cost
                        profit_pct = (profit / cost) * 100
                        
                        self.current_capital += revenue
                        self.max_capital = max(self.max_capital, self.current_capital)
                        
                        trades.append({
                            'date': current_date,
                            'type': 'sell',
                            'price': current_price,
                            'shares': position,
                            'cost': None,
                            'capital': self.current_capital,
                            'revenue': revenue,
                            'profit': profit,
                            'profit_pct': profit_pct
                        })
                        
                        position = 0
            
            # Verificar entrada se não houver posição
            elif position == 0:
                if self._check_entry_conditions(row):
                    # Calcular tamanho da posição
                    position_size = (self.current_capital * 0.95) / current_price
                    shares = int(position_size)
                    
                    if shares > 0:
                        cost = shares * current_price * 1.002  # Considerando custos
                        if cost <= self.current_capital:
                            position = shares
                            self.current_capital -= cost
                            
                            trades.append({
                                'date': current_date,
                                'type': 'buy',
                                'price': current_price,
                                'shares': shares,
                                'cost': cost,
                                'capital': self.current_capital,
                                'revenue': None,
                                'profit': None,
                                'profit_pct': None
                            })
            
            # Atualizar posições e curva de capital
            current_equity = self.current_capital + (position * current_price if position > 0 else 0)
            self.positions.iloc[i] = {
                'position': position,
                'capital': self.current_capital,
                'equity': current_equity  # Usando 'equity' em vez de 'equity_curve'
            }
        
        trades_df = pd.DataFrame(trades)
        if not trades_df.empty:
            trades_df['date'] = pd.to_datetime(trades_df['date'])
        return trades_df
    
    def get_metrics(self, trades_df):
        """
        Calcula as métricas do backtest.
        
        Args:
            trades_df: DataFrame com histórico de trades
        """
        if trades_df.empty:
            return {
                'total_trades': 0,
                'profitable_trades': 0,
                'win_rate': 0.0,
                'total_return': 0.0,
                'annual_return': 0.0,
                'max_drawdown': 0.0
            }
        
        # Filtrar trades de venda para análise de resultados
        sell_trades = trades_df[trades_df['type'] == 'sell'].copy()
        
        # Métricas básicas
        total_trades = len(sell_trades)
        profitable_trades = len(sell_trades[sell_trades['profit'] > 0])
        
        # Cálculo do retorno total
        final_capital = float(self.positions['equity'].iloc[-1])  # Usando 'equity'
        total_return = ((final_capital - self.initial_capital) / self.initial_capital) * 100
        
        # Cálculo do retorno anualizado
        start_date = self.df.index[0]
        end_date = self.df.index[-1]
        years = (end_date - start_date).days / 365.25
        
        if years > 0:
            annual_return = (((1 + total_return/100) ** (1/years)) - 1) * 100
        else:
            annual_return = total_return
        
        # Cálculo do drawdown máximo
        portfolio_values = self.positions['equity']  # Usando 'equity'
        rolling_max = portfolio_values.expanding(min_periods=1).max()
        drawdowns = (portfolio_values - rolling_max) / rolling_max * 100
        max_drawdown = abs(drawdowns.min())
        
        # Taxa de acerto
        win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0.0
        
        return {
            'total_trades': total_trades,
            'profitable_trades': profitable_trades,
            'win_rate': win_rate,
            'total_return': total_return,
            'annual_return': annual_return,
            'max_drawdown': max_drawdown
        }