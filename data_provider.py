import ccxt
import pandas as pd

class DataProvider:
    def __init__(self, exchange_id='binance'):
        if exchange_id == 'binanceus':
            self.exchange = ccxt.binanceus()
        else:
            self.exchange = ccxt.binance()

    def fetch_ohlcv(self, symbol, timeframe='1h', limit=500):
        """
        Fetch OHLCV data from Binance.
        :param symbol: Trading pair (e.g., 'BTC/USDT')
        :param timeframe: Candlestick interval ('1m', '5m', '1h', '4h', '1d')
        :param limit: Number of candles to fetch
        :return: Pandas DataFrame
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            print(f"Error fetching data: {e}")
            raise e

if __name__ == "__main__":
    # Test data fetching
    provider = DataProvider()
    df = provider.fetch_ohlcv('BTC/USDT', timeframe='1h', limit=10)
    if df is not None:
        print(df.head())
    else:
        print("Failed to fetch data.")
