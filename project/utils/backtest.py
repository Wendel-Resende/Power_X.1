"""
Módulo de backtesting com análise técnica.
"""
import pandas as pd
import pandas_ta as ta
import numpy as np

class Strategy:
    def __init__(self, df, initial_capital=10000.0):
        self.df = df.copy()
        self.initial_capital = float(initial_capital)
        self.positions = pd.DataFrame(index=df.index)
        self.positions['position'] = 0
        self.positions['capital'] = initial_capital
        self.current_capital = initial_capital
        self.max_capital = initial_capital
        
    def run_backtest(self):
        """Executa backtest da estratégia."""
        position = 0
        entry_price = 0
        trades = []
        self.current_capital = self.initial_capital
        
        for i in range(1, len(self.df)):
            current_price = float(self.df['Close'].iloc[i])
            current_date = self.df.index[i]
            signal = self.df['signal_color'].iloc[i]
            
            # Verificar saída
            if position > 0:
                # Stop loss (2%)
                stop_loss = entry_price * 0.98
                
                if current_price <= stop_loss or signal == 'red':
                    revenue = position * current_price * 0.998
                    cost = position * entry_price * 1.002
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
                        'profit_pct': profit_pct,
                        'exit_reason': 'stop_loss' if current_price <= stop_loss else 'signal'
                    })
                    
                    position = 0
                    entry_price = 0
            
            # Verificar entrada
            elif position == 0 and signal == 'green':
                # Calcular posição baseada em 1% de risco por trade
                risk_amount = self.current_capital * 0.01
                position_size = int((self.current_capital * 0.95) / current_price)
                
                if position_size > 0:
                    cost = position_size * current_price * 1.002
                    if cost <= self.current_capital:
                        position = position_size
                        entry_price = current_price
                        self.current_capital -= cost
                        
                        trades.append({
                            'date': current_date,
                            'type': 'buy',
                            'price': current_price,
                            'shares': position_size,
                            'cost': cost,
                            'capital': self.current_capital,
                            'revenue': None,
                            'profit': None,
                            'profit_pct': None,
                            'exit_reason': None
                        })
            
            # Atualizar posições
            self.positions.iloc[i] = {
                'position': position,
                'capital': self.current_capital + (position * current_price if position > 0 else 0)
            }
        
        trades_df = pd.DataFrame(trades)
        if not trades_df.empty:
            trades_df['date'] = pd.to_datetime(trades_df['date'])
        return trades_df
    
    def get_metrics(self, trades_df):
        """Calcula métricas do backtest."""
        if trades_df.empty:
            return {
                'total_trades': 0,
                'profitable_trades': 0,
                'win_rate': 0.0,
                'total_return': 0.0,
                'annual_return': 0.0,
                'max_drawdown': 0.0
            }
        
        # Métricas básicas
        total_trades = len(trades_df[trades_df['type'] == 'sell'])
        profitable_trades = len(trades_df[
            (trades_df['type'] == 'sell') & 
            (trades_df['profit'] > 0)
        ])
        
        # Retorno total
        final_capital = float(self.positions['capital'].iloc[-1])
        total_return = ((final_capital - self.initial_capital) / self.initial_capital) * 100
        
        # Retorno anualizado
        days = (self.df.index[-1] - self.df.index[0]).days
        years = days / 365.25
        annual_return = ((1 + total_return/100) ** (1/years) - 1) * 100 if years > 0 else total_return
        
        # Drawdown máximo
        capital_series = self.positions['capital']
        rolling_max = capital_series.expanding().max()
        drawdowns = (capital_series - rolling_max) / rolling_max * 100
        max_drawdown = abs(drawdowns.min())
        
        # Taxa de acerto
        win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
        
        return {
            'total_trades': total_trades,
            'profitable_trades': profitable_trades,
            'win_rate': win_rate,
            'total_return': total_return,
            'annual_return': annual_return,
            'max_drawdown': max_drawdown
        }