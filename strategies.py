import pandas as pd
import numpy as np

def simple_moving_average_strategy(df, short_window, long_window):
    """
    Generates signals based on SMA crossover.
    Buy (1) when Short SMA > Long SMA.
    Sell (0) when Short SMA < Long SMA.
    """
    signals = pd.DataFrame(index=df.index)
    signals['signal'] = 0.0

    # Calculate SMAs
    signals['short_mavg'] = df['Close'].rolling(window=short_window, min_periods=1).mean()
    signals['long_mavg'] = df['Close'].rolling(window=long_window, min_periods=1).mean()

    # Create signals
    # We want to be Long (1) when short > long.
    signals['signal'] = np.where(signals['short_mavg'] > signals['long_mavg'], 1.0, 0.0)   

    # Generate trading orders (changes in position)
    signals['positions'] = signals['signal'].diff()

    return signals

def rsi_strategy(df, period=14, buy_threshold=30, sell_threshold=70):
    """
    Generates signals based on RSI.
    Buy (1) when RSI < buy_threshold.
    Close (0) when RSI > sell_threshold.
    Holds position in between.
    """
    signals = pd.DataFrame(index=df.index)
    signals['signal'] = np.nan # Initialize with NaN to support ffill
    
    # Calculate RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    signals['rsi'] = 100 - (100 / (1 + rs))
    
    # Logic:
    # Buy when RSI < Buy Threshold (Oversold -> Rebound expected)
    signals.loc[signals['rsi'] < buy_threshold, 'signal'] = 1.0
    
    # Sell when RSI > Sell Threshold (Overbought -> Correction expected)
    signals.loc[signals['rsi'] > sell_threshold, 'signal'] = 0.0
    
    # Forward fill to maintain position
    signals['signal'] = signals['signal'].ffill().fillna(0.0)
    
    signals['positions'] = signals['signal'].diff()
    
    return signals
