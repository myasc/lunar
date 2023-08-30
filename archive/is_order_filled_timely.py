def is_order_filled_timely(self, oid):
    while True:
        orders_df = self.kite_obj.orders()
        this_order = orders_df[orders_df["order_id"] == oid].to_dict("records")[0]
        order_time = pd.to_datetime(this_order["order_timestamp"])
        now_time = dt.datetime.now()
        waittill_time = order_time + dt.timedelta(minutes=self.config["entry_order_valid_min"])
        if this_order["status"] == "COMPLETE":
            printer_logger(f"order complete intime {oid}", self.logger, "info", True)
            return True
        elif now_time > waittill_time:
            printer_logger(f"order not complete intime {oid}", self.logger, "info", True)
            return False
        sleep(30)