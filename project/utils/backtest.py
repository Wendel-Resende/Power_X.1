import pandas as pd
import numpy as np
from datetime import datetime

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
        """Executa o backtest da estratégia."""
        position = 0
        trades = []
        self.current_capital = self.initial_capital
        
        # Calcular média móvel diária para stop loss e take profit
        self.df['SMA_DAILY'] = self.df['Close'].rolling(window=7).mean()
        
        for i in range(1, len(self.df)):
            current_price = float(self.df['Close'].iloc[i])
            current_date = self.df.index[i]
            current_color = self.df['signal_color'].iloc[i]
            current_sma = self.df['SMA_DAILY'].iloc[i]
            
            # Verificar condições de saída se houver posição
            if position > 0:
                last_buy = next((t for t in reversed(trades) if t['type'] == 'buy'), None)
                if last_buy:
                    entry_price = last_buy['price']
                    
                    # Stop loss = média móvel diária * 1.5
                    stop_loss = current_sma * 1.5
                    # Take profit = média móvel diária * 3
                    take_profit = current_sma * 3
                    
                    # Condições de saída
                    stop_loss_hit = current_price <= stop_loss
                    take_profit_hit = current_price >= take_profit
                    black_candle = current_color == 'black'
                    
                    if stop_loss_hit or take_profit_hit or black_candle:
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
            
            # Verificar sinal de compra (apenas em candles verdes)
            elif current_color == 'green' and position == 0:
                # Calcular tamanho da posição baseado no capital disponível
                position_size = (self.current_capital * 0.95) / current_price  # Usa até 95% do capital
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
        """Calcula as métricas do backtest."""
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
        final_capital = float(self.positions['capital'].iloc[-1])
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
        portfolio_values = self.positions['capital']
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