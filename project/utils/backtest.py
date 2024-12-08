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
            row = self.df.iloc[i]
            prev_row = self.df.iloc[i-1]
            
            # Condições de entrada/saída
            stoch_condition = (row['STOCH_K'] > 50) and (row['STOCH_K'] > prev_row['STOCH_K'])
            rsi_condition = (row['RSI'] > 50) and (row['RSI'] > prev_row['RSI'])
            macd_condition = (row['MACD'] > row['MACD_SIGNAL']) and (row['MACD'] > prev_row['MACD'])
            
            # Filtros de tendência
            sma_20 = self.df['Close'].rolling(window=20).mean()
            sma_50 = self.df['Close'].rolling(window=50).mean()
            trend_condition = sma_20.iloc[i] > sma_50.iloc[i]
            
            # Sinais com confirmação de tendência
            buy_signal = all([stoch_condition, rsi_condition, macd_condition, trend_condition])
            
            # Stop loss e take profit dinâmicos baseados na média móvel diária
            if position > 0:
                entry_price = next(t['price'] for t in reversed(trades) if t['type'] == 'buy')
                stop_loss_price = row['SMA_7'] * 1.5
                take_profit_price = row['SMA_7'] * 3.0
                
                stop_loss_hit = row['Close'] <= stop_loss_price
                take_profit_hit = row['Close'] >= take_profit_price
                
                sell_signal = (not any([stoch_condition, rsi_condition, macd_condition])) or \
                             stop_loss_hit or \
                             take_profit_hit or \
                             (position > 0 and row['Close'] < sma_50.iloc[i])
            else:
                sell_signal = False
            
            # Lógica de trading com position sizing
            if buy_signal and position == 0:
                # Calcular stop loss e take profit baseados na média móvel
                stop_loss_price = row['SMA_7'] * 1.5
                take_profit_price = row['SMA_7'] * 3.0
                stop_distance = row['Close'] - stop_loss_price
                
                if stop_distance > 0:  # Só entra se o stop loss fizer sentido
                    risk_per_trade = capital * 0.02  # 2% do capital por trade
                    position_size = risk_per_trade / stop_distance
                    shares = min(int(position_size), int((capital * 0.98) // row['Close']))
                    
                    cost = shares * row['Close'] * 1.02
                    if cost <= capital:
                        position = shares
                        capital -= cost
                        trades.append({
                            'date': row.name,
                            'type': 'buy',
                            'price': row['Close'],
                            'shares': shares,
                            'cost': cost,
                            'capital': capital,
                            'stop_loss': stop_loss_price,
                            'take_profit': take_profit_price
                        })
            
            elif sell_signal and position > 0:
                revenue = position * row['Close'] * 0.98
                profit = revenue - cost
                exit_reason = 'stop_loss' if row['Close'] <= stop_loss_price else \
                            'take_profit' if row['Close'] >= take_profit_price else 'signal'
                
                capital += revenue
                trades.append({
                    'date': row.name,
                    'type': 'sell',
                    'price': row['Close'],
                    'shares': position,
                    'revenue': revenue,
                    'capital': capital,
                    'profit': profit,
                    'exit_reason': exit_reason
                })
                position = 0
            
            self.positions.iloc[i]['position'] = position
            self.positions.iloc[i]['capital'] = capital + (position * row['Close'] if position > 0 else 0)
        
        return pd.DataFrame(trades)
    
    def get_metrics(self, trades_df):
        if trades_df.empty:
            return self._empty_metrics()
        
        # Métricas básicas
        total_trades = len(trades_df[trades_df['type'] == 'sell'])
        initial_value = self.initial_capital
        final_value = self.positions['capital'].iloc[-1]
        
        # Cálculos de retorno
        total_return = ((final_value - initial_value) / initial_value) * 100
        
        # Análise de trades
        trades_df['profit'] = trades_df.apply(
            lambda x: x['revenue'] - trades_df[trades_df.index < x.name]['cost'].iloc[-1] 
            if x['type'] == 'sell' else 0, axis=1
        )
        
        profitable_trades = len(trades_df[trades_df['profit'] > 0])
        
        # Análise por tipo de saída
        if 'exit_reason' in trades_df.columns:
            stop_loss_trades = len(trades_df[trades_df['exit_reason'] == 'stop_loss'])
            take_profit_trades = len(trades_df[trades_df['exit_reason'] == 'take_profit'])
            signal_trades = len(trades_df[trades_df['exit_reason'] == 'signal'])
        else:
            stop_loss_trades = take_profit_trades = signal_trades = 0
        
        # Métricas de risco
        daily_returns = self.positions['capital'].pct_change()
        volatility = daily_returns.std() * np.sqrt(252)  # Anualizada
        sharpe_ratio = (daily_returns.mean() * 252) / volatility if volatility != 0 else 0
        
        # Drawdown
        rolling_max = self.positions['capital'].expanding().max()
        drawdown = (self.positions['capital'] - rolling_max) / rolling_max * 100
        max_drawdown = abs(drawdown.min())
        
        # Retorno anualizado
        days = (self.df.index[-1] - self.df.index[0]).days
        annual_return = ((1 + total_return/100) ** (365/days) - 1) * 100 if days > 0 else 0
        
        return {
            'total_trades': total_trades,
            'profitable_trades': profitable_trades,
            'win_rate': (profitable_trades / total_trades * 100) if total_trades > 0 else 0,
            'total_return': total_return,
            'annual_return': annual_return,
            'max_drawdown': max_drawdown,
            'volatility': volatility * 100,  # Em percentual
            'sharpe_ratio': sharpe_ratio,
            'stop_loss_trades': stop_loss_trades,
            'take_profit_trades': take_profit_trades,
            'signal_trades': signal_trades
        }
    
    def _empty_metrics(self):
        return {
            'total_trades': 0,
            'profitable_trades': 0,
            'win_rate': 0,
            'total_return': 0,
            'annual_return': 0,
            'max_drawdown': 0,
            'volatility': 0,
            'sharpe_ratio': 0,
            'stop_loss_trades': 0,
            'take_profit_trades': 0,
            'signal_trades': 0
        }