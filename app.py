import streamlit as st
import pandas as pd
from datetime import date, timedelta
from data import fetch_data
from strategies import simple_moving_average_strategy, rsi_strategy
from backtest import Backtester
from metrics import calculate_metrics
from plots import plot_price_chart, plot_equity_curve

# Page Configuration
st.set_page_config(
    page_title="Quant Trading Backtester",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look and BLACK/WHITE Theme
st.markdown("""
<style>
    /* Main App Background */
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
    }
    
    /* Hide Streamlit Header (Deploy, Menu, etc) */
    header[data-testid="stHeader"] {
        background-color: #000000;
        /* Do NOT set display: none, otherwise sidebar toggle vanishes */
    }
    
    /* Hide Deploy Button */
    .stDeployButton {
        display: none;
    }
    
    /* Hide Main Menu (lazy approach, might need specific testid) */
    [data-testid="stMainMenu"] {
        display: none;
    }    
    /* Hide Footer */
    footer {
        display: none;
    }
    
    /* Metric Card Styling - Blue Theme */
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        color: #00BFFF !important; /* Deep Sky Blue Text */
    }
    
    div[data-testid="stMetricLabel"] {
        color: #87CEFA !important; /* Light Sky Blue Label */
    }
    
    .metric-card {
        background-color: #000033; /* Very Dark Blue Background */
        border: 1px solid #000088;
        padding: 10px;
        border-radius: 5px;
    }

    /* Style st.info (Disclaimer & Instruction Box) */
    .stAlert {
        background-color: rgba(30, 30, 30, 0.5) !important; /* Semi-transparent Dark */
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px;
        backdrop-filter: blur(5px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3); /* "Floo"/Float effect */
    }
    
    /* Icon color inside st.info */
    .stAlert > div[role="alert"] > div:first-child {
        color: #FFFFFF !important;
    }
    
    /* Adjust sidebar background matches config, but ensure text is white */
    section[data-testid="stSidebar"] {
        background-color: #111111;
        border-right: 1px solid #333333;
    }
    
    /* Inputs and Selectbox styling for dark mode */
    .stTextInput > div > div > input {
        color: #FFFFFF;
        background-color: #000000;
        border: 1px solid #555555;
    }
    .stSelectbox > div > div > div {
        color: #FFFFFF;
        background-color: #000000;
    }

    /* Style the Buttons (Run Backtest) */
    .stButton > button {
        background-color: rgba(0, 0, 0, 0.5) !important;
        color: #FFFFFF !important;
        border: 1px solid #555555 !important;
    }
    .stButton > button:hover {
        background-color: rgba(0, 0, 0, 1.0) !important;
        border-color: #FFFFFF !important;
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("Quant Trading Strategy Backtester")
st.markdown("### Professional backtesting engine for technical analysis strategies.")

# --- Sidebar Configuration ---
st.sidebar.header("Configuration")

# Input Parameters
ticker = st.sidebar.text_input("Ticker Symbol", "AAPL").upper()
start_date = st.sidebar.date_input("Start Date", date.today() - timedelta(days=365*2))
end_date = st.sidebar.date_input("End Date", date.today())

st.sidebar.markdown("---")
st.sidebar.subheader("Strategy Settings")
strategy_type = st.sidebar.selectbox("Choose Strategy", ["Simple Moving Average (SMA)", "Relative Strength Index (RSI)"])

initial_capital = st.sidebar.number_input("Initial Capital ($)", value=10000.0, min_value=100.0)
commission = st.sidebar.number_input("Transaction Cost (Rate)", value=0.001, min_value=0.0, format="%.4f", help="e.g. 0.001 = 0.1%")

# Strategy Specific Params
params = {}
if strategy_type == "Simple Moving Average (SMA)":
    short_window = st.sidebar.slider("Short Window", 5, 100, 20)
    long_window = st.sidebar.slider("Long Window", 20, 300, 50)
    params = {'short': short_window, 'long': long_window}
    
elif strategy_type == "Relative Strength Index (RSI)":
    rsi_period = st.sidebar.slider("RSI Period", 5, 30, 14)
    rsi_buy = st.sidebar.slider("Buy Threshold (<)", 10, 50, 30)
    rsi_sell = st.sidebar.slider("Sell Threshold (>)", 50, 90, 70)
    params = {'period': rsi_period, 'buy': rsi_buy, 'sell': rsi_sell}

run_button = st.sidebar.button("Run Backtest", type="primary")

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="
    background-color: #000000;
    color: #FFFFFF;
    padding: 10px;
    border-radius: 5px;
    border: 1px solid #333333;
    font-size: 0.85em;
">
    <strong>Disclaimer:</strong> This tool is for educational purposes only. Trading involves risk.
</div>
""", unsafe_allow_html=True)

# --- Main Execution ---
if run_button:
    if start_date >= end_date:
        st.error("Error: Start date must be before end date.")
    else:
        with st.spinner(f"Fetching data for {ticker}..."):
            df = fetch_data(ticker, start_date, end_date)
            
        if df is not None and not df.empty:
            # 1. Calculate Signals
            signals = None
            if strategy_type == "Simple Moving Average (SMA)":
                signals = simple_moving_average_strategy(df, params['short'], params['long'])
            elif strategy_type == "Relative Strength Index (RSI)":
                signals = rsi_strategy(df, params['period'], params['buy'], params['sell'])
                
            # 2. Run Strategy Backtest
            bt_strat = Backtester(df, signals, initial_capital, commission)
            portfolio_strat, trades_strat = bt_strat.run_backtest()
            
            # 3. Run Benchmark Backtest (Buy & Hold)
            benchmark_signals = pd.DataFrame(index=df.index)
            benchmark_signals['signal'] = 1.0 # Always Long
            # Force a position change at start if needed, but Backtester handles signals.
            # If signal is 1 and holdings 0 -> Buy. perfectly handles B&H.
            
            bt_bench = Backtester(df, benchmark_signals, initial_capital, commission)
            portfolio_bench, trades_bench = bt_bench.run_backtest()
            
            # 4. Metrics
            metrics_strat = calculate_metrics(portfolio_strat, trades_strat)
            metrics_bench = calculate_metrics(portfolio_bench, trades_bench)
            
            # 5. Display Layout
            
            # KPI Metrics Row
            st.divider()
            col1, col2, col3, col4, col5 = st.columns(5)
            
            def display_metric(col, label, value, comparison=None, is_percent=True):
                fmt = "{:.2%}" if is_percent else "{:.2f}"
                val_str = fmt.format(value)
                delta_str = None
                if comparison is not None:
                    delta = value - comparison
                    delta_str = f"{delta:+.2%}" if is_percent else f"{delta:+.2f}"
                col.metric(label, val_str, delta_str)

            display_metric(col1, "Total Return", metrics_strat['Total Return'], metrics_bench['Total Return'])
            display_metric(col2, "CAGR", metrics_strat['CAGR'], metrics_bench['CAGR'])
            display_metric(col3, "Sharpe Ratio", metrics_strat['Sharpe Ratio'], metrics_bench['Sharpe Ratio'], is_percent=False)
            display_metric(col4, "Max Drawdown", metrics_strat['Max Drawdown'], metrics_bench['Max Drawdown']) # Inverse color logic handled by Streamlit? usually + is green.
            
            # Win Rate is specific to strategy (Benchmark usually 0 or N/A)
            col5.metric("Win Rate", f"{metrics_strat.get('Win Rate', 0):.2%}", f"{metrics_strat['Number of Trades']} Trades", delta_color="off")
            
            # Charts
            tab1, tab2 = st.tabs(["Equity Curve", "Price & Signals"])
            
            with tab1:
                st.subheader("Equity Curve vs Buy & Hold")
                st.plotly_chart(plot_equity_curve(portfolio_strat, portfolio_bench), use_container_width=True)
                
            with tab2:
                st.subheader(f"{ticker} Price Action")
                st.plotly_chart(plot_price_chart(df, trades_strat), use_container_width=True)
                
            # Trade Log
            with st.expander("View Strategy Trade Log (Simulated)"):
                if not trades_strat.empty:
                    # Format for display
                    trades_display = trades_strat.copy()
                    trades_display['Date'] = trades_display['Date'].dt.date
                    st.dataframe(trades_display, use_container_width=True)
                else:
                    st.info("No trades executed with current strategy settings.")

else:
    st.markdown("""
    <div style="
        background-color: #000000;
        color: #FFFFFF;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #333333;
        text-align: center;
    ">
        Set parameters and click <strong>'Run Backtest'</strong> to start.
    </div>
    """, unsafe_allow_html=True)
