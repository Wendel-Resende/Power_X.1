import streamlit as st
from utils.data import StockDataManager
from utils.indicators import calculate_indicators
from utils.plotting import create_dashboard_plot
from utils.backtest import Strategy

st.set_page_config(layout="wide", page_title="Dashboard Financeiro")

def initialize_session_state():
    """Inicializa o estado da sessão com valores padrão."""
    if 'data_manager' not in st.session_state:
        # Inicializar com a chave da Alpha Vantage se disponível
        alpha_vantage_key = st.secrets.get("ALPHA_VANTAGE_KEY", None)
        st.session_state.data_manager = StockDataManager(alpha_vantage_key)

def render_sidebar():
    """Renderiza a barra lateral com as configurações."""
    st.sidebar.header("Configurações")
    
    # Seleção do ativo
    symbol = st.sidebar.text_input(
        "Símbolo do Ativo (ex: BBDC4.SA)",
        value=st.session_state.data_manager.default_symbol
    )
    
    # Período e intervalo
    period = st.sidebar.selectbox(
        "Período",
        options=list(st.session_state.data_manager.valid_periods.keys()),
        format_func=lambda x: st.session_state.data_manager.valid_periods[x],
        index=3  # 1y por padrão
    )
    
    interval = st.sidebar.selectbox(
        "Intervalo",
        options=list(st.session_state.data_manager.valid_intervals.keys()),
        format_func=lambda x: st.session_state.data_manager.valid_intervals[x],
        index=0  # 1d por padrão
    )
    
    # Opção para usar Alpha Vantage
    use_alpha_vantage = False
    if hasattr(st.session_state.data_manager, 'alpha_vantage'):
        use_alpha_vantage = st.sidebar.checkbox(
            "Usar Alpha Vantage para dados intraday",
            value=False,
            help="Utiliza a API Alpha Vantage para dados intraday mais precisos"
        )
    
    # Configurações de Backtesting
    st.sidebar.header("Backtesting")
    initial_capital = st.sidebar.number_input(
        "Capital Inicial (R$)",
        min_value=1000.0,
        value=10000.0,
        step=1000.0,
        format="%.2f"
    )
    
    run_backtest = st.sidebar.button("Executar Backtest")
    
    return symbol, period, interval, use_alpha_vantage, initial_capital, run_backtest

def main():
    st.title("Dashboard Financeiro - Análise Técnica")
    
    # Inicializar estado da sessão
    initialize_session_state()
    
    # Renderizar sidebar e obter configurações
    symbol, period, interval, use_alpha_vantage, initial_capital, run_backtest = render_sidebar()
    
    try:
        # Carregar dados
        with st.spinner('Carregando dados do ativo...'):
            df = st.session_state.data_manager.fetch_stock_data(
                symbol, period, interval, use_alpha_vantage
            )
            
            # Carregar informações adicionais do ativo
            info = st.session_state.data_manager.get_symbol_info(
                symbol, use_alpha_vantage
            )
        
        if df.empty:
            st.warning("Não há dados disponíveis para o período selecionado.")
            return
        
        # Exibir informações do ativo
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
        st.error(f"Erro ao processar dados: {str(e)}")

if __name__ == "__main__":
    main()