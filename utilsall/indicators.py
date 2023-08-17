import numpy as np


def simple_moving_average(ohlcv_df, period):
    df = ohlcv_df.copy()
    df["sma"] = df["close"].rolling(period).mean()
    df["signal"] = np.where(df["sma"] < df["close"], 1, np.where(df["sma"] > df["close"], -1, 0))
    indi_last_value = df["sma"].values[-1]
    signal_last_value = df["signal"].values[-1]
    return indi_last_value, signal_last_value


def not_anchored_vwap(ohlcv_df):
    df = ohlcv_df.copy()
    df = df.reset_index()
    last_date_value = df["date"].max().date()
    df["date_only"] = df["date"].dt.date
    last_date_df = df[df["date_only"] == last_date_value].copy()
    # todo check if hlc average, or ohlc avg or other
    last_date_df["avg_price"] = (last_date_df["high"] + last_date_df["low"] + last_date_df["close"]) / 3
    indi_value = (last_date_df["avg_price"] * last_date_df["volume"]).sum() / last_date_df["volume"].sum()
    last_close = df["close"].values[-1]
    if last_close > indi_value:
        signal_value = 1
    elif last_close < indi_value:
        signal_value = -1
    else:
        signal_value = 0
    return indi_value, signal_value


def atr(ohlcv_df, period):
    df = ohlcv_df.copy()
    df["hml"] = df['high'] - df['low']
    df["hmpc"] = abs(df['high'] - df['close'].shift(1))
    df["lmpc"] = abs(df['low'] - df['close'].shift(1))
    df["tr"] = df[["hml", "hmpc", "lmpc"]].max(axis=1)
    avg_tr = df["tr"].rolling(period).mean()
    return avg_tr


def supertrend(ohlcv_df, period, multiplier):
    df = ohlcv_df.reset_index().copy()
    df["atr"] = atr(df, period)
    df["upper"] = ((df["high"] + df["low"]) / 2) + (multiplier * df["atr"])
    df["lower"] = ((df["high"] + df["low"]) / 2) - (multiplier * df["atr"])
    df["super"] = df["upper"].copy()
    for i in range(1, len(df["close"])):
        if (df["close"].loc[i] < df["upper"].loc[i]):  # and (df["close"].loc[i-1] > df["lower"].loc[i-1]):
            df.loc[i, "super"] = df["upper"].loc[i].copy()
        elif (df["close"].loc[i] > df["lower"].loc[i]):  # and (df["close"].loc[i-1] < df["upper"].loc[i-1]):
            df.loc[i, "super"] = df["lower"].loc[i].copy()
        else:
            df.loc[i, "super"] = df["super"].loc[i-1].copy()

    up_signal_mask = (df["close"] > df["super"]) & (df["close"].shift(1) < df["super"].shift(1))
    down_signal_mask = (df["close"] < df["super"]) & (df["close"].shift(1) > df["super"].shift(1))
    # todo this might be fixed after adding shift to super, check once
    df.loc[:, "signal"] = np.where(up_signal_mask, 1, np.where(down_signal_mask, -1, 0))
    df = df.reset_index(drop=True)
    # print(df[["super", "close", "lower", "upper", "signal"]].tail(50))
    indi_last_value = df["super"].values[-1]
    signal_last_value = df["signal"].values[-1]
    return indi_last_value, signal_last_value


def macd(ohlcv_df, period1, period2, period3):
    df = ohlcv_df.copy()
    df["macd"] = df['close'].ewm(span=period1, min_periods=period1).mean() - \
                 df['close'].ewm(span=period2, min_periods=period2).mean()
    df["macd_signal"] = df["macd"].ewm(span=period3, min_periods=period3).mean()
    df["macd_histogram"] = df["macd"] - df["macd_signal"]

    up_signal_mask = (df["macd_histogram"] > 0) & (df["macd_histogram"].shift(1) < 0)
    down_signal_mask = (df["macd_histogram"] < 0) & (df["macd_histogram"].shift(1) > 0)
    df["signal"] = np.where(up_signal_mask, 1, np.where(down_signal_mask, -1, 0))

    indi_last_value = df["macd_signal"].values[-1]
    signal_last_value = df["signal"].values[-1]
    # print(df[["macd_histogram", "signal"]].iloc[-100:-40])
    return indi_last_value, signal_last_value


def stochastic(ohlcv_df, period, k=3):
    df = ohlcv_df.copy()
    # Calculate the %K line
    df['%k'] = (df['close'] - df['low'].rolling(period).min()) / (df['high'].rolling(period).max() - df['low'].rolling(period).min()) * 100
    df['%d'] = df['%k'].rolling(k).mean()
    df['histogram'] = df['%k'] - df['%d']

    up_signal_mask = (df["%k"] > 60) & (df["%k"].shift(1) < 60)
    down_signal_mask = (df["%k"] < 60) & (df["%k"].shift(1) > 60)
    df["signal"] = np.where(up_signal_mask, 1, np.where(down_signal_mask, -1, 0))

    indi_last_value = df["%k"].values[-1]
    signal_last_value = df["signal"].values[-1]
    # print(df[["%k", "%d", "histogram", "signal"]].iloc[-100:-40])
    return indi_last_value, signal_last_value


if __name__ == "__main__":
    from kite_make_connection import Kite
    from fnodataprocessor import FnoDataProcessor

    kite = Kite()
    kite.establish_connection()

    bfd = FnoDataProcessor(kite.object, 8960770, "5minute")
    bfd.get_instru_basic_data()
    bfd.set_hist_data()
    data_df = bfd.historical_data_df
    print(data_df)

    # indi = Indicator()

    # atr = atr(ohlcv_df, 14)
    # print(atr)

    # st = supertrend(data_df, period=7, multiplier=0.5)
    # print(st)

    # macd = macd(data_df, 12, 26, 9)
    # print(macd)

    stoc = stochastic(data_df, 14)
    print(stoc)