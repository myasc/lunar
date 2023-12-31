import pandas as pd

from utilsall.utils import add_row_to_csv
from utilsall.misc import reach_project_dir
import datetime as dt
import os

class Orders:
    def __init__(self, kite_connection_obj, testing, logger):
        self.kite_obj = kite_connection_obj
        self.csv_filepath = None
        self.testing = testing
        self.logger = logger
        self.initialise_csv_logs()
        self.tag_name = "lunar"

    def initialise_csv_logs(self):
        date_str = str(dt.datetime.now().date()).replace("-", "")
        pwd = os.getcwd()
        reach_project_dir()
        file = f"csv_files/orders_{date_str}.csv"
        self.csv_filepath = file
        add_row_to_csv(row=["type", "side", "qty", "symbol", "price", "oid","remark"],
                       file_path=self.csv_filepath,
                       print_=True)
        self.logger.info(f"{__class__.__name__}: csv log initialised")
        os.chdir(pwd)

    def calculate_transaction_charges(self, buy_price, sell_price, quantity, asset_type):
        """return transaction charges after trade exit for zerodha"""
        buy_value = buy_price * quantity
        sell_value = sell_price * quantity
        if asset_type == 'FUT':
            brokerage_buy = 20 if (buy_value * 0.0003) > 20 else (buy_value * 0.0003)
            brokerage_sell = 20 if (sell_value * 0.0003) > 20 else (sell_value * 0.0003)
            stt = sell_value * 0.0001
            transaction_charges = (buy_value + sell_value) * 0.00002
            gst = (brokerage_buy + brokerage_sell + transaction_charges) * 0.18
            sebi_charges = (buy_value + sell_value) * 0.000001
            stamp_charges = buy_value * 0.00002
            total = brokerage_buy + brokerage_sell + stt + transaction_charges + gst + sebi_charges + stamp_charges
            return total
        elif asset_type in ['OPT', 'PE', 'CE']:
            brokerage_buy = 20
            brokerage_sell = 20
            stt = sell_value * 0.0005
            transaction_charges = (buy_value + sell_value) * 0.00053
            gst = (brokerage_buy + brokerage_sell + transaction_charges) * 0.18
            sebi_charges = (buy_value + sell_value) * 0.000001
            stamp_charges = buy_value * 0.00003
            total = brokerage_buy + brokerage_sell + stt + transaction_charges + gst + sebi_charges + stamp_charges
            return total

    def place_market_buy_nfo(self, trading_symbol, quantity, remark="None"):
        if not self.testing:
            response = self.kite_obj.place_order(tradingsymbol=trading_symbol,
                                      exchange=self.kite_obj.EXCHANGE_NFO,
                                      transaction_type=self.kite_obj.TRANSACTION_TYPE_BUY,
                                      quantity=quantity,
                                      order_type=self.kite_obj.ORDER_TYPE_MARKET,
                                      product=self.kite_obj.PRODUCT_NRML,
                                      variety=self.kite_obj.VARIETY_REGULAR,
                                             tag=self.tag_name)
            self.logger.info(f"{__class__.__name__}: market buy order sent {trading_symbol} {quantity} {remark} {response}")
            add_row_to_csv(row=["market", "buy", quantity, trading_symbol, " ",response, remark],
                           file_path=self.csv_filepath,
                           print_=True)
            return response
        else:
            response = {"data": {"order_id": "test_oid_123"}}
            print(f"test: {trading_symbol} "
                  f"{self.kite_obj.EXCHANGE_NFO} "
                  f"{self.kite_obj.TRANSACTION_TYPE_BUY} "
                  f"{quantity} "
                  f"{self.kite_obj.ORDER_TYPE_MARKET}"
                  f"{self.kite_obj.PRODUCT_NRML}"
                  f"{self.kite_obj.VARIETY_REGULAR}")
            self.logger.info(f"{__class__.__name__}: test market buy order sent {trading_symbol} {quantity} {remark} {response}")
            add_row_to_csv(row=["market", "buy", quantity, trading_symbol, " ",response, "testing"],
                           file_path=self.csv_filepath,
                           print_=True)
            return response
    def place_market_sell_nfo(self, trading_symbol, quantity, remark="None"):
        if not self.testing:
            response = self.kite_obj.place_order(tradingsymbol=trading_symbol,
                                      exchange=self.kite_obj.EXCHANGE_NFO,
                                      transaction_type=self.kite_obj.TRANSACTION_TYPE_SELL,
                                      quantity=quantity,
                                      order_type=self.kite_obj.ORDER_TYPE_MARKET,
                                      product=self.kite_obj.PRODUCT_NRML,
                                      variety=self.kite_obj.VARIETY_REGULAR,
                                             tag=self.tag_name)
            self.logger.info(f"{__class__.__name__}: market sell order sent {trading_symbol} {quantity} {remark} {response}")
            add_row_to_csv(row=["market", "sell", quantity, trading_symbol, " ",response, remark],
                           file_path=self.csv_filepath,
                           print_=True)
            return response
        else:
            response = {"data": {"order_id": "test_oid_123"}}
            print(f"test: {trading_symbol} "
                  f"{self.kite_obj.EXCHANGE_NFO} "
                  f"{self.kite_obj.TRANSACTION_TYPE_SELL} "
                  f"{quantity} "
                  f"{self.kite_obj.ORDER_TYPE_MARKET}"
                  f"{self.kite_obj.PRODUCT_NRML}"
                  f"{self.kite_obj.VARIETY_REGULAR}")
            self.logger.info(f"{__class__.__name__}: test market sell order sent {trading_symbol} {quantity} {remark} {response}")
            add_row_to_csv(row=["market", "sell", quantity, trading_symbol, " ",response, "testing"],
                           file_path=self.csv_filepath,
                           print_=True)
            return response

    def modify_qty_from_orderid(self, orderid, quantity, remark="None"):
        if not self.testing:
            response = self.kite_obj.place_order(order_id = orderid,
                                                 quantity=quantity,
                                                 variety=self.kite_obj.VARIETY_REGULAR)
            self.logger.info(f"{__class__.__name__}: modify order qty sent {orderid} {quantity} {remark} {response}")
            add_row_to_csv(row=["modify", "modify", quantity, " ", " ",response, remark],
                           file_path=self.csv_filepath,
                           print_=True)
            return response


    def place_sl_market_sell_nfo(self, trading_symbol, quantity, limit_price, remark="None"):
        if not self.testing:
            try:
                response = self.kite_obj.place_order(price=limit_price,
                                          trigger_price=limit_price,
                                          quantity=quantity,
                                          tradingsymbol=trading_symbol,
                                          exchange=self.kite_obj.EXCHANGE_NFO,
                                          transaction_type=self.kite_obj.TRANSACTION_TYPE_SELL,
                                          order_type=self.kite_obj.ORDER_TYPE_SL,
                                          product=self.kite_obj.PRODUCT_NRML,
                                          variety=self.kite_obj.VARIETY_REGULAR,
                                                 tag=self.tag_name)
            except:
                raise Exception
            self.logger.info(f"{__class__.__name__}: sl order sent {trading_symbol} {quantity} {limit_price} {remark} {response}")
            add_row_to_csv(row=["limit", "sell", quantity, trading_symbol, limit_price,response, remark],
                           file_path=self.csv_filepath,
                           print_=True)
            return response
        else:
            response = {"data": {"order_id": "test_oid_123"}}
            self.logger.info(f"{__class__.__name__}: test sl order sent {trading_symbol} {quantity} {limit_price} {remark} {response}")
            add_row_to_csv(row=["limit", "sell", quantity, trading_symbol, limit_price,response, "testing"],
                           file_path=self.csv_filepath,
                           print_=True)
            return response

    def place_limit_buy_nfo(self, trading_symbol, quantity, limit_price, remark="None"):
        if not self.testing:
            response = self.kite_obj.place_order(price=limit_price,
                                      trigger_price=limit_price,
                                      quantity=quantity,
                                      tradingsymbol=trading_symbol,
                                      exchange=self.kite_obj.EXCHANGE_NFO,
                                      transaction_type=self.kite_obj.TRANSACTION_TYPE_BUY,
                                      order_type=self.kite_obj.ORDER_TYPE_LIMIT,
                                      product=self.kite_obj.PRODUCT_NRML,
                                      variety=self.kite_obj.VARIETY_REGULAR,
                                             tag=self.tag_name)
            self.logger.info(f"{__class__.__name__}: limit buy order sent {trading_symbol} {quantity} {limit_price} {remark} {response}")
            add_row_to_csv(row=["limit", "buy", quantity, trading_symbol, limit_price,response, remark],
                           file_path=self.csv_filepath,
                           print_=True)
            return response
        else:
            response = {"data": {"order_id": "test_oid_123"}}
            self.logger.info(f"{__class__.__name__}: test limit buy order sent {trading_symbol} {quantity} {limit_price} {remark} {response}")
            add_row_to_csv(row=["limit", "buy", quantity, trading_symbol, limit_price,response, "testing"],
                           file_path=self.csv_filepath,
                           print_=True)
            return response
    def place_limit_sell_nfo(self, trading_symbol, quantity, limit_price, remark="None"):
        if not self.testing:
            response = self.kite_obj.place_order(price=limit_price,
                                      trigger_price=limit_price,
                                      quantity=quantity,
                                      tradingsymbol=trading_symbol,
                                      exchange=self.kite_obj.EXCHANGE_NFO,
                                      transaction_type=self.kite_obj.TRANSACTION_TYPE_SELL,
                                      order_type=self.kite_obj.ORDER_TYPE_LIMIT,
                                      product=self.kite_obj.PRODUCT_NRML,
                                      variety=self.kite_obj.VARIETY_REGULAR,
                                             tag=self.tag_name)
            self.logger.info(f"{__class__.__name__}: limit sell order sent {trading_symbol} {quantity} {limit_price} {remark} {response}")
            add_row_to_csv(row=["limit", "sell", quantity, trading_symbol, limit_price,response, remark],
                           file_path=self.csv_filepath,
                           print_=True)
            return response
        else:
            response = {"data": {"order_id": "test_oid_123"}}
            self.logger.info(f"{__class__.__name__}: test limit sell order sent {trading_symbol} {quantity} {limit_price} {remark} {response}")
            add_row_to_csv(row=["limit", "sell", quantity, trading_symbol, limit_price,response, "testing"],
                           file_path=self.csv_filepath,
                           print_=True)
            return response

    def place_validity_limit_buy_nfo(self, trading_symbol, quantity, limit_price, valid_mins, remark="None"):
        if not self.testing:
            response = self.kite_obj.place_order(price=limit_price,
                                      trigger_price=limit_price,
                                      quantity=quantity,
                                      tradingsymbol=trading_symbol,
                                      exchange=self.kite_obj.EXCHANGE_NFO,
                                      transaction_type=self.kite_obj.TRANSACTION_TYPE_BUY,
                                      order_type=self.kite_obj.ORDER_TYPE_LIMIT,
                                      product=self.kite_obj.PRODUCT_NRML,
                                      variety=self.kite_obj.VARIETY_REGULAR,
                                      validity=self.kite_obj.VALIDITY_TTL,
                                      validity_ttl=valid_mins,
                                             tag=self.tag_name)
            self.logger.info(f"{__class__.__name__}: limit validity buy order sent {trading_symbol} {quantity} {limit_price} {valid_mins} {remark} {response}")
            add_row_to_csv(row=["limit", "buy", quantity, trading_symbol, limit_price,response, remark],
                           file_path=self.csv_filepath,
                           print_=True)
            return response
        else:
            response = {"data": {"order_id": "test_oid_123"}}
            self.logger.info(f"{__class__.__name__}: test limit validity buy order sent {trading_symbol} {quantity} {limit_price} {valid_mins} {remark} {response}")
            add_row_to_csv(row=["limit", "buy", quantity, trading_symbol, limit_price,response, "testing"],
                           file_path=self.csv_filepath,
                           print_=True)
            return response

    def place_raw(self, price, trigger_price, quantity, trading_symbol, exchange, transaction_type, order_type, product,
                  variety):
        response = self.kite_obj.place_order(price=price,
                                              trigger_price=trigger_price,
                                              quantity=quantity,
                                              tradingsymbol=trading_symbol,
                                              exchange=exchange,
                                              transaction_type=transaction_type,
                                              order_type=order_type,
                                              product=product,
                                              variety=variety,
                                             tag=self.tag_name)
        self.logger.info(f"{__class__.__name__}: raw order sent {price} {trigger_price} {quantity} {trading_symbol} {exchange} {transaction_type} {order_type} {product} {variety}")
        add_row_to_csv(row=[order_type, transaction_type, quantity, trading_symbol, trigger_price,response, "raw_order"],
                       file_path=self.csv_filepath,
                       print_=True)
        return response

    def get_orders(self):
        orders_df = pd.DataFrame(self.kite_obj.orders())
        if not orders_df.empty:
            this_tag_orders = orders_df[orders_df["tag"] == self.tag_name].copy()
            self.logger.info(f"{__class__.__name__}: fetched existing orders for tag {self.tag_name}")
            return this_tag_orders
        else:
            self.logger.info(f"{__class__.__name__}: none fetched existing orders for tag {self.tag_name}")
            return orders_df

    def get_order_status(self, oid):
        if oid == "":
            self.logger.info(f"{__class__.__name__}: none order status fetched oid:{oid}")
            return ""
        else:
            orders_df = self.get_orders()
            if not orders_df.empty:
                this_order = orders_df[orders_df["order_id"] == oid].to_dict("records")[0]
                self.logger.info(f"{__class__.__name__}: order status fetched oid:{oid} {this_order['status']}")
                return this_order["status"]
            else:
                self.logger.info(f"{__class__.__name__}: none order status fetched oid:{oid}, dataframe emtpy")
                return None

    def cancel_all_tagged_open_orders(self):
        orders_df = pd.DataFrame(self.kite_obj.orders())
        if not orders_df.empty:
            tag_mask = orders_df["tag"] == self.tag_name
            open_mask = orders_df["status"] == "OPEN"
            this_tag_open_orders = orders_df[tag_mask & open_mask].copy()
            if not this_tag_open_orders.empty:
                for oid in this_tag_open_orders["order_id"].tolist():
                    self.kite_obj.cancel_order(variety=self.kite_obj.VARIETY_REGULAR, order_id=oid)
                    self.logger.info(f"{__class__.__name__}: cancelled order oid{oid}")
                self.logger.info(f"{__class__.__name__}: cancelled all tagged open orders")
            else:
                self.logger.info(f"{__class__.__name__}: none tagged open orders for cancel")
                pass
        else:
            self.logger.info(f"{__class__.__name__}: none orders available for cancel")
            pass

    def marketsell_tagged_open_orders(self):
        """
        this fucntion will square off positions irrespective of tag
        :return:
        """
        positions_df = pd.DataFrame(self.kite_obj.positions()["day"])
        if not positions_df.empty:
            # tag_mask = positions_df["tag"] == self.tag_name # tag doesn't work here
            open_mask = positions_df["quantity"] > 0
            open_positions = positions_df[open_mask].copy()
            if not open_positions.empty:
                for position in open_positions.to_dict("records"):
                    resp = self.place_market_sell_nfo(position["tradingsymbol"], position["quantity"], "squareoffopen")
                self.logger.info(f"{__class__.__name__}: marketsell tagged open orders complete")
            else:
                self.logger.info(f"{__class__.__name__}: none tagged open orders for marketsell")
        else:
            self.logger.info(f"{__class__.__name__}: none orders available for marketsell")
            pass

if __name__ == "__main__":
    orders_obj = Orders("dummy")
    charges = orders_obj.calculate_transaction_charges(47, 72, 50, "OPT")
    print(charges)
