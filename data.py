import yfinance as yf
import pandas as pd
import streamlit as st

@st.cache_data
def fetch_data(ticker, start_date, end_date):
    """
    Fetches historical data from yfinance.
    
    Args:
        ticker (str): Ticker symbol (e.g., 'AAPL', 'BTC-USD').
        start_date (datetime): Start date.
        end_date (datetime): End date.
        
    Returns:
        pd.DataFrame: DataFrame with historical data, or None if empty/error.
    """
    try:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
        
        if data.empty:
            st.warning(f"No data found for {ticker}. Please check the symbol and dates.")
            return None
            
        # Handle MultiIndex columns (common in new yfinance versions)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            
        # Ensure we have standardized column names
        data = data.rename(columns={
            "Open": "Open",
            "High": "High",
            "Low": "Low",
            "Close": "Close",
            "Volume": "Volume"
        })
        
        return data

    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None
