import logging

from utilsall.orders import Orders
from utilsall.kite_make_connection import Kite

master_filepath = "/Users/anirudh/Documents/"

kite_obj = Kite(cred_filepath=master_filepath+"api_credentials.json", token_filepath=master_filepath+"access_token.json")
kite_obj.establish_connection()

logger = logging.getLogger(__name__)

ord = Orders(kite_obj.object,False, logger)
symbol_ = "NIFTY23O0519000PE"
quantity_ = 50
price_ = 0.05
resp = ord.place_sl_market_sell_nfo(symbol_, quantity_, price_,"global_sl")
print(resp)