class Orders:
    def __init__(self, kite_connection_obj):
        self.kite_obj = kite_connection_obj

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

    def place_market_buy_nfo(self, trading_symbol, quantity):
        self.kite_obj.place_order(tradingsymbol=trading_symbol,
                                  exchange=self.kite_obj.EXCHANGE_NFO,
                                  transaction_type=self.kite_obj.TRANSACTION_TYPE_BUY,
                                  quantity=quantity,
                                  order_type=self.kite_obj.ORDER_TYPE_MARKET,
                                  product=self.kite_obj.PRODUCT_NRML,
                                  variety=self.kite_obj.VARIETY_REGULAR)

    def place_sl_market_sell_nfo(self, trading_symbol, quantity, limit_price):
        self.kite_obj.place_order(price=limit_price,
                                  trigger_price=limit_price,
                                  quantity=quantity,
                                  tradingsymbol=trading_symbol,
                                  exchange=self.kite_obj.EXCHANGE_NFO,
                                  transaction_type=self.kite_obj.TRANSACTION_TYPE_SELL,
                                  order_type=self.kite_obj.ORDER_TYPE_SL,
                                  product=self.kite_obj.PRODUCT_NRML,
                                  variety=self.kite_obj.VARIETY_REGULAR)

    def place_limit_buy_nfo(self, trading_symbol, quantity, limit_price):
        self.kite_obj.place_order(price=limit_price,
                                  trigger_price=limit_price,
                                  quantity=quantity,
                                  tradingsymbol=trading_symbol,
                                  exchange=self.kite_obj.EXCHANGE_NFO,
                                  transaction_type=self.kite_obj.TRANSACTION_TYPE_BUY,
                                  order_type=self.kite_obj.ORDER_TYPE_LIMIT,
                                  product=self.kite_obj.PRODUCT_NRML,
                                  variety=self.kite_obj.VARIETY_REGULAR)

    def place_raw(self, price, trigger_price, quantity, trading_symbol, exchange, transaction_type, order_type, product, variety):
        self.kite_obj.place_order(price=price,
                                  trigger_price=trigger_price,
                                  quantity=quantity,
                                  tradingsymbol=trading_symbol,
                                  exchange=exchange,
                                  transaction_type=transaction_type,
                                  order_type=order_type,
                                  product=product,
                                  variety=variety)


if __name__ == "__main__":
    orders_obj = Orders("dummy")
    charges = orders_obj.calculate_transaction_charges(47, 72, 50, "OPT")
    print(charges)
