import pandas as pd
import numpy as np

class Strategy:
    def __init__(self, df, initial_capital=100000.0):
        """
        Inicializa a estratégia de backtesting
        
        Args:
            df: DataFrame com dados OHLCV e indicadores
            initial_capital: Capital inicial para simulação
        """
        self.df = df.copy()
        self.initial_capital = initial_capital
        self.positions = pd.DataFrame(index=df.index)
        self.positions['position'] = 0
        self.positions['capital'] = initial_capital
        
    def run_backtest(self):
        """Executa o backtesting da estratégia."""
        # Inicializar variáveis
        capital = self.initial_capital
        position = 0
        trades = []
        
        for i in range(1, len(self.df)):
            row = self.df.iloc[i]
            prev_row = self.df.iloc[i-1]
            
            # Verificar condições de entrada/saída
            stoch_condition = (row['STOCH_K'] > 50) and (row['STOCH_K'] > prev_row['STOCH_K'])
            rsi_condition = (row['RSI'] > 50) and (row['RSI'] > prev_row['RSI'])
            macd_condition = (row['MACD'] > row['MACD_SIGNAL']) and (row['MACD'] > prev_row['MACD'])
            
            buy_signal = all([stoch_condition, rsi_condition, macd_condition])
            sell_signal = not any([stoch_condition, rsi_condition, macd_condition])
            
            # Lógica de trading
            if buy_signal and position == 0:
                # Comprar
                shares = (capital * 0.98) // row['Close']  # 2% para custos
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
                        'capital': capital
                    })
            
            elif sell_signal and position > 0:
                # Vender
                revenue = position * row['Close'] * 0.98  # 2% para custos
                capital += revenue
                trades.append({
                    'date': row.name,
                    'type': 'sell',
                    'price': row['Close'],
                    'shares': position,
                    'revenue': revenue,
                    'capital': capital
                })
                position = 0
            
            # Atualizar posições
            self.positions.iloc[i]['position'] = position
            self.positions.iloc[i]['capital'] = capital + (position * row['Close'] if position > 0 else 0)
        
        return pd.DataFrame(trades)
    
    def get_metrics(self, trades_df):
        """Calcula métricas de performance do backtesting."""
        if trades_df.empty:
            return {
                'total_trades': 0,
                'profitable_trades': 0,
                'win_rate': 0,
                'total_return': 0,
                'annual_return': 0,
                'max_drawdown': 0
            }
        
        # Calcular retornos diários
        daily_returns = self.positions['capital'].pct_change()
        
        # Métricas básicas
        total_trades = len(trades_df[trades_df['type'] == 'sell'])
        initial_value = self.initial_capital
        final_value = self.positions['capital'].iloc[-1]
        total_return = (final_value - initial_value) / initial_value * 100
        
        # Calcular trades lucrativos
        trades_df['profit'] = 0.0
        sell_trades = trades_df[trades_df['type'] == 'sell']
        buy_trades = trades_df[trades_df['type'] == 'buy']
        
        profits = []
        for i in range(len(sell_trades)):
            buy_price = buy_trades.iloc[i]['price']
            sell_price = sell_trades.iloc[i]['price']
            shares = sell_trades.iloc[i]['shares']
            profit = (sell_price - buy_price) * shares
            profits.append(profit)
        
        profitable_trades = sum(1 for p in profits if p > 0)
        
        # Calcular drawdown
        rolling_max = self.positions['capital'].expanding().max()
        drawdown = (self.positions['capital'] - rolling_max) / rolling_max * 100
        max_drawdown = abs(drawdown.min())
        
        # Calcular retorno anualizado
        days = (self.df.index[-1] - self.df.index[0]).days
        annual_return = ((1 + total_return/100) ** (365/days) - 1) * 100
        
        return {
            'total_trades': total_trades,
            'profitable_trades': profitable_trades,
            'win_rate': (profitable_trades / total_trades * 100) if total_trades > 0 else 0,
            'total_return': total_return,
            'annual_return': annual_return,
            'max_drawdown': max_drawdown
        }