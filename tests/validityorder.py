from utilsall.orders import Orders
from utilsall.kite_make_connection import Kite

kite_obj = Kite()
kite_obj.establish_connection()

instru_token = 8963842

ord = Orders(kite_obj.object,False)
trading_symbol = "NIFTY2390719400CE"
quantity = 50
limit_price = 151
valid_mins =  1
remark = "test validity order"
ord.place_validity_limit1_buy_nfo(trading_symbol, quantity, limit_price, valid_mins, remark)