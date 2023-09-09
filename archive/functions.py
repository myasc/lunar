def send_global_sl_order(self):
    self.order_dict["slorderglobal"]["symbol"] = self.order_dict["entryorder"]["symbol"]
    self.order_dict["slorderglobal"]["quantity"] = self.order_dict["entryorder"]["quantity"]
    self.order_dict["slorderglobal"]["limit_price"] = self.order_dict["entryorder"]["limit_price"] - \
                                                      self.config["global_sl"]
    sl_resp = self.orders.place_sl_market_sell_nfo(self.order_dict["slorderglobal"]["symbol"],
                                                   self.order_dict["slorderglobal"]["quantity"],
                                                   self.order_dict["slorderglobal"]["limit_price"],
                                                   "globalsl")
    self.order_dict["slorderglobal"]["oid"] = sl_resp["data"]["order_id"]

