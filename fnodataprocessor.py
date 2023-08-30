import datetime as dt
import time

import pandas as pd
pd.set_option("display.max_columns", 50)
from utilsall.historicaldata import HistoricalData
from utilsall import indicators
from config import config


class FnoDataProcessor:
# todo avoid last row from historical data as it keeps getting updated in realtime
    def __init__(self, kite_obj, instru_token, candle_interval):
        self.kite_obj = kite_obj
        self.instru_token = instru_token
        self.candle_interval = candle_interval
        self.instru_name = None
        self.trading_symbol = None
        self.expiry_date = None
        self.strike = None
        self.lot_size = None
        self.instru_type = None

        self.hist_data_obj = None
        self.historical_data_df = None
        self.data_end_datetime = None
        self.data_start_datetime = None
        self.last_close_price = None
        self.ti_1_value = None
        self.ti_2_value = None
        self.ti_3_value = None
        self.ti_4_value = None
        self.ti_5_value = None

        self.ti_1_sl_value = None
        self.ti_2_sl_value = None
        self.ti_3_sl_value = None

        self.ti_1_signal = None
        self.ti_2_signal = None
        self.ti_3_signal = None
        self.ti_4_signal = None
        self.ti_5_signal = None

        self.ti_1_enabled = None
        self.ti_2_enabled = None
        self.ti_3_enabled = None
        self.ti_4_enabled = None
        self.ti_5_enabled = None

        self.ti_1_weight = None
        self.ti_2_weight = None
        self.ti_3_weight = None
        self.ti_4_weight = None
        self.ti_5_weight = None
        self.level_weight = None

        self.rank = None

        self.level_signal = None
        self.level_value = None

        self.instruments_fetched = False
        print(__class__, __name__, self.instru_token, "object created")

    def read_instruments_df(self):
        if self.instruments_fetched:
            instru_df = pd.read_csv("NFO_instruments.csv")
        else:
            instru = self.kite_obj.instruments(exchange="NFO")
            instru_df = pd.DataFrame(instru)
            instru_df.to_csv("NFO_instruments.csv")
            self.instruments_fetched = True
        return instru_df

    def get_instru_basic_data(self):
        nfo_instruments_df = self.read_instruments_df()
        this_instru_data = nfo_instruments_df[nfo_instruments_df["instrument_token"] == self.instru_token].to_dict("records")[0]
        self.instru_name = this_instru_data["name"]
        self.trading_symbol = this_instru_data["tradingsymbol"]
        self.expiry_date = this_instru_data["expiry"]
        self.strike = this_instru_data["strike"]
        self.lot_size = this_instru_data["lot_size"]
        self.instru_type = this_instru_data["instrument_type"]

    def create_hist_data_obj(self):
        self.hist_data_obj = HistoricalData(self.kite_obj, self.instru_token, self.candle_interval)

    def set_hist_data(self):
        self.hist_data_obj = HistoricalData(self.kite_obj, self.instru_token, self.candle_interval)
        self.data_end_datetime = dt.datetime.now().date()
        self.data_start_datetime = self.data_end_datetime - dt.timedelta(days=90)
        data_w_lastcandle_changing = self.hist_data_obj.fetch(self.data_start_datetime, self.data_end_datetime)
        self.historical_data_df = data_w_lastcandle_changing.iloc[:-1].copy()
        # print(data_w_lastcandle_changing.tail(5))
        # print(self.historical_data_df.tail(5))

    def set_last_close_price(self):
            self.last_close_price = self.historical_data_df.iloc[-1]["close"]

    def set_indicator_enable(self):
        enable_indi_list = config["ti_enabled_list"]
        self.ti_1_enabled = True if 1 in enable_indi_list else False
        self.ti_2_enabled = True if 2 in enable_indi_list else False
        self.ti_3_enabled = True if 3 in enable_indi_list else False
        self.ti_4_enabled = True if 4 in enable_indi_list else False
        self.ti_5_enabled = True if 5 in enable_indi_list else False

    def set_indicator_value_signal(self):
        if self.ti_1_enabled:
            self.ti_1_value, self.ti_1_signal = indicators.simple_moving_average(self.historical_data_df, config["ti_1_config"])
        else:
            pass
        if self.ti_2_enabled:
            self.ti_2_value, self.ti_2_signal = indicators.not_anchored_vwap(self.historical_data_df)
        else:
            pass
        if self.ti_3_enabled:
            self.ti_3_value, self.ti_3_signal = indicators.supertrend(self.historical_data_df, config["ti_3_config"][0], config["ti_3_config"][1])
        else:
            pass
        if self.ti_4_enabled:
            self.ti_4_value, self.ti_4_signal = indicators.macd(self.historical_data_df, config["ti_4_config"][0], config["ti_4_config"][1], config["ti_4_config"][2])
        else:
            pass
        if self.ti_5_enabled:
            self.ti_5_value, self.ti_5_signal = indicators.stochastic(self.historical_data_df, config["ti_5_config"])
        else:
            pass

        self.ti_1_sl_value, dummy = indicators.simple_moving_average(self.historical_data_df, config["ti_1_sl_config"])
        self.ti_2_sl_value, dummy = indicators.simple_moving_average(self.historical_data_df, config["ti_2_sl_config"])
        self.ti_3_sl_value, dummy = indicators.simple_moving_average(self.historical_data_df, config["ti_3_sl_config"])

    def set_level_signal(self):
        if self.instru_name == "NIFTY":
            if config["nifty_level_up"] is not None:
                if self.last_close_price > config["nifty_level_up"]:
                    self.level_signal = 1
                    self.level_value = config["nifty_level_up"]
                else:
                    self.level_signal = 0
            else:
                self.level_signal = 0

            if config["nifty_level_down"] is not None:
                if self.last_close_price < config["nifty_level_down"]:
                    self.level_signal = 1
                    self.level_value = config["nifty_level_down"]
                else:
                    self.level_signal = 0
            else:
                self.level_signal = 0
        elif self.instru_name == "BANKNIFTY":
            if config["banknifty_level_up"] is not None:
                if self.last_close_price > config["banknifty_level_up"]:
                    self.level_signal = 1
                    self.level_value = config["banknifty_level_up"]
                else:
                    self.level_signal = 0
            else:
                self.level_signal = 0

            if config["banknifty_level_down"] is not None:
                if self.last_close_price < config["banknifty_level_down"]:
                    self.level_signal = 1
                    self.level_value = config["banknifty_level_down"]
                else:
                    self.level_signal = 0
            else:
                self.level_signal = 0
        else:
            self.level_signal = 0

    def set_rank(self):
        self.ti_1_weight = config["ti_1_rank"] if (self.ti_1_enabled and self.ti_1_signal == 1) else 0
        self.ti_2_weight = config["ti_2_rank"] if (self.ti_2_enabled and self.ti_2_signal == 1) else 0
        self.ti_3_weight = config["ti_3_rank"] if (self.ti_3_enabled and self.ti_3_signal == 1) else 0
        self.ti_4_weight = config["ti_4_rank"] if (self.ti_4_enabled and self.ti_4_signal == 1) else 0
        self.ti_5_weight = config["ti_5_rank"] if (self.ti_5_enabled and self.ti_5_signal == 1) else 0
        self.level_weight = self.level_signal * config["future_levels_rank"] if config["future_levels_enabled"] else 0

        self.rank = self.ti_1_weight + self.ti_2_weight + self.ti_3_weight + self.ti_4_weight + self.ti_5_weight + self.level_weight

    def initialise(self):
        self.get_instru_basic_data()
        self.create_hist_data_obj()
        self.set_hist_data()
        self.set_last_close_price()
        self.set_indicator_enable()
        self.set_indicator_value_signal()
        self.set_level_signal()
        self.set_rank()
        print(self.trading_symbol)
        # time.sleep(5)

    def update(self):
        self.set_hist_data()
        self.set_last_close_price()
        self.set_indicator_value_signal()
        self.set_level_signal()
        self.set_rank()

if __name__ == "__main__":
    from utilsall.kite_make_connection import Kite
    kite = Kite()
    kite.establish_connection()

    bfd = FnoDataProcessor(kite.object, 8960770, "5minute")
    bfd.get_instru_basic_data()
    bfd.set_hist_data()
    del dt
    print(bfd.instru_token)
    print(bfd.trading_symbol)
    print(bfd.expiry_date)
    print(bfd.strike)
    print(bfd.lot_size)
    # print(bfd.historical_data_df)
    print(bfd.historical_data_df["close"].values)
    print(bfd.historical_data_df["close"].values[-1])

    from utilsall.indicators import Indicator
    indi = Indicator()
    vwap = not_anchored_vwap(bfd.historical_data_df)
    print(vwap)

    supertrend = supertrend(bfd.historical_data_df, 14, 3)
    print(supertrend)






