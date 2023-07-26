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

    def _get_instruments(self, exchange="NFO"):
        instruments = self.kite_connection_obj.instruments(exchange)
        self.all_instruments_df = pd.DataFrame(instruments)
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
            return -1

    def get_instrument_id(self):
        self._get_instruments("NFO")
        try:
            filter_1 = (self.all_instruments_df.name == self.underlying)
            filter_2 = (self.all_instruments_df.expiry == self.expiry)
            filter_3 = (self.all_instruments_df.strike == self.strike)
            filter_4 = (self.all_instruments_df.instrument_type == self.instrument)
            if self.instrument in ["CE", "PE"]:
                filterd_df = self.all_instruments_df[filter_1 & filter_2 & filter_3 & filter_4]
                return filterd_df.instrument_token.values[0]
            elif self.instrument == "FUT":
                filterd_df = self.all_instruments_df[filter_1 & filter_2 & filter_4]
                pprint(filterd_df.to_dict("records"))
                return filterd_df.instrument_token.values[0]
        except Exception as e:
            print(e)
            return -1

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
