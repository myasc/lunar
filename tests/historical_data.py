from utilsall.historicaldata import HistoricalData
from utilsall.kite_make_connection import Kite
import datetime as dt

kite_obj = Kite()
kite_obj.establish_connection()

instru_token = 8972290
start_dt = dt.datetime(2023, 8, 16)
end_dt = dt.datetime(2023, 8, 18)
hd = HistoricalData(kite_obj.object, instru_token, "5minute")
df = hd.fetch(start_dt, end_dt)
print(df)