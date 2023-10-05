import time

import pandas as pd
pd.set_option("display.max_columns", 50)
pd.set_option('display.width', 200)
from utilsall.orders import Orders
from utilsall.kite_make_connection import Kite
from pprint import pprint
import logging

logger = logging.getLogger(__name__)

master_filepath = "/Users/anirudh/Documents/"

kite_obj = Kite(cred_filepath=master_filepath+"api_credentials.json", token_filepath=master_filepath+"access_token.json")
kite_obj.establish_connection()

ord = Orders(kite_obj.object, False, logger)
orders_df = pd.DataFrame(kite_obj.object.orders())
print(orders_df)

positions_df = pd.DataFrame(kite_obj.object.positions()["day"])
print(positions_df)

ord.cancel_all_tagged_open_orders()
ord.marketsell_tagged_open_orders()