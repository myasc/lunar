from utilsall.kite_make_connection import Kite
from fnodataprocessor import FnoDataProcessor
from utilsall.indicators import simple_moving_average, not_anchored_vwap, supertrend, macd, stochastic
import pandas as pd
from time import sleep
import datetime as dt
from pprint import pprint

import warnings
warnings.filterwarnings('ignore')

kite = Kite()
kite.establish_connection()

bfd = FnoDataProcessor(kite.object, 8960770, "5minute")
bfd.get_instru_basic_data()
while True:
    bfd.set_hist_data()
    print(bfd.historical_data_df.tail(5))
    data_df = bfd.historical_data_df.iloc[:-1].copy()
    print(dt.datetime.now(), "-" * 50)
    pprint(data_df.iloc[-1])


    sma, sma_signal = simple_moving_average(data_df, 20)
    vwap, vwap_signal = not_anchored_vwap(data_df)
    st, st_signal = supertrend(data_df, period=7, multiplier=3)
    macd_, macd_signal = macd(data_df, 12, 26, 9)
    stoc, stoc_signal = stochastic(data_df, 14)

    print_dict = {"SMA": [sma, sma_signal],
                  "VWAP": [vwap, vwap_signal],
                  "Super": [st, st_signal],
                  "MACD": [macd_, macd_signal],
                  "stocastic": [stoc, stoc_signal]}

    print(pd.DataFrame(print_dict, index=["Indicator value", "Signal"]))
    sleep(5)
