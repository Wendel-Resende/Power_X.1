"""
Módulo de backtesting com suporte a ML.
"""
import pandas as pd
import pandas_ta as ta
import numpy as np
from .ml_strategy import MLStrategy

class Strategy:
    def __init__(self, df, initial_capital=10000.0):
        self.df = df.copy()
        self.initial_capital = float(initial_capital)
        self.positions = pd.DataFrame(index=df.index)
        self.positions['position'] = 0
        self.positions['capital'] = initial_capital
        self.positions['equity'] = initial_capital
        self.current_capital = initial_capital
        self.max_capital = initial_capital
        self.ml_strategy = MLStrategy()
        
    def _calculate_indicators(self, df):
        """Calcula indicadores técnicos."""
        # Médias móveis
        df['EMA_9'] = df.ta.ema(length=9)
        df['EMA_21'] = df.ta.ema(length=21)
        
        # Stochastic
        stoch = df.ta.stoch(high='High', low='Low', close='Close', k=14, d=3, smooth_k=3)
        df['STOCH_K'] = stoch[f'STOCHk_14_3_3']
        df['STOCH_D'] = stoch[f'STOCHd_14_3_3']
        
        # RSI
        df['RSI'] = df.ta.rsi(close='Close', length=21)
        
        # MACD
        macd = df.ta.macd(close='Close', fast=12, slow=26, signal=9)
        df['MACD'] = macd[f'MACD_12_26_9']
        df['MACD_SIGNAL'] = macd[f'MACDs_12_26_9']
        
        # ATR para stop loss
        df['ATR'] = df.ta.atr(high=df['High'], low=df['Low'], close=df['Close'], length=14)
        
        return df
    
    def run_backtest(self):
        """Executa backtest com ML."""
        # Calcular indicadores
        self.df = self._calculate_indicators(self.df)
        
        # Treinar modelo ML
        print("Treinando modelo...")
        self.ml_strategy.train(self.df)
        
        # Gerar sinais
        self.df['signal_color'] = self.ml_strategy.generate_trading_signals(self.df)
        
        position = 0
        entry_price = 0
        trades = []
        self.current_capital = self.initial_capital
        
        # Inicializar curva de capital
        self.positions['equity'] = self.initial_capital
        
        for i in range(1, len(self.df)):
            current_price = float(self.df['Close'].iloc[i])
            current_date = self.df.index[i]
            signal = self.df['signal_color'].iloc[i]
            
            # Verificar saída
            if position > 0:
                # Stop loss (2 ATR)
                stop_loss = entry_price - (2 * self.df['ATR'].iloc[i])
                
                if current_price < stop_loss or signal == 'red':
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
                        'exit_reason': 'stop_loss' if current_price < stop_loss else 'signal'
                    })
                    
                    position = 0
                    entry_price = 0
            
            # Verificar entrada
            elif position == 0 and signal == 'green':
                risk_per_trade = self.current_capital * 0.01
                stop_loss = current_price - (2 * self.df['ATR'].iloc[i])
                risk_per_share = current_price - stop_loss
                
                if risk_per_share > 0:
                    position_size = risk_per_trade / risk_per_share
                    shares = int(min(
                        position_size,
                        (self.current_capital * 0.95) / current_price
                    ))
                    
                    if shares > 0:
                        cost = shares * current_price * 1.002
                        if cost <= self.current_capital:
                            position = shares
                            entry_price = current_price
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
            current_equity = self.current_capital + (position * current_price if position > 0 else 0)
            self.positions.iloc[i] = {
                'position': position,
                'capital': self.current_capital,
                'equity': current_equity
            }
        
        trades_df = pd.DataFrame(trades)
        if not trades_df.empty:
            trades_df['date'] = pd.to_datetime(trades_df['date'])
        return trades_df