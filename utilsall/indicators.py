import numpy as np
import pandas as pd


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

    df["f_up"] = 0
    df["f_low"] = 0
    df["super"] = 0

    print(df.head(3))
    print(df.tail(3))

    for i in df.index:
        if i <= period-1:
            pass
        else:
            if (df.loc[i, "upper"] < df.loc[i-1, "f_up"]) | (df.loc[i-1, "close"] > df.loc[i-1, "f_up"]):
                df.loc[i, "f_up"] = df.loc[i, "upper"]
            else:
                df.loc[i, "f_up"] = df.loc[i-1, "f_up"]

    for i in df.index:
        if i <= period-1:
            pass
        else:
            if (df.loc[i, "lower"] < df.loc[i - 1, "f_low"]) | (df.loc[i - 1, "close"] > df.loc[i - 1, "f_low"]):
                df.loc[i, "f_low"] = df.loc[i, "lower"]
            else:
                df.loc[i, "f_low"] = df.loc[i - 1, "f_low"]

    for i in df.index:
        if i <= period-1:
            pass
        elif df.loc[i-1, "super"] == df.loc[i-1, "f_up"] and df.loc[i, "close"] < df.loc[i, "f_up"]:
            df.loc[i, "super"] = df.loc[i, "f_up"]
        elif df.loc[i-1, "super"] == df.loc[i-1, "f_up"] and df.loc[i, "close"] > df.loc[i, "f_up"]:
            df.loc[i, "super"] = df.loc[i, "f_low"]
        elif df.loc[i-1, "super"] == df.loc[i-1, "f_low"] and df.loc[i, "close"] > df.loc[i, "f_low"]:
            df.loc[i, "super"] = df.loc[i, "f_low"]
        elif df.loc[i-1, "super"] == df.loc[i-1, "f_low"] and df.loc[i, "close"] < df.loc[i, "f_low"]:
            df.loc[i, "super"] = df.loc[i, "f_up"]
    print(df.head(15))
    print(df.tail(15))

    df = df.reset_index(drop=True)
    columns_to_round = ["upper", "super", "lower", "f_up", "f_low"]
    df[columns_to_round] = df[columns_to_round].applymap(lambda x: round(x, 2))

    print_cols = ["high", "low", "upper", "f_up", "super", "lower", "f_low", "close"]
    df_print = df[print_cols].copy()
    print(df_print.head(25))
    print(df_print.tail(25))

    # indi_last_value = df["super"].values[-1]
    # signal_last_value = df["signal"].values[-1]
    # return indi_last_value, signal_last_value


def supertrend2(ohlcv_df, period, multiplier):
    df = ohlcv_df.reset_index().copy()
    df["atr"] = atr(df, period)
    upper_band = ((df["high"] + df["low"]) / 2) + (multiplier * df["atr"])
    lower_band = ((df["high"] + df["low"]) / 2) - (multiplier * df["atr"])
    df["upper"] = upper_band
    df["lower"] = lower_band
    close = df["close"].copy()

    # FINAL UPPER BAND
    final_bands = pd.DataFrame(columns=['upper', 'lower'])
    final_bands.iloc[:, 0] = [x for x in upper_band - upper_band]
    final_bands.iloc[:, 1] = final_bands.iloc[:, 0]

    for i in range(len(final_bands)):
        if i == 0:
            final_bands.iloc[i, 0] = 0
        else:
            if (upper_band[i] < final_bands.iloc[i - 1, 0]) | (close[i - 1] > final_bands.iloc[i - 1, 0]):
                final_bands.iloc[i, 0] = upper_band[i]
            else:
                final_bands.iloc[i, 0] = final_bands.iloc[i - 1, 0]
    # FINAL LOWER BAND
    for i in range(len(final_bands)):
        if i == 0:
            final_bands.iloc[i, 1] = 0
        else:
            if (lower_band[i] > final_bands.iloc[i - 1, 1]) | (close[i - 1] < final_bands.iloc[i - 1, 1]):
                final_bands.iloc[i, 1] = lower_band[i]
            else:
                final_bands.iloc[i, 1] = final_bands.iloc[i - 1, 1]
    df["f_upper"] = final_bands["upper"]
    df["f_lower"] = final_bands["lower"]
    # SUPERTREND

    supertrend = pd.DataFrame(columns=[f'supertrend_{period}'])
    supertrend.iloc[:, 0] = [x for x in final_bands['upper'] - final_bands['upper']]

    for i in range(len(supertrend)):
        if i == 0:
            supertrend.iloc[i, 0] = 0
        elif supertrend.iloc[i - 1, 0] == final_bands.iloc[i - 1, 0] and close[i] < final_bands.iloc[i, 0]:
            supertrend.iloc[i, 0] = final_bands.iloc[i, 0]
        elif supertrend.iloc[i - 1, 0] == final_bands.iloc[i - 1, 0] and close[i] > final_bands.iloc[i, 0]:
            supertrend.iloc[i, 0] = final_bands.iloc[i, 1]
        elif supertrend.iloc[i - 1, 0] == final_bands.iloc[i - 1, 1] and close[i] > final_bands.iloc[i, 1]:
            supertrend.iloc[i, 0] = final_bands.iloc[i, 1]
        elif supertrend.iloc[i - 1, 0] == final_bands.iloc[i - 1, 1] and close[i] < final_bands.iloc[i, 1]:
            supertrend.iloc[i, 0] = final_bands.iloc[i, 0]

    supertrend = supertrend.set_index(upper_band.index)
    supertrend = supertrend.dropna()[1:]
    print(supertrend)
    df["super"] = supertrend[f'supertrend_{period}']

    df = df.reset_index(drop=True)
    columns_to_round = ["upper", "super", "lower"]
    df[columns_to_round] = df[columns_to_round].applymap(lambda x: round(x, 2))

    print_cols = ["high", "low", "upper","f_upper", "super", "lower", "f_lower", "close"]
    df_print = df[print_cols].copy()
    print(df_print.head(25))
    print(df_print.tail(25))

    # indi_last_value = df["super"].values[-1]
    # signal_last_value = df["signal"].values[-1]
    # return indi_last_value, signal_last_value


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