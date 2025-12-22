import yfinance as yf

tickers = ["XAUUSD=X", "EURUSD=X", "JPY=X", "GC=F"]
for t in tickers:
    print(f"--- Fetching {t} ---")
    data = yf.download(t, period="1mo", progress=False)
    print(data.head())
    print(f"Empty? {data.empty}")
