from flask import Flask, render_template, request
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime, timedelta

app = Flask(__name__)

# In-memory store for portfolio
portfolio = []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Capture stock information from the form
        ticker = request.form['ticker']
        price = float(request.form['purchase_price'])
        shares = int(request.form['shares'])
        
        # Add stock to portfolio
        portfolio.append({'ticker': ticker, 'purchase_price': price, 'shares': shares})
    
    # Fetch stock data and calculate portfolio performance
    data = []
    total_value = 0
    for stock in portfolio:
        ticker_data = yf.Ticker(stock['ticker'])
        stock_history = ticker_data.history(period="1y")
        
        # Calculate current value and stock forecast (simple moving average)
        current_price = stock_history['Close'][-1]
        total_value += current_price * stock['shares']
        
        # Stock price forecast using moving average (for simplicity)
        stock_history['SMA'] = stock_history['Close'].rolling(window=20).mean()
        
        data.append({
            'ticker': stock['ticker'],
            'purchase_price': stock['purchase_price'],
            'current_price': current_price,
            'forecast': stock_history['SMA'][-1]  # Simple forecast (last value of SMA)
        })
    
    # Visualization: Pie Chart for Portfolio Allocation
    labels = [stock['ticker'] for stock in portfolio]
    values = [yf.Ticker(stock['ticker']).history(period="1y")['Close'][-1] * stock['shares'] for stock in portfolio]
    
    fig = px.pie(names=labels, values=values, title='Portfolio Allocation')
    
    # Visualizing performance (Line Chart for portfolio value over time)
    timestamps = [datetime.today() - timedelta(days=i*30) for i in range(len(portfolio))]
    portfolio_values = [total_value for _ in range(len(timestamps))]
    
    fig2, ax2 = plt.subplots()
    ax2.plot(timestamps, portfolio_values, label="Portfolio Value Over Time")
    ax2.set_title("Portfolio Performance")
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Portfolio Value (USD)')
    
    return render_template('index.html', data=data, plot=fig.to_html(), plot2=fig2)

if __name__ == '__main__':
    app.run(debug=True)
