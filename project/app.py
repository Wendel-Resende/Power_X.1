import streamlit as st
import pandas as pd
from utils.data import fetch_stock_data
from utils.indicators import calculate_indicators
from utils.plotting import create_dashboard_plot

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
        
        # Exibir últimos sinais
        st.subheader("Últimos Sinais")
        last_rows = df.tail(5)[['Close', 'STOCH_K', 'RSI', 'MACD', 'signal_color']]
        st.dataframe(last_rows)
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")

if __name__ == "__main__":
    main()