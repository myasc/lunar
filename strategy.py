from fnodataprocessor import FnoDataProcessor
from utilsall.utils import fetch_instru_token
from utilsall.Orders import Orders


class Strategy:
    def __init__(self, kite_obj, config):
        self.kite_obj = kite_obj
        self.config = config
        self.nf_fut_obj = None
        self.nf_ce_obj = None
        self.nf_pe_obj = None
        self.bnf_fut_obj = None
        self.bnf_ce_obj = None
        self.bnf_pe_obj = None
        self.candle_interval = self.config["candle_interval"]
        self.orders = Orders(self.kite_obj)

        self.ce_buy_trigger = False
        self.pe_buy_trigger = False

        self.last_buy_order_filled = None
        #todo change this to false before every order


    def _set_dataprocessor_obj(self):
        nf_fut_token = fetch_instru_token(self.kite_obj, "NIFTY", None, "FUT")
        nf_ce_token = fetch_instru_token(self.kite_obj, "NIFTY", self.config["nifty_strike_ce"], "CE")
        nf_pe_token = fetch_instru_token(self.kite_obj, "NIFTY", self.config["nifty_strike_pe"], "PE")
        bnf_fut_token = fetch_instru_token(self.kite_obj, "BANKNIFTY", None, "FUT")
        bnf_ce_token = fetch_instru_token(self.kite_obj, "BANKNIFTY", self.config["banknifty_strike_ce"], "CE")
        bnf_pe_token = fetch_instru_token(self.kite_obj, "BANKNIFTY", self.config["banknifty_strike_pe"], "PE")

        self.nf_fut_obj = FnoDataProcessor(self.kite_obj, nf_fut_token, self.candle_interval)
        self.nf_ce_obj = FnoDataProcessor(self.kite_obj, nf_ce_token, self.candle_interval)
        self.nf_pe_obj = FnoDataProcessor(self.kite_obj, nf_pe_token, self.candle_interval)
        self.bnf_fut_obj = FnoDataProcessor(self.kite_obj, bnf_fut_token, self.candle_interval)
        self.bnf_ce_obj = FnoDataProcessor(self.kite_obj, bnf_ce_token, self.candle_interval)
        self.bnf_pe_obj = FnoDataProcessor(self.kite_obj, bnf_pe_token, self.candle_interval)

    def _init_dataprocessor_obj(self):
        self.nf_fut_obj.initialise()
        self.nf_ce_obj.initialise()
        self.nf_pe_obj.initialise()
        self.bnf_fut_obj.initialise()
        self.bnf_ce_obj.initialise()
        self.bnf_pe_obj.initialise()

    def set_trigger_cepe_buy(self):
        if (self.nf_fut_obj.rank >= 30) \
                and (self.bnf_fut_obj.rank >= 30) \
                and (self.nf_ce_obj.rank >= 70) \
                and (self.nf_pe_obj.rank <= 30):
            self.ce_buy_trigger = True
        else:
            self.ce_buy_trigger = False

        if (self.nf_fut_obj.rank <= 30) \
                and (self.bnf_fut_obj.rank <= 30) \
                and (self.nf_ce_obj.rank <= 30) \
                and (self.nf_pe_obj.rank >= 70):
            self.pe_buy_trigger = True
        else:
            self.pe_buy_trigger = False

    def send_orders(self):
        # buy order
        # stoploss orders

    def send_buy_order(self):
        symbol = ""
        quantity = 0
        limit_price = 0

        if self.ce_buy_trigger:
            if self.config["option_buy_underlying"] == "NIFTY":
                symbol = self.nf_ce_obj.trading_symbol
                quantity = self.config["lots_per_set"] * self.nf_ce_obj.lot_size
                limit_price = self.nf_ce_obj.last_close_price
            elif self.config["option_buy_underlying"] == "BANKNIFTY":
                symbol = self.bnf_ce_obj.trading_symbol
                quantity = self.config["lots_per_set"] * self.bnf_ce_obj.lot_size
                limit_price = self.bnf_ce_obj.last_close_price
            else:
                print(f"Invalid config['option_buy_underlying']: {self.config['option_buy_underlying']}")
        elif self.pe_buy_trigger:
            if self.config["option_buy_underlying"] == "NIFTY":
                symbol = self.nf_pe_obj.trading_symbol
                quantity = self.config["lots_per_set"] * self.nf_pe_obj.lot_size
                limit_price = self.nf_pe_obj.last_close_price
            elif self.config["option_buy_underlying"] == "BANKNIFTY":
                symbol = self.bnf_pe_obj.trading_symbol
                quantity = self.config["lots_per_set"] * self.bnf_pe_obj.lot_size
                limit_price = self.bnf_pe_obj.last_close_price
            else:
                print(f"Invalid config['option_buy_underlying']: {self.config['option_buy_underlying']}")
        else:
            print("no buy order trigger, passing")

        buy_resp = self.orders.place_limit_buy_nfo(symbol, quantity, limit_price)
        last_buy_oid = buy_resp["order_id"]
        #todo if order response completed or filled_quantity=quantity
        if buy_resp["status"] == "completed":
            self.buy_complete_process()
        else:
            self.buy_not_complete_process()

    def buy_not_complete_process(self):
        if time >= 3min from order time:
            cancel order
        change signal related variable changes

    def buy_complete_process(self):
        log order details
        count trade for signal generated

        in orders.json named as strategy startdatetime store following
        every order
        jsonupdatetime
        json createtime
        order_id
        order_status
        order_createtime
        order_updatetime
        entry_price
        fill_price
        order complete/or imcomplete (to trigger stoploss orders)
        first, second, third SL prices set and order sent

