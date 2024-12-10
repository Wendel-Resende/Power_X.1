import streamlit as st
from utils.data import StockDataManager
from utils.indicators import calculate_indicators
from utils.plotting import create_dashboard_plot
from utils.backtest import Strategy
from utils.analysis.metrics import calculate_risk_metrics
from utils.analysis.optimization import optimize_parameters
from utils.visualization.charts import create_analysis_charts
from utils.visualization.indicators import create_indicator_charts

st.set_page_config(layout="wide", page_title="Dashboard Financeiro")

def initialize_session_state():
    """Inicializa o estado da sessão com valores padrão."""
    if 'data_manager' not in st.session_state:
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
    
    # Período
    period = st.sidebar.selectbox(
        "Período",
        options=list(st.session_state.data_manager.valid_periods.keys()),
        format_func=lambda x: st.session_state.data_manager.valid_periods[x],
        index=3  # 1y por padrão
    )
    
    # Opção para usar Alpha Vantage
    use_alpha_vantage = False
    if hasattr(st.session_state.data_manager, 'alpha_vantage'):
        use_alpha_vantage = st.sidebar.checkbox(
            "Usar Alpha Vantage",
            value=False,
            help="Utiliza a API Alpha Vantage para dados diários"
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
    
    # Otimização de Parâmetros
    st.sidebar.header("Otimização")
    optimize = st.sidebar.checkbox("Otimizar Parâmetros", value=False)
    
    run_backtest = st.sidebar.button("Executar Backtest")
    
    return symbol, period, '1d', use_alpha_vantage, initial_capital, run_backtest, optimize

def main():
    st.title("Dashboard Financeiro - Análise Técnica")
    
    # Inicializar estado da sessão
    initialize_session_state()
    
    # Renderizar sidebar e obter configurações
    symbol, period, interval, use_alpha_vantage, initial_capital, run_backtest, optimize = render_sidebar()
    
    try:
        # Carregar dados
        with st.spinner('Carregando dados do ativo...'):
            df = st.session_state.data_manager.fetch_stock_data(
                symbol, period, interval, use_alpha_vantage
            )
            
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
        
        # Criar gráfico principal
        fig = create_dashboard_plot(df)
        st.plotly_chart(fig, use_container_width=True)
        
        # Criar gráfico de indicadores
        st.subheader("Análise de Indicadores")
        fig_indicators = create_indicator_charts(df)
        st.plotly_chart(fig_indicators, use_container_width=True)
        
        # Executar backtest se solicitado
        if run_backtest:
            st.header("Resultados do Backtest")
            
            # Otimizar parâmetros se solicitado
            if optimize:
                with st.spinner("Otimizando parâmetros..."):
                    param_ranges = {
                        'stoch_k': [14, 21, 28],
                        'stoch_d': [3, 5, 7],
                        'rsi_length': [7, 14, 21],
                        'macd_fast': [12, 15, 18],
                        'macd_slow': [26, 30, 34],
                        'macd_signal': [9, 12, 15]
                    }
                    results = optimize_parameters(df, param_ranges)
                    
                    st.subheader("Resultados da Otimização")
                    st.dataframe(results.sort_values('accuracy', ascending=False).head())
            
            strategy = Strategy(df, initial_capital)
            trades = strategy.run_backtest()
            metrics = strategy.get_metrics(trades)
            
            # Métricas básicas
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
            
            # Métricas avançadas de risco
            risk_metrics = calculate_risk_metrics(strategy.positions)
            st.subheader("Métricas de Risco")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Sharpe Ratio", f"{risk_metrics['sharpe_ratio']:.2f}")
            with col2:
                st.metric("Sortino Ratio", f"{risk_metrics['sortino_ratio']:.2f}")
            with col3:
                st.metric("Calmar Ratio", f"{risk_metrics['calmar_ratio']:.2f}")
            
            # Gráficos de análise
            st.subheader("Análise Detalhada")
            fig_analysis = create_analysis_charts(df, trades)
            st.plotly_chart(fig_analysis, use_container_width=True)
            
            # Histórico de trades
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