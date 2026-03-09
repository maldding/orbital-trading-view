from data_provider import DataProvider
from indicators import IndicatorCalculator

def verify():
    print("Starting verification...")
    provider = DataProvider()
    symbol = 'BTC/USDT'
    timeframe = '1h'
    
    print(f"Fetching data for {symbol} ({timeframe})...")
    df = provider.fetch_ohlcv(symbol, timeframe=timeframe, limit=100)
    
    if df is None or df.empty:
        print("❌ Data fetching failed!")
        return
    
    print(f"✅ Data fetched successfully. Rows: {len(df)}")
    
    print("Calculating indicators...")
    calc = IndicatorCalculator()
    p = {
        'ema_periods': [20, 50],
        'bb_length': 20, 'bb_std': 2.0,
        'rsi_length': 14,
        'macd_fast': 12, 'macd_slow': 26, 'macd_signal': 9,
        'atr_length': 14,
        'vol_ema_length': 20
    }
    df = calc.add_indicators(df, p)
    
    required_columns = ['EMA_20', 'RSI_14', 'ATR_14', 'MACD_12_26_9', 'BBM_20']
    missing = [col for col in required_columns if col not in df.columns]
    
    if missing:
        print(f"❌ Missing indicators: {missing}")
    else:
        print("✅ All indicators calculated successfully.")
        print(df[required_columns].tail())

if __name__ == "__main__":
    verify()
