import pandas as pd
pd.set_option("display.max_columns", 50)
import datetime as dt
from time import sleep
from pprint import pprint
import os
from fnodataprocessor import FnoDataProcessor
from utilsall.utils import fetch_instru_token
from utilsall.orders import Orders
from utilsall.utils import logger_intialise, printer_logger, add_row_to_csv, get_latest_json_dict
from utilsall.misc import create_print_dict, creat_empty_order_dict, reach_project_dir
from utilsall.testprint import test_prints

class Strategy:
    def __init__(self, kite_obj, config, testing=False):
        self.kite_obj = kite_obj
        self.config = config
        self.testing = testing
        self.nf_fut_obj = None
        self.nf_ce_obj = None
        self.nf_pe_obj = None
        self.bnf_fut_obj = None
        self.bnf_ce_obj = None
        self.bnf_pe_obj = None
        self.candle_interval = self.config["candle_interval"]
        self.orders = Orders(self.kite_obj, self.testing)

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
        self.order_dict["entryorder"] = creat_empty_order_dict()
        self.order_dict["slorder1"] = creat_empty_order_dict()
        self.order_dict["slorder2"] = creat_empty_order_dict()
        self.order_dict["slorder3"] = creat_empty_order_dict()
        self.order_dict["slorderglobal"] = creat_empty_order_dict()
        test_prints(f"{__class__.__name__}, object created")

    def initialise_logs_n_files(self):
        # todo order csv&logger logs for all orders place, cancel, sl, exits
        self.logger = logger_intialise("strategy")
        pwd = os.getcwd()
        reach_project_dir()
        file = "csv_files/startegy.csv"
        add_row_to_csv(row=["timestamp", "process", "pnl"],
                       file_path=file,
                       print_=True)
        os.chdir(pwd)
        printer_logger("logs and json initialised", self.logger, print_=True)
        test_prints(f"{__class__.__name__}, initialise csv and logs")


    def prepare_strategy_dict_n_json(self):
        test_prints(f"{__class__.__name__}, pre strat dict n json")
        pass

    def read_latest_strategy_dict(self):
        pwd = os.getcwd()
        reach_project_dir()
        file = "/json_files/startegy.json"
        strategy_json_filepath = file
        os.chdir(pwd)
        self.strategy_state_dict = get_latest_json_dict(strategy_json_filepath)
        test_prints(f"{__class__.__name__}, read last strategy dict")

    def _set_dataprocessor_obj(self):
        nf_fut_token = fetch_instru_token(self.kite_obj, "NIFTY", None, "FUT")
        self.nf_fut_obj = FnoDataProcessor(self.kite_obj, nf_fut_token, self.candle_interval, None)
        nf_ce_token = fetch_instru_token(self.kite_obj, "NIFTY", self.config["nifty_strike_ce"], "CE")
        self.nf_ce_obj = FnoDataProcessor(self.kite_obj, nf_ce_token, self.candle_interval, self.nf_fut_obj.last_close_price)
        nf_pe_token = fetch_instru_token(self.kite_obj, "NIFTY", self.config["nifty_strike_pe"], "PE")
        self.nf_pe_obj = FnoDataProcessor(self.kite_obj, nf_pe_token, self.candle_interval, self.nf_fut_obj.last_close_price)
        bnf_fut_token = fetch_instru_token(self.kite_obj, "BANKNIFTY", None, "FUT")
        self.bnf_fut_obj = FnoDataProcessor(self.kite_obj, bnf_fut_token, self.candle_interval, None)
        bnf_ce_token = fetch_instru_token(self.kite_obj, "BANKNIFTY", self.config["banknifty_strike_ce"], "CE")
        self.bnf_ce_obj = FnoDataProcessor(self.kite_obj, bnf_ce_token, self.candle_interval, self.bnf_fut_obj.last_close_price)
        bnf_pe_token = fetch_instru_token(self.kite_obj, "BANKNIFTY", self.config["banknifty_strike_pe"], "PE")
        self.bnf_pe_obj = FnoDataProcessor(self.kite_obj, bnf_pe_token, self.candle_interval, self.bnf_fut_obj.last_close_price)
        test_prints(f"{__class__.__name__}, fetch token and create dataproc object")

    def _init_dataprocessor(self):
        self.nf_fut_obj.initialise()
        self.nf_ce_obj.initialise()
        self.nf_pe_obj.initialise()
        self.bnf_fut_obj.initialise()
        self.bnf_ce_obj.initialise()
        self.bnf_pe_obj.initialise()
        test_prints(f"{__class__.__name__}, initi dataproc object")


    def _update_dataprocessor(self):
        self.nf_fut_obj.update()
        self.nf_ce_obj.update()
        self.nf_pe_obj.update()
        self.bnf_fut_obj.update()
        self.bnf_ce_obj.update()
        self.bnf_pe_obj.update()
        test_prints(f"{__class__.__name__}, update dataproc object")


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
        test_prints(f"{__class__.__name__}, set trading security as per rank else none")


    def place_order_process(self):
        self.send_buy_order_ifvalid()
        if self.order_dict["entryorder"]["oid"] == "":
            printer_logger("buy not triggered", self.logger, "info", True)
        else:
            printer_logger("buy triggered", self.logger, "info", True)
            self.strategy_state_dict["signals"] += 1
            if self.get_order_status(self.order_dict["entryorder"]["oid"]) == "complete":
                self.buy_complete_process()
                self.strategy_state_dict["trades"] += 1
            elif self.get_order_status(self.order_dict["entryorder"]["oid"]) == "cancel":
                self.buy_cancel_process()
            else:
                self.buy_notyet_complete_process()
        test_prints(f"{__class__.__name__}, buy order n process to trigger if order status")


    def get_order_status(self, oid):
        while True:
            orders_df = self.kite_obj.orders()
            # todo this might need to be converted to dataframe, above
            this_order = orders_df[orders_df["order_id"] == oid].to_dict("records")[0]
            if this_order["status"] == "COMPLETE":
                printer_logger(f"order complete intime {oid}", self.logger, "info", True)
                test_prints(f"{__class__.__name__}, get order status from oid")
                return "complete"
            elif this_order["status"] == "CANCELLED":
                printer_logger(f"order not complete intime {oid}", self.logger, "info", True)
                test_prints(f"{__class__.__name__}, get order status from oid")
                return "cancel"
            else:
                test_prints(f"{__class__.__name__}, get order status from oid")
                return this_order["status"]


    def print_to_console(self):
        # status beacon
        # a. ON-WT = program is running, condition not met, no live position
        # b. IN-POS = program is running, condition is satisfied, live position
        # c. CLOSE-WT = program is running, condition was satisfied and closed, no live position
        # d. CLOSE-NWT = program is running, SL Limit Hit/Global SL, No further action for day
        # e. #OFF= program is not running or in exception
        # f. Update the changes to program log file
        print_data_indicator = create_print_dict(self.nf_fut_obj,
                                                 self.nf_ce_obj,
                                                 self.nf_pe_obj,
                                                 self.bnf_fut_obj,
                                                 self.bnf_ce_obj,
                                                 self.bnf_pe_obj)
        print_data_strategy = {"status_beacon": self.strategy_state_dict["status_beacon"],
                               "day pnl": "",
                               }
        print("current time: ", dt.datetime.now())
        print("Indicator signal/value/rank")
        print("Trading signal for: ",self.trading_security)
        # pprint(print_data_indicator)
        print("-"*30)
        print(self.nf_fut_obj.trading_symbol, "rank: ", self.nf_fut_obj.rank)
        print(pd.DataFrame(print_data_indicator["nf_fu"]))
        print("-"*30)
        print(self.nf_ce_obj.trading_symbol, "rank: ", self.nf_ce_obj.rank)
        print(pd.DataFrame(print_data_indicator["nf_ce"]))
        print("-"*30)
        print(self.nf_pe_obj.trading_symbol, "rank: ", self.nf_pe_obj.rank)
        print(pd.DataFrame(print_data_indicator["nf_pe"]))
        print("-"*30)
        print(self.bnf_fut_obj.trading_symbol, "rank: ", self.bnf_fut_obj.rank)
        print(pd.DataFrame(print_data_indicator["bnf_fu"]))
        print("-"*30)
        print(self.bnf_ce_obj.trading_symbol, "rank: ", self.bnf_ce_obj.rank)
        print(pd.DataFrame(print_data_indicator["bnf_ce"]))
        print("-"*30)
        print(self.bnf_pe_obj.trading_symbol, "rank: ", self.bnf_pe_obj.rank)
        print(pd.DataFrame(print_data_indicator["bnf_pe"]))
        print("-" * 30)
        # print(print_data_strategy)
        # print("current open positions:", 0)
        # print("day pnl:", 0)
        # print("no of SL hit today:", 0)
        # print("no of exit done today:", 0)
        print()
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

        test_prints(f"{__class__.__name__}, send buy order as per security selected")

    def buy_notyet_complete_process(self):
        pass
        printer_logger("buy not complete process initiated", self.logger, "info", True)
        test_prints(f"{__class__.__name__}, process not ye complete")

    def buy_cancel_process(self):
        self.trading_security = None
        printer_logger("buy order cancelled process initiated", self.logger, "info", True)
        test_prints(f"{__class__.__name__}, process buy cancel")

    def buy_complete_process(self):
        self.strategy_state_dict["status_beacon"] = "IN-POS"
        self.send_stoploss_orders()
        self.send_global_sl_order()
        printer_logger("buy complete process initiated", self.logger, "info", True)
        test_prints(f"{__class__.__name__}, process buy complete")



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
        test_prints(f"{__class__.__name__}, send gloabl sl order")

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

            self.order_dict["slorder1"]["oid"] = self.orders.place_sl_market_sell_nfo(
                self.order_dict["slorder1"]["symbol"],
                self.order_dict["slorder1"]["quantity"],
                self.order_dict["slorder1"]["limit_price"],
                "sl1stlot")
            self.order_dict["slorder2"]["oid"] = self.orders.place_sl_market_sell_nfo(
                self.order_dict["slorder2"]["symbol"],
                self.order_dict["slorder2"]["quantity"],
                self.order_dict["slorder2"]["limit_price"],
                "sl2ndlot")
            self.order_dict["slorder3"]["oid"] = self.orders.place_sl_market_sell_nfo(
                self.order_dict["slorder3"]["symbol"],
                self.order_dict["slorder3"]["quantity"],
                self.order_dict["slorder3"]["limit_price"],
                "sl3rdlot")
        test_prints(f"{__class__.__name__}, send 3 sl order")

    def initialise(self):
        self.initialise_logs_n_files()
        self.prepare_strategy_dict_n_json()
        self.read_latest_strategy_dict()
        self._set_dataprocessor_obj()
        self._init_dataprocessor()
        self._update_dataprocessor()
        self.set_trading_security()
        self.place_order_process()
        test_prints(f"{__class__.__name__}, initialise")

    def update(self):
        self._update_dataprocessor()
        self.place_order_process()
        test_prints(f"{__class__.__name__}, update")
