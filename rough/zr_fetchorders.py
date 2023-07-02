from utilsall.kite_make_connection import Kite
import pandas as pd
from pprint import pprint

# pd.set_option("display.max_columns", 500)
pd.set_option('display.expand_frame_repr', False)

kt = Kite()
kt.establish_connection()

# from Orders import Orders
#
# ord = Orders(kt.object)
# price = 20
# ord.place_raw(price=price,
#               trigger_price=price,
#               quantity=50,
#               trading_symbol="NIFTY23JUN18750CE",
#               exchange=kt.object.EXCHANGE_NFO,
#               transaction_type=kt.object.TRANSACTION_TYPE_BUY,
#               order_type=kt.object.ORDER_TYPE_LIMIT,
#               product=kt.object.PRODUCT_NRML,
#               variety=kt.object.VARIETY_REGULAR)

order_df = (kt.object.orders())
pprint(order_df)
print(pd.DataFrame(order_df))
