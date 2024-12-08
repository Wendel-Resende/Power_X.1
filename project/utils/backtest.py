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
        
        # Calcular médias móveis e indicadores adicionais
        self.df['SMA_20'] = self.df['Close'].rolling(window=20).mean()
        self.df['SMA_50'] = self.df['Close'].rolling(window=50).mean()
        self.df['ATR'] = self.calculate_atr(14)
        self.df['Volatility'] = self.df['ATR'] / self.df['Close'] * 100
        
        for i in range(50, len(self.df)):  # Começar após ter dados suficientes para as médias
            current_price = float(self.df['Close'].iloc[i])
            current_date = self.df.index[i]
            
            # Condições de entrada refinadas
            stoch_condition = (
                (self.df['STOCH_K'].iloc[i] > 20) and  # Não muito sobrevendido
                (self.df['STOCH_K'].iloc[i] < 80) and  # Não muito sobrecomprado
                (self.df['STOCH_K'].iloc[i] > self.df['STOCH_K'].iloc[i-1]) and
                (self.df['STOCH_K'].iloc[i] > self.df['STOCH_D'].iloc[i])  # Cruzamento positivo
            )
            
            rsi_condition = (
                (self.df['RSI'].iloc[i] > 40) and  # Não muito sobrevendido
                (self.df['RSI'].iloc[i] < 70) and  # Não muito sobrecomprado
                (self.df['RSI'].iloc[i] > self.df['RSI'].iloc[i-1])
            )
            
            macd_condition = (
                (self.df['MACD'].iloc[i] > self.df['MACD_SIGNAL'].iloc[i]) and
                (self.df['MACD'].iloc[i] > self.df['MACD'].iloc[i-1]) and
                (self.df['MACD'].iloc[i] > 0)  # MACD positivo
            )
            
            # Filtros de tendência
            trend_condition = (
                (self.df['Close'].iloc[i] > self.df['SMA_20'].iloc[i]) and  # Acima da média de 20
                (self.df['SMA_20'].iloc[i] > self.df['SMA_20'].iloc[i-1]) and  # Média de 20 subindo
                (self.df['SMA_20'].iloc[i] > self.df['SMA_50'].iloc[i])  # Média de 20 acima da de 50
            )
            
            # Filtro de volatilidade
            volatility_condition = self.df['Volatility'].iloc[i] < 3.0  # Volatilidade menor que 3%
            
            # Stop loss dinâmico baseado no ATR
            atr_multiplier = 2.5  # Aumentado para dar mais espaço
            stop_loss = current_price - (self.df['ATR'].iloc[i] * atr_multiplier)
            take_profit = current_price + (self.df['ATR'].iloc[i] * atr_multiplier * 2.0)  # Aumentado para 2.0x
            
            # Verificar condições de saída se houver posição
            if position > 0:
                last_buy = next((t for t in reversed(trades) if t['type'] == 'buy'), None)
                if last_buy:
                    entry_price = last_buy['price']
                    current_stop = max(
                        stop_loss,
                        entry_price * 0.98,  # Stop fixo de 2%
                        last_buy['stop_loss']  # Manter stop anterior se maior
                    )
                    
                    # Condições de saída refinadas
                    stop_hit = current_price <= current_stop
                    target_hit = current_price >= take_profit
                    trend_reversal = (
                        not trend_condition or
                        self.df['Close'].iloc[i] < self.df['SMA_20'].iloc[i] or
                        (self.df['MACD'].iloc[i] < 0 and self.df['MACD'].iloc[i] < self.df['MACD_SIGNAL'].iloc[i])
                    )
                    
                    if stop_hit or target_hit or trend_reversal:
                        revenue = position * current_price * 0.998
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
                            'profit_pct': profit_pct,
                            'exit_reason': 'stop_loss' if stop_hit else 'take_profit' if target_hit else 'trend_reversal'
                        })
                        
                        position = 0
            
            # Verificar sinal de compra com condições melhoradas
            elif all([
                stoch_condition,
                rsi_condition,
                macd_condition,
                trend_condition,
                volatility_condition
            ]) and position == 0:
                # Gerenciamento de risco: máximo de 1.5% do capital por operação
                risk_per_trade = self.current_capital * 0.015
                position_size = risk_per_trade / (current_price - stop_loss)
                shares = int(min(position_size, self.current_capital * 0.95 / current_price))
                
                if shares > 0:
                    cost = shares * current_price * 1.002
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
                            'profit_pct': None,
                            'stop_loss': stop_loss,
                            'take_profit': take_profit
                        })
            
            # Atualizar posições
            self.positions.iloc[i] = {
                'position': position,
                'capital': self.current_capital + (position * current_price if position > 0 else 0)
            }
        
        return pd.DataFrame(trades)
    
    def calculate_atr(self, period):
        """Calcula o Average True Range (ATR)."""
        high = self.df['High']
        low = self.df['Low']
        close = self.df['Close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    def get_metrics(self, trades_df):
        """Calcula as métricas do backtest."""
        if trades_df.empty:
            return {
                'total_trades': 0,
                'profitable_trades': 0,
                'win_rate': 0.0,
                'total_return': 0.0,
                'annual_return': 0.0,
                'max_drawdown': 0.0,
                'avg_profit_per_trade': 0.0,
                'avg_loss_per_trade': 0.0,
                'profit_factor': 0.0
            }
        
        # Filtrar trades de venda para análise de resultados
        sell_trades = trades_df[trades_df['type'] == 'sell'].copy()
        
        # Métricas básicas
        total_trades = len(sell_trades)
        profitable_trades = len(sell_trades[sell_trades['profit'] > 0])
        losing_trades = len(sell_trades[sell_trades['profit'] <= 0])
        
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
        
        # Métricas adicionais
        avg_profit = sell_trades[sell_trades['profit'] > 0]['profit'].mean() if profitable_trades > 0 else 0
        avg_loss = abs(sell_trades[sell_trades['profit'] <= 0]['profit'].mean()) if losing_trades > 0 else 0
        total_profit = sell_trades[sell_trades['profit'] > 0]['profit'].sum()
        total_loss = abs(sell_trades[sell_trades['profit'] <= 0]['profit'].sum())
        profit_factor = total_profit / total_loss if total_loss != 0 else float('inf')
        
        # Taxa de acerto
        win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0.0
        
        return {
            'total_trades': total_trades,
            'profitable_trades': profitable_trades,
            'win_rate': win_rate,
            'total_return': total_return,
            'annual_return': annual_return,
            'max_drawdown': max_drawdown,
            'avg_profit_per_trade': avg_profit,
            'avg_loss_per_trade': avg_loss,
            'profit_factor': profit_factor
        }