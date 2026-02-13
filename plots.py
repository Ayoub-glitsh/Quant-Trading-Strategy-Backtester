import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

def plot_price_chart(data, trades=None):
    """
    Plots interactive candlestick chart with buy/sell markers.
    """
    fig = go.Figure()

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='Price'
    ))

    # Add Markers
    if trades is not None and not trades.empty:
        buys = trades[trades['Type'] == 'Buy']
        sells = trades[trades['Type'] == 'Sell']

        if not buys.empty:
            fig.add_trace(go.Scatter(
                x=buys['Date'], y=buys['Price'],
                mode='markers',
                marker=dict(symbol='triangle-up', color='green', size=12),
                name='Buy Signal'
            ))
            
        if not sells.empty:
            fig.add_trace(go.Scatter(
                x=sells['Date'], y=sells['Price'],
                mode='markers',
                marker=dict(symbol='triangle-down', color='red', size=12),
                name='Sell Signal'
            ))

    fig.update_layout(
        title='Price History & Trade Signals',
        xaxis_title='Date',
        yaxis_title='Price',
        template='plotly_dark',
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white")
    )
    return fig

def plot_equity_curve(portfolio, benchmark=None):
    """
    Plots the equity curve vs benchmark.
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=portfolio.index, 
        y=portfolio['total'],
        mode='lines',
        name='Strategy Equity',
        line=dict(color='#00CC96')
    ))
    
    if benchmark is not None:
         fig.add_trace(go.Scatter(
            x=benchmark.index, 
            y=benchmark['total'],
            mode='lines',
            name='Buy & Hold',
            line=dict(color='#636EFA', dash='dash')
        ))

    fig.update_layout(
        title='Equity Curve Strategy vs Benchmark',
        xaxis_title='Date',
        yaxis_title='Portfolio Value ($)',
        template='plotly_dark',
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white")
    )
    return fig
