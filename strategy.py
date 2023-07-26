import pandas as pd
import datetime as dt
from time import sleep

import utilsall.utils
from fnodataprocessor import FnoDataProcessor
from utilsall.utils import fetch_instru_token
from utilsall.Orders import Orders
from utilsall.utils import logger_intialise, printer_logger, add_row_to_csv


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

        self.logger = None
        self.trading_security = None

        self.strategy_state_dict = dict()
        self.strategy_state_dict["loggedat"] = str(dt.datetime.now())
        self.strategy_state_dict["signals"] = 0  # -1
        self.strategy_state_dict["trades"] = 0  # -1
        self.strategy_state_dict["slhit"] = 0  # -1
        self.strategy_state_dict["exits"] = 0  # -1
        self.strategy_state_dict["status_beacon"] = None  # -1

        self.order_dict = dict()
        self.order_dict["entryorder"] = {"symbol": "",
                                         "quantity": 0,
                                         "limit_price": 0,
                                         "oid": "",
                                         "state": ""}
        self.order_dict["slorder1"] = {"symbol": "",
                                       "quantity": 0,
                                       "limit_price": 0,
                                       "oid": "",
                                       "state": ""}
        self.order_dict["slorder2"] = {"symbol": "",
                                       "quantity": 0,
                                       "limit_price": 0,
                                       "oid": "",
                                       "state": ""}
        self.order_dict["slorder3"] = {"symbol": "",
                                       "quantity": 0,
                                       "limit_price": 0,
                                       "oid": "",
                                       "state": ""}
        self.order_dict["slorderglobal"] = {"symbol": "",
                                            "quantity": 0,
                                            "limit_price": 0,
                                            "oid": "",
                                            "state": ""}

    def initialise_logs_n_files(self):
        # todo order csv&logger logs for all orders place, cancel, sl, exits
        self.logger = logger_intialise("strategy")
        add_row_to_csv(row=["timestamp", "process", "pnl"],
                       file_path="/Users/asc/Documents/atdv/Lunar/csv_files/startegy.csv",
                       print_=True)
        printer_logger("logs and json initialised", self.logger, print_=True)

    def prepare_strategy_dict_n_json(self):
        pass

    def read_latest_strategy_dict(self):
        strategy_json_filepath = "/Users/asc/Documents/atdv/Lunar/json_files/startegy.json"
        self.strategy_state_dict = utilsall.utils.get_latest_json_dict(strategy_json_filepath)

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

    def _init_dataprocessor(self):
        self.nf_fut_obj.initialise()
        self.nf_ce_obj.initialise()
        self.nf_pe_obj.initialise()
        self.bnf_fut_obj.initialise()
        self.bnf_ce_obj.initialise()
        self.bnf_pe_obj.initialise()

    def _update_dataprocessor(self):
        self.nf_fut_obj.update()
        self.nf_ce_obj.update()
        self.nf_pe_obj.update()
        self.bnf_fut_obj.update()
        self.bnf_ce_obj.update()
        self.bnf_pe_obj.update()

    def set_trading_security(self):
        self.strategy_state_dict["status_beacon"] = "ON-WT"
        if (self.nf_fut_obj.rank >= 30) \
                and (self.bnf_fut_obj.rank >= 30) \
                and (self.nf_ce_obj.rank >= 70) \
                and (self.nf_pe_obj.rank <= 30):
            if self.config["option_buy_underlying"] == "NIFTY":
                self.trading_security = "niftyce"
            elif self.config["option_buy_underlying"] == "BANKNIFTY":
                self.trading_security = "bankniftyce"
            else:
                print(f"Invalid config['option_buy_underlying']: {self.config['option_buy_underlying']}")
                self.trading_security = None
        elif (self.nf_fut_obj.rank <= 30) \
                and (self.bnf_fut_obj.rank <= 30) \
                and (self.nf_pe_obj.rank >= 70) \
                and (self.nf_ce_obj.rank <= 30):
            if self.config["option_buy_underlying"] == "NIFTY":
                self.trading_security = "niftype"
            elif self.config["option_buy_underlying"] == "BANKNIFTY":
                self.trading_security = "bankniftype"
            else:
                print(f"Invalid config['option_buy_underlying']: {self.config['option_buy_underlying']}")
                self.trading_security = None
        else:
            self.trading_security = None

    def place_order_process(self):
        if self.order_dict["entryorder"]["oid"] == "":
            printer_logger("buy not triggered", self.logger, "info", True)
        else:
            printer_logger("buy triggered", self.logger, "info", True)
            self.strategy_state_dict["signals"] += 1
            if self.is_order_filled_timely(self.order_dict["entryorder"]["oid"]):
                self.buy_complete_process()
                self.strategy_state_dict["trades"] += 1
            else:
                self.buy_not_complete_process()

    def print_to_console(self):
        # status beacon
        # a. ON-WT = program is running, condition not met, no live position
        # b. IN-POS = program is running, condition is satisfied, live position
        # c. CLOSE-WT = program is running, condition was satisfied and closed, no live position
        # d. CLOSE-NWT = program is running, SL Limit Hit/Global SL, No further action for day
        # e. #OFF= program is not running or in exception
        # f. Update the changes to program log file

        print("current time: ", dt.datetime.now())
        print("program beacon running status", self.strategy_state_dict["status_beacon"])
        print("start date considered for FUT and Option", self.nf_fut_obj.data_start_datetime)
        print("end date considered for FUT and Option", self.nf_fut_obj.data_end_datetime)
        print("Indicator signal/value/rank")
        # print("1", self.nf_fut_obj.rank)
        print("current open positions")
        print("day pnl")
        print("no of SL hit today")
        print("no of exit done today")
        print()

    def send_buy_order_ifvalid(self):
        if self.trading_security is None:
            print(f"buy order security set as {self.trading_security}, passing")
        else:
            printer_logger(f"entry order waiting after valid signal", self.logger, "info", True)
            sleep(self.config["entry_order_wait_min"] * 55)  # little less than 60 seconds
            if self.trading_security == "niftyce":
                self.order_dict["entryorder"]["symbol"] = self.nf_ce_obj.trading_symbol
                self.order_dict["entryorder"]["quantity"] = self.config["lots_per_set"] * self.nf_ce_obj.lot_size
                self.order_dict["entryorder"]["limit_price"] = self.nf_ce_obj.last_close_price
            elif self.trading_security == "bankniftyce":
                self.order_dict["entryorder"]["symbol"] = self.bnf_ce_obj.trading_symbol
                self.order_dict["entryorder"]["quantity"] = self.config["lots_per_set"] * self.bnf_ce_obj.lot_size
                self.order_dict["entryorder"]["limit_price"] = self.bnf_ce_obj.last_close_price
            elif self.trading_security == "niftype":
                self.order_dict["entryorder"]["symbol"] = self.nf_pe_obj.trading_symbol
                self.order_dict["entryorder"]["quantity"] = self.config["lots_per_set"] * self.nf_pe_obj.lot_size
                self.order_dict["entryorder"]["limit_price"] = self.nf_pe_obj.last_close_price
            elif self.trading_security == "bankniftype":
                self.order_dict["entryorder"]["symbol"] = self.bnf_pe_obj.trading_symbol
                self.order_dict["entryorder"]["quantity"] = self.config["lots_per_set"] * self.bnf_pe_obj.lot_size
                self.order_dict["entryorder"]["limit_price"] = self.bnf_pe_obj.last_close_price
            else:
                print(f"buy order security set as {self.trading_security}, passing")

            buy_resp = self.orders.place_limit_buy_nfo(self.order_dict["entryorder"]["symbol"],
                                                       self.order_dict["entryorder"]["quantity"],
                                                       self.order_dict["entryorder"]["limit_price"],
                                                       "entry")
            self.order_dict["entryorder"]["oid"] = buy_resp["data"]["order_id"]

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

    def buy_not_complete_process(self):
        cancel_resp = self.kite_obj.cancel_order(self.kite_obj.VARIETY_REGULAR, self.order_dict["entryorder"]["oid"])
        self.trading_security = None
        printer_logger("buy not complete process initiated", self.logger, "info", True)

    def buy_complete_process(self):
        self.strategy_state_dict["status_beacon"] = "IN-POS"
        self.send_stoploss_orders()
        self.send_global_sl_order()
        printer_logger("buy complete process initiated", self.logger, "info", True)

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

    def send_stoploss_orders(self):
        if self.trading_security is None:
            print(f"none stoploss orders, security set as {self.trading_security}, passing")
        else:
            if self.trading_security == "niftyce":
                self.order_dict["slorder1"]["symbol"] = self.nf_ce_obj.trading_symbol
                self.order_dict["slorder1"]["quantity"] = self.nf_ce_obj.lot_size
                self.order_dict["slorder1"]["limit_price"] = self.nf_ce_obj.ti_1_sl_value

                self.order_dict["slorder2"]["symbol"] = self.nf_ce_obj.trading_symbol
                self.order_dict["slorder2"]["quantity"] = self.nf_ce_obj.lot_size
                self.order_dict["slorder2"]["limit_price"] = self.nf_ce_obj.ti_2_sl_value

                self.order_dict["slorder3"]["symbol"] = self.nf_ce_obj.trading_symbol
                self.order_dict["slorder3"]["quantity"] = self.nf_ce_obj.lot_size
                self.order_dict["slorder3"]["limit_price"] = self.nf_ce_obj.ti_3_sl_value
            elif self.trading_security == "bankniftyce":
                self.order_dict["slorder1"]["symbol"] = self.bnf_ce_obj.trading_symbol
                self.order_dict["slorder1"]["quantity"] = self.bnf_ce_obj.lot_size
                self.order_dict["slorder1"]["limit_price"] = self.bnf_ce_obj.ti_1_sl_value

                self.order_dict["slorder2"]["symbol"] = self.bnf_ce_obj.trading_symbol
                self.order_dict["slorder2"]["quantity"] = self.bnf_ce_obj.lot_size
                self.order_dict["slorder2"]["limit_price"] = self.bnf_ce_obj.ti_2_sl_value

                self.order_dict["slorder3"]["symbol"] = self.bnf_ce_obj.trading_symbol
                self.order_dict["slorder3"]["quantity"] = self.bnf_ce_obj.lot_size
                self.order_dict["slorder3"]["limit_price"] = self.bnf_ce_obj.ti_3_sl_value
            elif self.trading_security == "niftype":
                self.order_dict["slorder1"]["symbol"] = self.nf_pe_obj.trading_symbol
                self.order_dict["slorder1"]["quantity"] = self.nf_pe_obj.lot_size
                self.order_dict["slorder1"]["limit_price"] = self.nf_pe_obj.ti_1_sl_value

                self.order_dict["slorder2"]["symbol"] = self.nf_pe_obj.trading_symbol
                self.order_dict["slorder2"]["quantity"] = self.nf_pe_obj.lot_size
                self.order_dict["slorder2"]["limit_price"] = self.nf_pe_obj.ti_2_sl_value

                self.order_dict["slorder3"]["symbol"] = self.nf_pe_obj.trading_symbol
                self.order_dict["slorder3"]["quantity"] = self.nf_pe_obj.lot_size
                self.order_dict["slorder3"]["limit_price"] = self.nf_pe_obj.ti_3_sl_value
            elif self.trading_security == "bankniftype":
                self.order_dict["slorder1"]["symbol"] = self.bnf_pe_obj.trading_symbol
                self.order_dict["slorder1"]["quantity"] = self.bnf_pe_obj.lot_size
                self.order_dict["slorder1"]["limit_price"] = self.bnf_pe_obj.ti_1_sl_value

                self.order_dict["slorder2"]["symbol"] = self.bnf_pe_obj.trading_symbol
                self.order_dict["slorder2"]["quantity"] = self.bnf_pe_obj.lot_size
                self.order_dict["slorder2"]["limit_price"] = self.bnf_pe_obj.ti_2_sl_value

                self.order_dict["slorder3"]["symbol"] = self.bnf_pe_obj.trading_symbol
                self.order_dict["slorder3"]["quantity"] = self.bnf_pe_obj.lot_size
                self.order_dict["slorder3"]["limit_price"] = self.bnf_pe_obj.ti_3_sl_value
            else:
                print(f"none stoploss orders, security set as {self.trading_security}, passing")

            self.order_dict["slorder1"]["oid"] = self.orders.place_sl_market_sell_nfo(self.order_dict["slorder1"]["symbol"],
                                                 self.order_dict["slorder1"]["quantity"],
                                                 self.order_dict["slorder1"]["limit_price"],
                                                 "sl1stlot")
            self.order_dict["slorder2"]["oid"] = self.orders.place_sl_market_sell_nfo(self.order_dict["slorder2"]["symbol"],
                                                 self.order_dict["slorder2"]["quantity"],
                                                 self.order_dict["slorder2"]["limit_price"],
                                                 "sl2ndlot")
            self.order_dict["slorder3"]["oid"] = self.orders.place_sl_market_sell_nfo(self.order_dict["slorder3"]["symbol"],
                                                 self.order_dict["slorder3"]["quantity"],
                                                 self.order_dict["slorder3"]["limit_price"],
                                                 "sl3rdlot")
