import time

import pandas as pd
from utilsall.kite_make_connection import Kite
from pprint import pprint

class FNOContractSelector:
    def __init__(self, kite_connection_obj, underlying, expiry, instrument, strike=None):
        self.kite_connection_obj = kite_connection_obj
        self.underlying = underlying
        self.expiry = expiry
        self.strike = strike
        self.instrument = instrument
        self.all_instruments_df = None
        self.instruments_fetched = False

    def _get_instruments(self, exchange="NFO"):
        if self.instruments_fetched:
            self.all_instruments_df = pd.read_csv(f"{exchange}_instruments.csv")
        else:
            instruments = self.kite_connection_obj.instruments(exchange)
            self.all_instruments_df = pd.DataFrame(instruments)
            self.all_instruments_df.to_csv(f"{exchange}_instruments.csv")
            self.instruments_fetched = True
        return

    def get_instrument_symbol(self):
        self._get_instruments("NFO")
        try:
            filter_1 = (self.all_instruments_df.name == self.underlying)
            filter_2 = (self.all_instruments_df.expiry == self.expiry)
            filter_3 = (self.all_instruments_df.strike == self.strike)
            filter_4 = (self.all_instruments_df.instrument_type == self.instrument)
            if self.instrument in ["CE", "PE"]:
                filtered_df = self.all_instruments_df[filter_1 & filter_2 & filter_3 & filter_4]
                return filtered_df.tradingsymbol.values[0]
            elif self.instrument == "FUT":
                filterd_df = self.all_instruments_df[filter_1 & filter_2 & filter_4]
                return filterd_df.tradingsymbol.values[0]
        except Exception as e:
            print(e)
            raise(e)
            return -1

    def get_instrument_id(self):
        filterd_dict = []
        self._get_instruments("NFO")
        try:
            filter_1 = (self.all_instruments_df.name == self.underlying)
            filter_2 = (self.all_instruments_df.expiry == self.expiry)
            filter_3 = (self.all_instruments_df.strike == self.strike)
            filter_4 = (self.all_instruments_df.instrument_type == self.instrument)
            if self.instrument in ["CE", "PE"]:
                filterd_df = self.all_instruments_df[filter_1 & filter_2 & filter_3 & filter_4]
                filterd_dict = filterd_df.to_dict("records")
            elif self.instrument == "FUT":
                filterd_df = self.all_instruments_df[filter_1 & filter_2 & filter_4]
                filterd_dict = filterd_df.to_dict("records")
            else:
                exception_str = f"Invalid instrument, not in [CE, PE, FUT]"
                raise Exception(exception_str)

            if len(filterd_dict) == 0:
                exception_str = f"None matching instrument found {{'underlying': {self.underlying}," \
                                f"'expiry': {self.expiry},'strike': {self.strike}, 'instrument': {self.instrument}}}"
                raise Exception(exception_str)
            elif len(filterd_dict) > 1:
                exception_str = f"More than 1 matching instrument found {{'underlying': {self.underlying},"\
                                f"'expiry': {self.expiry},'strike': {self.strike}, 'instrument': {self.instrument}}}"
                raise Exception(exception_str)
            else:
                return filterd_dict[0]["instrument_token"]
        except Exception as e:
            raise e

if __name__ == "__main__":
    import datetime as dt
    kite = Kite()
    kite.establish_connection()
    instruments = kite.object.instruments(exchange="NFO")
    nfo_instruments_df = pd.DataFrame(instruments)
    print(nfo_instruments_df)
    nfo_instruments_df.to_csv("nfo_kite_instru.csv")
    print(nfo_instruments_df.iloc[1].expiry)
    print(type(nfo_instruments_df.iloc[1].expiry))
    print(nfo_instruments_df.columns)
    cs = FNOContractSelector(kite.object, "NIFTY", dt.date(2023, 6, 29), "FUT", None)
    id_ = cs.get_instrument_id()
    print(id_)
