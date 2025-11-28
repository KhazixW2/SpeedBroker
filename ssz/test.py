import yfinance as yf

df = yf.download("AAPL", start="2010-01-01", end="2020-01-01")
print(df.head())
print(df.columns)