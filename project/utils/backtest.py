"""
Módulo de backtesting usando pandas_ta para indicadores.
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
        self.positions['equity'] = initial_capital
        self.current_capital = initial_capital
        self.max_capital = initial_capital
        
    def _calculate_indicators(self, df):
        """Calcula indicadores usando pandas_ta."""
        # Tendência de Médias Móveis
        df['EMA_9'] = df.ta.ema(length=9)
        df['EMA_21'] = df.ta.ema(length=21)
        df['EMA_200'] = df.ta.ema(length=200)
        
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
        
        # Volume Force Index
        df['VFI'] = df.ta.vfi(high=df['High'], low=df['Low'], close=df['Close'], volume=df['Volume'])
        
        # Average True Range para Stop Loss
        df['ATR'] = df.ta.atr(high=df['High'], low=df['Low'], close=df['Close'], length=14)
        
        return df
    
    def _check_entry_conditions(self, row):
        """Verifica condições de entrada melhoradas."""
        try:
            # 1. Tendência de Longo Prazo (EMA 200)
            long_trend = row['Close'] > row['EMA_200']
            
            # 2. Tendência de Médio Prazo (EMA 21)
            medium_trend = row['EMA_9'] > row['EMA_21']
            
            # 3. Momentum (RSI)
            momentum = row['RSI'] > 50 and row['RSI'] < 70
            
            # 4. Volume Force Index
            volume_confirmation = row['VFI'] > 0
            
            # 5. Stochastic
            stoch_signal = (row['STOCH_K'] > 20 and row['STOCH_K'] < 80 and 
                          row['STOCH_K'] > row['STOCH_K_PREV'])
            
            # 6. MACD
            macd_signal = row['MACD'] > row['MACD_SIGNAL']
            
            # Combinar sinais
            entry_score = sum([
                long_trend * 2,  # Peso maior para tendência longa
                medium_trend * 1.5,  # Peso médio para tendência média
                momentum,
                volume_confirmation,
                stoch_signal,
                macd_signal
            ])
            
            return entry_score >= 5  # Exige pelo menos 5 pontos para entrada
            
        except Exception as e:
            print(f"Erro ao verificar condições de entrada: {str(e)}")
            return False
    
    def _check_exit_conditions(self, row, entry_price):
        """Verifica condições de saída melhoradas."""
        try:
            # 1. Stop Loss (2 ATR)
            stop_loss = entry_price - (2 * row['ATR'])
            if row['Close'] < stop_loss:
                return True, 'stop_loss'
            
            # 2. Reversão de Tendência
            trend_reversal = row['EMA_9'] < row['EMA_21']
            
            # 3. Momentum
            momentum_exit = row['RSI'] > 80 or row['RSI'] < 30
            
            # 4. Volume Force Index
            volume_exit = row['VFI'] < 0
            
            # 5. Stochastic
            stoch_exit = row['STOCH_K'] > 80 or row['STOCH_K'] < 20
            
            # 6. MACD
            macd_exit = row['MACD'] < row['MACD_SIGNAL']
            
            # Combinar sinais de saída
            exit_score = sum([
                trend_reversal * 2,  # Peso maior para reversão
                momentum_exit,
                volume_exit,
                stoch_exit,
                macd_exit
            ])
            
            return exit_score >= 3, 'signal'  # Exige pelo menos 3 pontos para saída
            
        except Exception as e:
            print(f"Erro ao verificar condições de saída: {str(e)}")
            return True, 'error'
    
    def run_backtest(self):
        """Executa o backtest da estratégia."""
        # Calcular indicadores
        self.df = self._calculate_indicators(self.df)
        
        position = 0
        entry_price = 0
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
                should_exit, exit_reason = self._check_exit_conditions(row, entry_price)
                
                if should_exit:
                    revenue = position * current_price * 0.998  # Custos
                    cost = position * entry_price * 1.002  # Custos
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
                        'exit_reason': exit_reason
                    })
                    
                    position = 0
                    entry_price = 0
            
            # Verificar entrada se não houver posição
            elif position == 0:
                if self._check_entry_conditions(row):
                    # Position sizing baseado em risco (1% do capital por trade)
                    risk_per_trade = self.current_capital * 0.01
                    stop_loss = current_price - (2 * row['ATR'])
                    risk_per_share = current_price - stop_loss
                    
                    if risk_per_share > 0:
                        position_size = risk_per_trade / risk_per_share
                        shares = int(min(
                            position_size,
                            (self.current_capital * 0.95) / current_price  # Máximo 95% do capital
                        ))
                        
                        if shares > 0:
                            cost = shares * current_price * 1.002  # Custos
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
            
            # Atualizar posições e curva de capital
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
        
        # Filtrar trades de venda
        sell_trades = trades_df[trades_df['type'] == 'sell'].copy()
        
        # Métricas básicas
        total_trades = len(sell_trades)
        profitable_trades = len(sell_trades[sell_trades['profit'] > 0])
        
        # Retorno total
        final_capital = float(self.positions['equity'].iloc[-1])
        total_return = ((final_capital - self.initial_capital) / self.initial_capital) * 100
        
        # Retorno anualizado
        start_date = self.df.index[0]
        end_date = self.df.index[-1]
        years = (end_date - start_date).days / 365.25
        
        if years > 0:
            annual_return = (((1 + total_return/100) ** (1/years)) - 1) * 100
        else:
            annual_return = total_return
        
        # Drawdown máximo
        portfolio_values = self.positions['equity']
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