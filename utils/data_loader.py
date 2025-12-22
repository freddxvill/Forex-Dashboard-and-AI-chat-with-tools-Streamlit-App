import yfinance as yf
import pandas as pd

def get_forex_data(ticker, period="1mo"):
    """
    Fetches historical forex data from yfinance.
    
    Args:
        ticker (str): The symbol to fetch (e.g., 'EURUSD=X').
        period (str): The period to fetch (e.g., '1mo', '3mo', '1y').
        
    Returns:
        pd.DataFrame: DataFrame with Date, Open, High, Low, Close.
    """
    try:
        # yfinance tickers are standardized
        # Map simpler period names if necessary or pass directly if matching yfinance API
        # yfinance supports: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        
        df = yf.download(ticker, period=period, progress=False)
        
        # Flatten columns if MultiIndex (common in new yfinance)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
            
        return df
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()
