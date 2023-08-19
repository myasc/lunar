from utilsall import indicators
from utilsall.historicaldata import HistoricalData
from utilsall.kite_make_connection import Kite
import datetime as dt
import pandas as pd
pd.set_option("display.max_columns", 50)

kite_obj = Kite()
kite_obj.establish_connection()

instru_token = 8963842
start_dt = dt.datetime(2023, 8, 16)
end_dt = dt.datetime(2023, 8, 19)
hd = HistoricalData(kite_obj.object, instru_token, "5minute")
df = hd.fetch(start_dt, end_dt)
print(df)

indicators.supertrend(df, 14, 3)
