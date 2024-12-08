import pandas as pd
import numpy as np
from datetime import datetime

class Strategy:
    def __init__(self, df, initial_capital=10000.0):
        self.df = df.copy()
        self.initial_capital = initial_capital
        self.positions = pd.DataFrame(index=df.index)
        self.positions['position'] = 0
        self.positions['capital'] = initial_capital
        
    def run_backtest(self):
        """Executa o backtest da estratégia."""
        capital = self.initial_capital
        position = 0
        trades = []
        
        # Calcular média móvel para stop loss e take profit
        self.df['SMA_7'] = self.df['Close'].rolling(window=7).mean()
        
        for i in range(1, len(self.df)):
            current_price = self.df['Close'].iloc[i]
            current_date = self.df.index[i]
            
            # Condições de entrada
            stoch_condition = (self.df['STOCH_K'].iloc[i] > 50) and (self.df['STOCH_K'].iloc[i] > self.df['STOCH_K'].iloc[i-1])
            rsi_condition = (self.df['RSI'].iloc[i] > 50) and (self.df['RSI'].iloc[i] > self.df['RSI'].iloc[i-1])
            macd_condition = (self.df['MACD'].iloc[i] > self.df['MACD_SIGNAL'].iloc[i]) and (self.df['MACD'].iloc[i] > self.df['MACD'].iloc[i-1])
            
            # Stop loss e take profit
            stop_loss = self.df['SMA_7'].iloc[i] * 0.985  # 1.5% abaixo da média móvel
            take_profit = self.df['SMA_7'].iloc[i] * 1.03  # 3% acima da média móvel
            
            # Verificar condições de saída se houver posição
            if position > 0:
                last_buy = next(t for t in reversed(trades) if t['type'] == 'buy')
                entry_price = last_buy['price']
                
                # Condições de saída
                exit_condition = (current_price <= stop_loss) or (current_price >= take_profit)
                
                if exit_condition:
                    # Calcular resultado da operação
                    revenue = position * current_price * 0.998  # Considerando 0.2% de taxa
                    cost = last_buy['cost']
                    profit = revenue - cost
                    profit_pct = (profit / cost) * 100
                    
                    trades.append({
                        'date': current_date,
                        'type': 'sell',
                        'price': current_price,
                        'shares': position,
                        'cost': None,
                        'capital': capital + revenue,
                        'revenue': revenue,
                        'profit': profit,
                        'profit_pct': profit_pct
                    })
                    
                    capital += revenue
                    position = 0
            
            # Verificar sinal de compra
            elif all([stoch_condition, rsi_condition, macd_condition]) and position == 0:
                # Calcular quantidade de ações baseado no capital disponível
                shares = int(capital * 0.95 / current_price)  # Usa 95% do capital disponível
                
                if shares > 0:
                    cost = shares * current_price * 1.002  # Considerando 0.2% de taxa
                    if cost <= capital:
                        position = shares
                        capital -= cost
                        
                        trades.append({
                            'date': current_date,
                            'type': 'buy',
                            'price': current_price,
                            'shares': position,
                            'cost': cost,
                            'capital': capital,
                            'revenue': None,
                            'profit': None,
                            'profit_pct': None
                        })
            
            # Atualizar posições
            self.positions.iloc[i]['position'] = position
            self.positions.iloc[i]['capital'] = capital + (position * current_price if position > 0 else 0)
        
        return pd.DataFrame(trades)
    
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
        final_capital = self.positions['capital'].iloc[-1]
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
        peak = portfolio_values.expanding(min_periods=1).max()
        drawdown = ((portfolio_values - peak) / peak) * 100
        max_drawdown = abs(drawdown.min())
        
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