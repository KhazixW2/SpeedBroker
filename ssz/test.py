import yfinance as yf
import matplotlib.pyplot as plt

# Download stock data
data = yf.download(['MSFT', 'AAPL', 'GOOG'], period='1mo')

# Plot closing prices
plt.figure(figsize=(12, 6))
data['Close'].plot()
plt.title('Stock Prices - 1 Month')
plt.xlabel('Date')
plt.ylabel('Price (USD)')
plt.legend(['MSFT', 'AAPL', 'GOOG'])
plt.grid(True)
plt.tight_layout()
plt.savefig('ssz/stock_chart.png')
plt.show()

print("Chart saved to ssz/stock_chart.png")
