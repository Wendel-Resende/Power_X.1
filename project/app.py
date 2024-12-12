"""
Aplicativo principal do dashboard financeiro.
"""
import streamlit as st
from utils.data import StockDataManager
from utils.indicators import calculate_indicators
from utils.plotting import create_dashboard_plot
from utils.backtest import Strategy
from utils.ml import MLPredictor
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(layout="wide", page_title="Dashboard Financeiro")

def initialize_session_state():
    """Inicializa o estado da sessão com valores padrão."""
    if 'data_manager' not in st.session_state:
        alpha_vantage_key = st.secrets.get("ALPHA_VANTAGE_KEY", None)
        st.session_state.data_manager = StockDataManager(alpha_vantage_key)
    if 'ml_predictor' not in st.session_state:
        st.session_state.ml_predictor = MLPredictor()

def render_sidebar():
    """Renderiza a barra lateral com as configurações."""
    st.sidebar.header("Configurações")
    
    symbol = st.sidebar.text_input(
        "Símbolo do Ativo (ex: PETR4.SA)",
        value=st.session_state.data_manager.default_symbol
    )
    
    # Seleção de datas
    st.sidebar.subheader("Período")
    end_date = st.sidebar.date_input(
        "Data Final",
        value=datetime.now(),
        max_value=datetime.now()
    )
    start_date = st.sidebar.date_input(
        "Data Inicial",
        value=end_date - timedelta(days=365),
        max_value=end_date
    )
    
    use_alpha_vantage = False
    if hasattr(st.session_state.data_manager, 'alpha_vantage'):
        use_alpha_vantage = st.sidebar.checkbox(
            "Usar Alpha Vantage",
            value=False,
            help="Utiliza a API Alpha Vantage para dados diários"
        )
    
    st.sidebar.header("Machine Learning")
    use_ml = st.sidebar.checkbox(
        "Usar Previsões ML",
        value=True,
        help="Combina análise técnica com previsões de machine learning"
    )
    
    st.sidebar.header("Backtesting")
    initial_capital = st.sidebar.number_input(
        "Capital Inicial (R$)",
        min_value=1000.0,
        value=10000.0,
        step=1000.0,
        format="%.2f"
    )
    
    run_backtest = st.sidebar.button("Executar Backtest")
    
    return symbol, start_date, end_date, use_alpha_vantage, use_ml, initial_capital, run_backtest

def main():
    st.title("Dashboard Financeiro - Análise Técnica + ML")
    
    initialize_session_state()
    
    symbol, start_date, end_date, use_alpha_vantage, use_ml, initial_capital, run_backtest = render_sidebar()
    
    try:
        with st.spinner('Carregando dados do ativo...'):
            df = st.session_state.data_manager.fetch_stock_data(
                symbol, start_date, end_date, use_alpha_vantage
            )
            
            info = st.session_state.data_manager.get_symbol_info(
                symbol, use_alpha_vantage
            )
        
        if df.empty:
            st.warning("Não há dados disponíveis para o período selecionado.")
            return
        
        # Métricas do ativo
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Preço Atual", f"R$ {info['market_price']:.2f}")
        with col2:
            st.metric("Volume", f"{info['volume']:,}")
        with col3:
            if 'pe_ratio' in info:
                st.metric("P/L", info['pe_ratio'])
        
        # Calcular indicadores
        df = calculate_indicators(df)
        
        # Machine Learning
        if use_ml and len(df) > 50:  # Mínimo de dados para ML
            with st.spinner('Treinando modelo...'):
                try:
                    metrics = st.session_state.ml_predictor.train(df)
                    
                    # Mostrar métricas do modelo
                    st.subheader("Métricas do Modelo ML")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Precisão (Treino)", f"{metrics['train_score']:.2%}")
                    with col2:
                        st.metric("Precisão (Teste)", f"{metrics['test_score']:.2%}")
                    with col3:
                        st.metric("RMSE (Teste)", f"{metrics['test_rmse']:.4f}")
                    
                    # Importância das features
                    if 'feature_importance' in metrics:
                        st.subheader("Importância das Features")
                        st.dataframe(metrics['feature_importance'])
                    
                    # Gerar sinais combinados
                    df['signal_color'] = st.session_state.ml_predictor.get_trading_signals(df)
                except Exception as e:
                    st.warning(f"Erro ao treinar modelo ML: {str(e)}")
                    df['signal_color'] = df.apply(lambda row: get_signal_color(row), axis=1)
        else:
            # Usar apenas sinais técnicos
            df['signal_color'] = df.apply(lambda row: get_signal_color(row), axis=1)
        
        # Plotar gráfico
        fig = create_dashboard_plot(df)
        st.plotly_chart(fig, use_container_width=True)
        
        # Backtest
        if run_backtest:
            st.header("Resultados do Backtest")
            
            strategy = Strategy(df, initial_capital)
            trades = strategy.run_backtest()
            metrics = strategy.get_metrics(trades)
            
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
            
            if not trades.empty:
                st.subheader("Histórico de Trades")
                st.dataframe(trades)
        
        st.subheader("Últimos Sinais")
        last_rows = df.tail(5)[['Close', 'STOCH_K', 'RSI', 'MACD', 'signal_color']]
        st.dataframe(last_rows)
        
    except Exception as e:
        st.error(f"Erro ao processar dados: {str(e)}")

if __name__ == "__main__":
    main()