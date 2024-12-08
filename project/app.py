import streamlit as st
import pandas as pd
from utils.data import fetch_stock_data
from utils.indicators import calculate_indicators
from utils.plotting import create_dashboard_plot
from utils.backtest import Strategy

st.set_page_config(layout="wide", page_title="Dashboard Financeiro")

def main():
    st.title("Dashboard Financeiro - Análise Técnica")
    
    # Sidebar para configurações
    st.sidebar.header("Configurações")
    symbol = st.sidebar.text_input("Símbolo do Ativo", value="PETR4.SA")
    period = st.sidebar.selectbox(
        "Período",
        options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        index=3
    )
    interval = st.sidebar.selectbox(
        "Intervalo",
        options=["1d", "1wk", "1mo"],
        index=0
    )
    
    # Configurações de Backtesting
    st.sidebar.header("Backtesting")
    initial_capital = st.sidebar.number_input(
        "Capital Inicial (R$)",
        min_value=1000.0,
        value=100000.0,
        step=1000.0
    )
    run_backtest = st.sidebar.button("Executar Backtest")

    try:
        # Carregar dados
        df = fetch_stock_data(symbol, period, interval)
        
        # Calcular indicadores
        df = calculate_indicators(df)
        
        # Adicionar colunas anteriores para comparação
        df['STOCH_K_PREV'] = df['STOCH_K'].shift(1)
        df['RSI_PREV'] = df['RSI'].shift(1)
        df['MACD_PREV'] = df['MACD'].shift(1)
        
        # Determinar cores dos candles
        df['signal_color'] = df.apply(lambda row: 'black', axis=1)  # cor padrão
        for i in range(1, len(df)):
            row = df.iloc[i]
            prev_row = df.iloc[i-1]
            
            stoch_condition = (row['STOCH_K'] > 50) and (row['STOCH_K'] > prev_row['STOCH_K'])
            rsi_condition = (row['RSI'] > 50) and (row['RSI'] > prev_row['RSI'])
            macd_condition = (row['MACD'] > row['MACD_SIGNAL']) and (row['MACD'] > prev_row['MACD'])
            
            conditions_met = sum([stoch_condition, rsi_condition, macd_condition])
            
            if conditions_met == 3:
                df.iloc[i, df.columns.get_loc('signal_color')] = 'green'
            elif conditions_met == 0:
                df.iloc[i, df.columns.get_loc('signal_color')] = 'red'
        
        # Criar gráfico
        fig = create_dashboard_plot(df)
        st.plotly_chart(fig, use_container_width=True)
        
        # Executar backtest se solicitado
        if run_backtest:
            st.header("Resultados do Backtest")
            
            strategy = Strategy(df, initial_capital)
            trades = strategy.run_backtest()
            metrics = strategy.get_metrics(trades)
            
            # Exibir métricas em colunas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Retorno Total", f"{metrics['total_return']:.2f}%")
                st.metric("Retorno Anualizado", f"{metrics['annual_return']:.2f}%")
            with col2:
                st.metric("Total de Trades", metrics['total_trades'])
                st.metric("Taxa de Acerto", f"{metrics['win_rate']:.2f}%")
            with col3:
                st.metric("Drawdown Máximo", f"{metrics['max_drawdown']:.2f}%")
                st.metric("Trades Lucrativos", metrics['profitable_trades'])
            
            # Exibir histórico de trades
            if not trades.empty:
                st.subheader("Histórico de Trades")
                st.dataframe(trades)
        
        # Exibir últimos sinais
        st.subheader("Últimos Sinais")
        last_rows = df.tail(5)[['Close', 'STOCH_K', 'RSI', 'MACD', 'signal_color']]
        st.dataframe(last_rows)
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")

if __name__ == "__main__":
    main()