from utilsall.historicaldata import HistoricalData
from utilsall.kite_make_connection import Kite
import datetime as dt
import os
from pprint import pprint

master_filepath = "/Users/anirudh/Documents/"

kite_obj = Kite(cred_filepath=master_filepath+"api_credentials.json", token_filepath=master_filepath+"access_token.json")
kite_obj.establish_connection()
orders_df = kite_obj.object.orders()
pprint(orders_df)