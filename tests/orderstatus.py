from utilsall.orders import Orders
from utilsall.kite_make_connection import Kite

kite_obj = Kite()
kite_obj.establish_connection()

ord = Orders(kite_obj.object,False)

oid = "230915602663514"
order_status = ord.get_order_status(oid)
print(order_status)

if order_status == "COMPLETE":
    print("matched")
