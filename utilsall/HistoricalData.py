import pandas as pd
import datetime as dt

class HistoricalData:
    def __init__(self, kite_obj, instrument_id, timeframe):
        self.kite_obj = kite_obj
        self.instrument_id = instrument_id
        self.timeframe = timeframe

    def fetch(self, start_datetime, end_datetime):
        data = pd.DataFrame(self.kite_obj.historical_data(self.instrument_id,
                                                          start_datetime,
                                                          end_datetime,
                                                          self.timeframe)
                            )
        data.set_index("date", inplace=True)
        return data

    def fetch_intraday(self):
        dt_now = dt.datetime.now()
        data = pd.DataFrame(self.kite_obj.historical_data(self.instrument_id,
                                                          dt_now.replace(hour=9,
                                                                         minute=15,
                                                                         second=0,
                                                                         microsecond=0),
                                                          dt_now,
                                                          self.timeframe)
                            )
        data.set_index("date", inplace=True)
        return data

if __name__ == "__main__":
    kite = Kite()
    kite.establish_connection()
    histdata = HistoricalData(kite.object, 8960770, "5minute")
    # start_datetime = dt.date(2023, 5, 1)
    # end_datetime = dt.date(2023, 6, 10)
    end_datetime = dt.datetime.now().date()
    start_datetime = end_datetime - dt.timedelta(days=90)
    print(f"Fetching from {start_datetime} to {end_datetime}")
    data_df = histdata.fetch(start_datetime, end_datetime)
    print(data_df)