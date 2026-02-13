import pandas as pd
import numpy as np

def calculate_metrics(portfolio, trades=None):
    """
    Calculates performance metrics.
    
    Args:
        portfolio (pd.DataFrame): DataFrame with 'total' and 'returns' columns.
        trades (pd.DataFrame): DataFrame with trade history (optional).
    
    Returns:
        dict: Dictionary of metrics.
    """
    metrics = {}
    
    # Risk-free rate assumption (2% annual)
    rf = 0.02
    
    # Total Return
    start_val = portfolio['total'].iloc[0]
    end_val = portfolio['total'].iloc[-1]
    total_return = (end_val / start_val) - 1
    metrics['Total Return'] = total_return
    
    # Annualized Return (CAGR)
    days = (portfolio.index[-1] - portfolio.index[0]).days
    if days > 0:
        cagr = (end_val / start_val) ** (365.0/days) - 1
    else:
        cagr = 0.0
    metrics['CAGR'] = cagr
    
    # Volatility (Annualized)
    volatility = portfolio['returns'].std() * np.sqrt(252)
    metrics['Volatility'] = volatility
    
    # Sharpe Ratio
    excess_returns = portfolio['returns'] - rf/252
    if volatility > 0:
        sharpe_ratio = excess_returns.mean() / portfolio['returns'].std() * np.sqrt(252)
    else:
        sharpe_ratio = 0.0
    metrics['Sharpe Ratio'] = sharpe_ratio
    
    # Max Drawdown
    cumulative_returns = (1 + portfolio['returns']).cumprod()
    peak = cumulative_returns.cummax()
    drawdown = (cumulative_returns - peak) / peak
    max_drawdown = drawdown.min()
    metrics['Max Drawdown'] = max_drawdown
    
    # Trade Metrics
    if trades is not None and not trades.empty:
        metrics['Number of Trades'] = len(trades)
        
        # Win Rate
        # Calculate PnL per trade cycle (Buy -> Sell)
        # Assuming Long-Only: Sell Value - Buy Value - Commissions
        # But 'trades' lists individual executions. We need to pair them or estimate.
        # Simplified: Check if Sell Price > Buy Price (match by order?)
        # Better: Calculate Trade PnL.
        
        # Since we are long only and close position before next trade (usually),
        # A cycle is Buy -> Sell.
        buys = trades[trades['Type'] == 'Buy']
        sells = trades[trades['Type'] == 'Sell']
        
        # Match lengths (take min)
        n = min(len(buys), len(sells))
        if n > 0:
            pnl = (sells.iloc[:n]['Value'].values - sells.iloc[:n]['Commission'].values) - \
                  (buys.iloc[:n]['Value'].values + buys.iloc[:n]['Commission'].values)
            
            winning_trades = np.sum(pnl > 0)
            win_rate = winning_trades / n
            metrics['Win Rate'] = win_rate
        else:
             metrics['Win Rate'] = 0.0
    else:
        metrics['Number of Trades'] = 0
        metrics['Win Rate'] = 0.0
        
    return metrics
