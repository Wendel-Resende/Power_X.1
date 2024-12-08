import pandas as pd
import numpy as np

class Strategy:
    def __init__(self, df, initial_capital=100000.0):
        self.df = df.copy()
        self.initial_capital = initial_capital
        self.positions = pd.DataFrame(index=df.index)
        self.positions['position'] = 0
        self.positions['capital'] = initial_capital
        
    def run_backtest(self):
        capital = self.initial_capital
        position = 0
        trades = []
        
        # Calcular média móvel diária para stop loss e take profit
        self.df['SMA_7'] = self.df['Close'].rolling(window=7).mean()
        
        for i in range(1, len(self.df)):
            current_price = self.df['Close'].iloc[i]
            
            # Condições de entrada/saída
            stoch_condition = (self.df['STOCH_K'].iloc[i] > 50) and (self.df['STOCH_K'].iloc[i] > self.df['STOCH_K'].iloc[i-1])
            rsi_condition = (self.df['RSI'].iloc[i] > 50) and (self.df['RSI'].iloc[i] > self.df['RSI'].iloc[i-1])
            macd_condition = (self.df['MACD'].iloc[i] > self.df['MACD_SIGNAL'].iloc[i]) and (self.df['MACD'].iloc[i] > self.df['MACD'].iloc[i-1])
            
            # Sinais com confirmação de tendência
            buy_signal = all([stoch_condition, rsi_condition, macd_condition])
            
            # Stop loss e take profit dinâmicos
            if position > 0:
                last_buy = next(t for t in reversed(trades) if t['type'] == 'buy')
                entry_price = last_buy['price']
                stop_loss = entry_price * 0.98  # 2% stop loss
                take_profit = entry_price * 1.04  # 4% take profit
                
                if current_price <= stop_loss or current_price >= take_profit:
                    # Vender posição
                    revenue = position * current_price * 0.998  # 0.2% de taxa
                    profit = revenue - last_buy['cost']
                    trades.append({
                        'date': self.df.index[i],
                        'type': 'sell',
                        'price': current_price,
                        'shares': position,
                        'cost': None,
                        'capital': capital + revenue,
                        'revenue': revenue,
                        'profit': profit
                    })
                    capital += revenue
                    position = 0
            
            # Sinal de compra
            elif buy_signal and position == 0:
                # Calcular quantidade de ações baseado no capital disponível
                max_shares = int(capital * 0.95 / current_price)  # Usa 95% do capital disponível
                if max_shares > 0:
                    position = max_shares
                    cost = position * current_price * 1.002  # 0.2% de taxa
                    capital -= cost
                    trades.append({
                        'date': self.df.index[i],
                        'type': 'buy',
                        'price': current_price,
                        'shares': position,
                        'cost': cost,
                        'capital': capital,
                        'revenue': None,
                        'profit': None
                    })
            
            # Atualizar posições
            self.positions.iloc[i]['position'] = position
            self.positions.iloc[i]['capital'] = capital + (position * current_price if position > 0 else 0)
        
        return pd.DataFrame(trades)
    
    def get_metrics(self, trades_df):
        if trades_df.empty:
            return {
                'total_trades': 0,
                'profitable_trades': 0,
                'win_rate': 0.0,
                'total_return': 0.0,
                'annual_return': 0.0,
                'max_drawdown': 0.0
            }
        
        # Calcular métricas
        sell_trades = trades_df[trades_df['type'] == 'sell']
        total_trades = len(sell_trades)
        profitable_trades = len(sell_trades[sell_trades['profit'] > 0])
        
        # Retorno total
        initial_value = self.initial_capital
        final_value = self.positions['capital'].iloc[-1]
        total_return = ((final_value - initial_value) / initial_value) * 100
        
        # Retorno anualizado
        days = (self.df.index[-1] - self.df.index[0]).days
        annual_return = ((1 + total_return/100) ** (365/days) - 1) * 100 if days > 0 else 0
        
        # Drawdown máximo
        portfolio_value = self.positions['capital']
        rolling_max = portfolio_value.expanding().max()
        drawdown = ((portfolio_value - rolling_max) / rolling_max) * 100
        max_drawdown = abs(drawdown.min())
        
        return {
            'total_trades': total_trades,
            'profitable_trades': profitable_trades,
            'win_rate': (profitable_trades / total_trades * 100) if total_trades > 0 else 0.0,
            'total_return': total_return,
            'annual_return': annual_return,
            'max_drawdown': max_drawdown
        }