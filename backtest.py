import pandas as pd
import numpy as np

class Backtester:
    def __init__(self, data, signals, initial_capital=10000.0, transaction_cost=0.001):
        """
        Initializes the Backtester.
        
        Args:
            data (pd.DataFrame): Historical price data.
            signals (pd.DataFrame): Dataframe with 'signal' column (1=Long, 0=Cash).
            initial_capital (float): Starting capital.
            transaction_cost (float): Cost per trade (e.g., 0.001 for 0.1%).
        """
        self.data = data
        self.signals = signals
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost
        self.portfolio = pd.DataFrame(index=data.index)
        self.trades = []
        
    def run_backtest(self):
        """
        Executes the backtest iterative loop.
        
        Returns:
            portfolio (pd.DataFrame): Contains 'total' value daily.
            trades (pd.DataFrame): List of executed trades.
        """
        cash = self.initial_capital
        holdings = 0
        portfolio_value = []
        
        # Ensure alignment
        prices = self.data['Close']
        signal_series = self.signals['signal']
        
        # Realign if necessary (though indices should match)
        common_index = prices.index.intersection(signal_series.index)
        prices = prices.loc[common_index]
        signal_series = signal_series.loc[common_index]
        
        # Iterate day by day
        for date, price in prices.items():
            signal = signal_series.loc[date]
            
            # Logic:
            # If Signal 1 (Long) and we are in Cash -> BUY
            if signal == 1 and holdings == 0:
                amount_to_invest = cash
                commission = amount_to_invest * self.transaction_cost
                holdings = (amount_to_invest - commission) / price
                cash = 0
                
                self.trades.append({
                    'Date': date,
                    'Type': 'Buy',
                    'Price': price,
                    'Shares': holdings,
                    'Value': amount_to_invest,
                    'Commission': commission
                })
                
            # If Signal 0 (Cash) and we have Holdings -> SELL
            elif (signal == 0 or np.isnan(signal)) and holdings > 0:
                revenue = holdings * price
                commission = revenue * self.transaction_cost
                cash = revenue - commission
                
                self.trades.append({
                    'Date': date,
                    'Type': 'Sell',
                    'Price': price,
                    'Shares': holdings,
                    'Value': revenue,
                    'Commission': commission
                })
                
                holdings = 0
            
            # Calculate total portfolio value for the day
            current_val = cash + (holdings * price)
            portfolio_value.append(current_val)
            
        self.portfolio = pd.DataFrame(index=prices.index)
        self.portfolio['total'] = portfolio_value
        self.portfolio['returns'] = self.portfolio['total'].pct_change()
        
        return self.portfolio, pd.DataFrame(self.trades)
