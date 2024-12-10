import pandas as pd
import numpy as np
import pandas_ta as ta
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
        
        # Calcular indicadores usando pandas_ta
        # SMA para tendência e stops
        self.df['SMA_DAILY'] = self.df.ta.sma(close='Close', length=7)
        self.df['SMA_20'] = self.df.ta.sma(close='Close', length=20)
        self.df['trend_filter'] = self.df['Close'] > self.df['SMA_20']
        
        # Stochastic
        stoch = self.df.ta.stoch(high='High', low='Low', close='Close', k=14, d=3, smooth_k=3)
        self.df['STOCH_K'] = stoch['STOCHk_14_3_3']
        self.df['STOCH_D'] = stoch['STOCHd_14_3_3']
        
        # RSI
        self.df['RSI'] = self.df.ta.rsi(close='Close', length=7)
        
        # MACD
        macd = self.df.ta.macd(close='Close', fast=12, slow=26, signal=9)
        self.df['MACD'] = macd[f'MACD_12_26_9']
        self.df['MACD_SIGNAL'] = macd[f'MACDs_12_26_9']
        
        # Calcular sinais
        self.df['stoch_signal'] = (
            (self.df['STOCH_K'] > 50) & 
            (self.df['STOCH_K'] > self.df['STOCH_K'].shift(1))
        ).astype(int)
        
        self.df['rsi_signal'] = (
            (self.df['RSI'] > 50) & 
            (self.df['RSI'] > self.df['RSI'].shift(1))
        ).astype(int)
        
        self.df['macd_signal'] = (
            (self.df['MACD'] > self.df['MACD_SIGNAL']) & 
            (self.df['MACD'] > self.df['MACD'].shift(1))
        ).astype(int)
    
    def run_backtest(self):
        """Executa o backtest da estratégia."""
        position = 0
        trades = []
        self.current_capital = self.initial_capital
        last_buy_index = None
        
        for i in range(1, len(self.df)):
            current_price = float(self.df['Close'].iloc[i])
            current_date = self.df.index[i]
            
            # Verificar sinais usando os indicadores
            stoch_signal = bool(self.df['stoch_signal'].iloc[i])
            rsi_signal = bool(self.df['rsi_signal'].iloc[i])
            macd_signal = bool(self.df['macd_signal'].iloc[i])
            trend_signal = bool(self.df['trend_filter'].iloc[i])
            
            all_signals = stoch_signal and rsi_signal and macd_signal and trend_signal
            
            # Verificar condições de saída se houver posição
            if position > 0:
                last_buy = next((t for t in reversed(trades) if t['type'] == 'buy'), None)
                if last_buy:
                    entry_price = last_buy['price']
                    
                    # Trailing stop dinâmico
                    max_price_since_entry = self.df['High'].iloc[last_buy_index:i+1].max()
                    trailing_stop = max_price_since_entry * 0.98  # 2% abaixo da máxima
                    
                    # Stop loss fixo
                    fixed_stop = entry_price * 0.97  # 3% abaixo do preço de entrada
                    
                    # Usar o stop mais alto entre trailing e fixo
                    stop_loss = max(trailing_stop, fixed_stop)
                    
                    # Take profit dinâmico baseado na volatilidade
                    atr = self.df.ta.atr(high='High', low='Low', close='Close', length=14).iloc[i]
                    take_profit = entry_price + (2 * atr)  # 2x ATR para take profit
                    
                    # Condições de saída
                    stop_loss_hit = current_price <= stop_loss
                    take_profit_hit = current_price >= take_profit
                    exit_signal = not all_signals
                    
                    if stop_loss_hit or take_profit_hit or exit_signal:
                        revenue = position * current_price * 0.998  # Considerando custos
                        cost = last_buy['cost']
                        profit = revenue - cost
                        profit_pct = (profit / cost) * 100
                        
                        self.current_capital += revenue
                        self.max_capital = max(self.max_capital, self.current_capital)
                        
                        exit_reason = ('stop_loss' if stop_loss_hit else 
                                     'take_profit' if take_profit_hit else 'signal')
                        
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
                            'exit_reason': exit_reason
                        })
                        
                        position = 0
            
            # Verificar sinal de compra (todos os indicadores positivos)
            elif all_signals and position == 0:
                # Volume mínimo para entrada
                min_volume = self.df['Volume'].rolling(window=20).mean().iloc[i] * 0.5
                if self.df['Volume'].iloc[i] >= min_volume:
                    # Calcular tamanho da posição baseado no capital disponível
                    position_size = (self.current_capital * 0.95) / current_price  # Usa até 95% do capital
                    shares = int(position_size)
                    
                    if shares > 0:
                        cost = shares * current_price * 1.002  # Considerando custos
                        if cost <= self.current_capital:
                            position = shares
                            last_buy_index = i
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