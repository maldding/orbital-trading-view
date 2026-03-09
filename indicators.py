import pandas_ta as ta

class IndicatorCalculator:
    @staticmethod
    def add_indicators(df, params):
        """
        Calculate and add indicators to the DataFrame based on user parameters.
        :param df: Pandas DataFrame with OHLCV data
        :param params: Dictionary containing indicator configurations
        """
        if df is None or df.empty:
            return df

        # EMAs (up to 3)
        for i, period in enumerate(params.get('ema_periods', [])):
            if period > 0:
                df[f'EMA_{period}'] = ta.ema(df['close'], length=period)

        # Bollinger Bands
        bb_length = params.get('bb_length', 20)
        bb_std = params.get('bb_std', 2.0)
        bb = ta.bbands(df['close'], length=bb_length, std=bb_std)
        if bb is not None:
            # Standardize column names for UI consistency
            df[f'BBL_{bb_length}'] = bb.iloc[:, 0]
            df[f'BBM_{bb_length}'] = bb.iloc[:, 1]
            df[f'BBU_{bb_length}'] = bb.iloc[:, 2]

        # RSI
        rsi_length = params.get('rsi_length', 14)
        df[f'RSI_{rsi_length}'] = ta.rsi(df['close'], length=rsi_length)

        # MACD
        macd_fast = params.get('macd_fast', 12)
        macd_slow = params.get('macd_slow', 26)
        macd_signal = params.get('macd_signal', 9)
        macd = ta.macd(df['close'], fast=macd_fast, slow=macd_slow, signal=macd_signal)
        if macd is not None:
            df[f'MACD_{macd_fast}_{macd_slow}_{macd_signal}'] = macd.iloc[:, 0]
            df[f'MACDs_{macd_fast}_{macd_slow}_{macd_signal}'] = macd.iloc[:, 1]
            df[f'MACDh_{macd_fast}_{macd_slow}_{macd_signal}'] = macd.iloc[:, 2]

        # ATR
        atr_length = params.get('atr_length', 14)
        df[f'ATR_{atr_length}'] = ta.atr(df['high'], df['low'], df['close'], length=atr_length)

        # Volume EMA
        vol_ema_length = params.get('vol_ema_length', 20)
        if vol_ema_length > 0:
            df[f'VOL_EMA_{vol_ema_length}'] = ta.ema(df['volume'], length=vol_ema_length)

        return df

if __name__ == "__main__":
    import pandas as pd
    # Test with dummy data
    data = {
        'high': [100]*50,
        'low': [90]*50,
        'close': [95]*50,
        'volume': [1000]*50
    }
    df = pd.DataFrame(data)
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
    print(df.columns.tolist())
