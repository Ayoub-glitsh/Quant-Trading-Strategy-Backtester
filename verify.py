import pandas as pd
from datetime import date, timedelta
from data import fetch_data
from strategies import simple_moving_average_strategy
from backtest import Backtester
from metrics import calculate_metrics

def verify():
    print("Verifying Quant Trading Backtester...")
    
    # 1. Fetch Data
    print("\nFetching Data for AAPL...")
    end = date.today()
    start = end - timedelta(days=365)
    df = fetch_data("AAPL", start, end)
    
    if df is None or df.empty:
        print("Error: No data fetched.")
        return
        
    print(f"Data fetched: {len(df)} rows.")
    
    # 2. Strategy
    print("\nRunning SMA Strategy (20, 50)...")
    signals = simple_moving_average_strategy(df, 20, 50)
    print("Signals generated.")
    print(signals.tail())
    
    # 3. Backtest
    print("\nRunning Backtest...")
    bt = Backtester(df, signals, initial_capital=10000.0)
    portfolio, trades = bt.run_backtest()
    print("Backtest complete.")
    print(f"Final Portfolio Value: {portfolio['total'].iloc[-1]:.2f}")
    
    # 4. Metrics
    print("\nCalculating Metrics...")
    metrics = calculate_metrics(portfolio, trades)
    for k, v in metrics.items():
        print(f"{k}: {v}")
        
    print("\nVerification Passed!")

if __name__ == "__main__":
    verify()
