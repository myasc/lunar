import datetime as dt

import pandas as pd
pd.set_option("display.max_columns", 50)
from utilsall.historicaldata import HistoricalData
from utilsall import indicators
from config1 import config

class FnoDataProcessor:
    def __init__(self, kite_obj, instru_token, candle_interval, last_fut_close_price=None, logger=None):
        self.kite_obj = kite_obj
        self.logger = logger
        self.instru_token = instru_token
        self.candle_interval = candle_interval
        self.instru_name = None
        self.trading_symbol = None
        self.expiry_date = None
        self.strike = None
        self.lot_size = None
        self.tick_size = None
        self.instru_type = None

        self.hist_data_obj = None
        self.historical_data_df = None
        self.data_end_datetime = None
        self.data_start_datetime = None
        self.last_close_price = None
        self.last_fut_close_price = last_fut_close_price
        self.ti_1_value = None
        self.ti_2_value = None
        self.ti_3_value = None
        self.ti_4_value = None
        self.ti_5_value = None

        self.ti_1_tp_value = None
        self.ti_2_tp_value = None
        self.ti_3_tp_value = None

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
        self.sl_indi_sell_signal = None

        self.instruments_fetched = False
        # self.last_timestamp_processed = None
        self.latest_timestamp = None

        self.fno_dataproc_initialised = False

    def read_instruments_df(self):
        """fetching instruments and info from api"""
        if self.instruments_fetched:
            instru_df = pd.read_csv("NFO_instruments.csv")
        else:
            instru = self.kite_obj.instruments(exchange="NFO")
            instru_df = pd.DataFrame(instru)
            instru_df.to_csv("NFO_instruments.csv")
            self.instruments_fetched = True
        if self.logger is not None:
            self.logger.info(f"{__class__.__name__}: fetched instruments df from kite")
        return instru_df

    def get_instru_basic_data(self):
        nfo_instruments_df = self.read_instruments_df()
        if not nfo_instruments_df.empty:
            this_instru_df = nfo_instruments_df[nfo_instruments_df["instrument_token"] == self.instru_token]
            if not this_instru_df.empty:
                this_instru_data = this_instru_df.to_dict("records")[0]
                self.instru_name = this_instru_data["name"]
                self.trading_symbol = this_instru_data["tradingsymbol"]
                self.expiry_date = this_instru_data["expiry"]
                self.strike = this_instru_data["strike"]
                self.lot_size = this_instru_data["lot_size"]
                self.tick_size = this_instru_data["tick_size"]
                self.instru_type = this_instru_data["instrument_type"]
                if self.logger is not None:
                    self.logger.info(f"{__class__.__name__}: instrument data fetched name:{self.instru_name}, symbol:{self.trading_symbol} expiry:{self.expiry_date} strike:{self.strike} lot:{self.lot_size} tick:{self.tick_size} type:{self.instru_type}")
            else:
                self.logger.info(f"{__class__.__name__}: none fetched instruments df from kite for token {self.instru_token}")
                pass
        else:
            self.logger.info(f"{__class__.__name__}: none fetched instruments df from kite empty")
            pass


    def create_hist_data_obj(self):
        self.hist_data_obj = HistoricalData(self.kite_obj, self.instru_token, self.candle_interval)
        if self.logger is not None:
            self.logger.info(f"{__class__.__name__}: historical data object created")


    def set_hist_data(self):
        self.data_end_datetime = dt.datetime.now().date()
        self.data_start_datetime = self.data_end_datetime - dt.timedelta(days=90)
        data_w_last_candle_changing = self.hist_data_obj.fetch(self.data_start_datetime, self.data_end_datetime)
        # print(data_w_last_candle_changing.tail(2))
        if not data_w_last_candle_changing.empty:
            self.historical_data_df = data_w_last_candle_changing.iloc[:-1].copy()
            if self.logger is not None:
                self.logger.info(f"{__class__.__name__}: historical data fetched size {self.historical_data_df.shape}")
            self.latest_timestamp = pd.to_datetime(self.historical_data_df.index[-1])
            if self.logger is not None:
                self.logger.info(f"{__class__.__name__}: latest timestamp set to {self.latest_timestamp}")
        else:
            self.historical_data_df = pd.DataFrame()
            if self.logger is not None:
                self.logger.info(f"{__class__.__name__}: none historical data emtpy dataframe")


    def set_last_close_price(self):
        if not self.historical_data_df.empty:
            self.last_close_price = self.historical_data_df.iloc[-1]["close"]
        self.last_fut_close_price = self.last_fut_close_price if self.last_fut_close_price is not None else self.last_close_price
        if self.logger is not None:
            self.logger.info(f"{__class__.__name__}: last close price set lcp:{self.last_close_price} lastfuturecloseprice{self.last_fut_close_price}")

    def set_indicator_enable(self):
        enable_indi_list = config["ti_enabled_list"]
        self.ti_1_enabled = True if 1 in enable_indi_list else False
        self.ti_2_enabled = True if 2 in enable_indi_list else False
        self.ti_3_enabled = True if 3 in enable_indi_list else False
        self.ti_4_enabled = True if 4 in enable_indi_list else False
        self.ti_5_enabled = True if 5 in enable_indi_list else False
        if self.logger is not None:
            self.logger.info(f"{__class__.__name__}: enabled indicators 1:{self.ti_1_enabled} 2:{self.ti_2_enabled} 3:{self.ti_3_enabled} 4:{self.ti_4_enabled} 5:{self.ti_5_enabled}")

    def get_indicator_value_signal(self):
        if self.ti_1_enabled:
            self.ti_1_value, self.ti_1_signal = indicators.simple_moving_average(self.historical_data_df, config["ti_1_config"])
        else:
            pass
        if self.logger is not None:
            self.logger.info(f"{__class__.__name__}: indicator 1 set value:{self.ti_1_value} signal:{self.ti_1_signal} config:{config['ti_1_config']}")
        if self.ti_2_enabled:
            self.ti_2_value, self.ti_2_signal = indicators.not_anchored_vwap(self.historical_data_df)
        else:
            pass
        if self.logger is not None:
            self.logger.info(f"{__class__.__name__}: indicator 2 set value:{self.ti_2_value} signal:{self.ti_2_signal} config:{config['ti_2_config']}")
        if self.ti_3_enabled:
            self.ti_3_value, self.ti_3_signal = indicators.supertrend(self.historical_data_df, config["ti_3_config"][0], config["ti_3_config"][1])
        else:
            pass
        if self.logger is not None:
            self.logger.info(f"{__class__.__name__}: indicator 3 set value:{self.ti_3_value} signal:{self.ti_3_signal} config:{config['ti_3_config']}")
        if self.ti_4_enabled:
            self.ti_4_value, self.ti_4_signal = indicators.macd(self.historical_data_df, config["ti_4_config"][0], config["ti_4_config"][1], config["ti_4_config"][2])
        else:
            pass
        if self.logger is not None:
            self.logger.info(f"{__class__.__name__}: indicator 4 set value:{self.ti_4_value} signal:{self.ti_4_signal} config:{config['ti_4_config']}")
        if self.ti_5_enabled:
            self.ti_5_value, self.ti_5_signal = indicators.stochastic(self.historical_data_df, config["ti_5_config"])
        else:
            pass
        if self.logger is not None:
            if self.logger is not None:
                self.logger.info(f"{__class__.__name__}: indicator 5 set value:{self.ti_5_value} signal:{self.ti_5_signal} config:{config['ti_5_config']}")

        self.ti_1_tp_value, dummy = indicators.simple_moving_average(self.historical_data_df, config["ti_1_tp_config"])
        if self.logger is not None:
            self.logger.info(f"{__class__.__name__}: indicator tp 1 set value:{self.ti_1_tp_value} signal:{dummy} config:{config['ti_1_tp_config']}")
        self.ti_2_tp_value, dummy = indicators.simple_moving_average(self.historical_data_df, config["ti_2_tp_config"])
        if self.logger is not None:
            self.logger.info(f"{__class__.__name__}: indicator tp 2 set value:{self.ti_2_tp_value} signal:{dummy} config:{config['ti_2_tp_config']}")
        self.ti_3_tp_value, dummy = indicators.simple_moving_average(self.historical_data_df, config["ti_3_tp_config"])
        if self.logger is not None:
            self.logger.info(f"{__class__.__name__}: indicator tp 3 set value:{self.ti_3_tp_value} signal:{dummy} config:{config['ti_3_tp_config']}")


    def set_level_signal(self):
        if self.instru_name == "NIFTY":
            if (self.last_fut_close_price > config["nifty_level_up"]) or (self.last_fut_close_price < config["nifty_level_down"]):
                self.level_signal = 1
                self.level_value = f"{config['nifty_level_up'], config['nifty_level_down']}"
                if self.logger is not None:
                    self.logger.info(f"{__class__.__name__}:  {self.instru_name} level set value:{self.level_value} signal:{self.level_signal}")
            else:
                self.level_signal = 0
                if self.logger is not None:
                    self.logger.info(f"{__class__.__name__}: {self.instru_name} level set value:{self.level_value} signal:{self.level_signal}")
        elif self.instru_name == "BANKNIFTY":
            if (self.last_fut_close_price > config["banknifty_level_up"]) or (self.last_fut_close_price < config["banknifty_level_down"]):
                self.level_signal = 1
                self.level_value = f"{config['banknifty_level_up'], config['banknifty_level_down']}"
                if self.logger is not None:
                    self.logger.info(f"{__class__.__name__}: {self.instru_name} level set value:{self.level_value} signal:{self.level_signal}")
            else:
                self.level_signal = 0
                if self.logger is not None:
                    self.logger.info(f"{__class__.__name__}: {self.instru_name} level set value:{self.level_value} signal:{self.level_signal}")
        else:
            self.level_signal = 0
            if self.logger is not None:
                self.logger.info(f"{__class__.__name__}: {self.instru_name} level set value:{self.level_value} signal:{self.level_signal}")

    def set_sl_indi_sell_signal(self):
        self.sl_indi_sell_signal = True if self.ti_3_signal == -1 else False
        if self.logger is not None:
            self.logger.info(f"{__class__.__name__}: {self.instru_name} {self.trading_symbol} sl indicator sell signal set as {self.sl_indi_sell_signal}")

    def set_rank(self):
        self.ti_1_weight = config["ti_1_rank"] if (self.ti_1_enabled and self.ti_1_signal == 1) else 0
        self.ti_2_weight = config["ti_2_rank"] if (self.ti_2_enabled and self.ti_2_signal == 1) else 0
        self.ti_3_weight = config["ti_3_rank"] if (self.ti_3_enabled and self.ti_3_signal == 1) else 0
        self.ti_4_weight = config["ti_4_rank"] if (self.ti_4_enabled and self.ti_4_signal == 1) else 0
        self.ti_5_weight = config["ti_5_rank"] if (self.ti_5_enabled and self.ti_5_signal == 1) else 0
        self.level_weight = self.level_signal * config["future_levels_rank"] if config["future_levels_enabled"] else 0

        if self.logger is not None:
            self.logger.info(f"{__class__.__name__}: weights for rank set as 1:{self.ti_1_weight} 2:{self.ti_2_weight} 3:{self.ti_3_weight} 4:{self.ti_4_weight} 5:{self.ti_5_weight} level:{self.level_weight}")
        self.rank = self.ti_1_weight + self.ti_2_weight + self.ti_3_weight + self.ti_4_weight + self.ti_5_weight + self.level_weight
        if self.logger is not None:
            self.logger.info(f"{__class__.__name__}: rank set as {self.rank}")

    def initialise(self):
        self.get_instru_basic_data()
        self.create_hist_data_obj()
        self.set_indicator_enable()
        self.fno_dataproc_initialised = True
        if self.logger is not None:
            self.logger.info(f"{__class__.__name__}: instruToken: {self.instru_token}, instruSymbol: {self.trading_symbol}, object initialised")

    def update(self):
        if not self.fno_dataproc_initialised:
            self.initialise()
        else:
            self.set_hist_data()
            self.set_last_close_price()
            self.get_indicator_value_signal()
            self.set_level_signal()
            self.set_sl_indi_sell_signal()
            self.set_rank()
            if self.logger is not None:
                self.logger.info(f"{__class__.__name__}: instruToken: {self.instru_token}, instruSymbol: {self.trading_symbol}, object updated")


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

    # from utils all.indicators import Indicator
    # indi = Indicator()
    # vwap = not_anchored_vwap(bfd.historical_data_df)
    # print(vwap)
    #
    # super trend = super trend(bfd.historical_data_df, 14, 3)
    # print(super trend)






