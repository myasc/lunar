import pandas as pd
pd.set_option("display.max_columns", 50)
import datetime as dt
from time import sleep
from pprint import pprint
import os
from fnodataprocessor import FnoDataProcessor
from utilsall.utils import fetch_instru_token, save_dict_to_json_file, sleep_till_time
from utilsall.orders import Orders
from utilsall.utils import logger_intialise, printer_logger, add_row_to_csv, get_latest_json_dict, is_market_open, is_market_holiday
from utilsall.misc import create_print_dict, creat_empty_order_dict, reach_project_dir


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
        self.csv_strategy_log_file_path = None
        self.strat_json_file_path = None
        self.trading_security = None
        self.signal_security = None
        self.trading_instru_obj_ref_dict = None
        self.all_instru_obj_ref_dict = None

        self.csv_log_row_list = []
        self.strategy_state_dict = dict()
        self.strategy_state_dict["loggedat"] = str(dt.datetime.now())
        self.strategy_state_dict["trading_symbol"] = None  # -1
        self.strategy_state_dict["trading_instu_token"] = 0  # -1
        self.strategy_state_dict["signals"] = 0  # -1
        self.strategy_state_dict["trades"] = 0  # -1
        self.strategy_state_dict["slhit"] = 0  # -1
        self.strategy_state_dict["tphit"] = 0  # -1
        self.strategy_state_dict["daypnl"] = 0  # -1
        self.strategy_state_dict["tradepnl"] = 0  # -1
        self.strategy_state_dict["status_beacon"] = None  # -1
        self.strategy_state_dict["status_code"] = 0  # -1
        self.strategy_state_dict["last_processed_timestamp"] = None  # -1

        self.order_dict = dict()
        self.order_dict["entryorder"] = creat_empty_order_dict()
        self.order_dict["tporder1"] = creat_empty_order_dict()
        self.order_dict["tporder2"] = creat_empty_order_dict()
        self.order_dict["tporder3"] = creat_empty_order_dict()
        self.order_dict["slglobal"] = creat_empty_order_dict()
        self.order_dict["slindicator"] = creat_empty_order_dict()

        self.strategy_initialised = False

    def initialise_logs_n_files(self):
        self.logger = logger_intialise("strategy")
        self.init_strategy_csv_log()
        self.init_strategy_json()
        printer_logger("logs and json initialised", self.logger, print_=True)

    def init_strategy_json(self):
        date_str = str(dt.datetime.now().date()).replace("-", "")
        self.strat_json_file_path = f"json_files/strategy_{date_str}.json"
        pwd = os.getcwd()
        reach_project_dir()
        if not os.path.exists(self.strat_json_file_path):
            save_dict_to_json_file(self.strategy_state_dict, self.strat_json_file_path)
        else:
            latest_dict = get_latest_json_dict(self.strat_json_file_path)
            if latest_dict != {}:
                self.strategy_state_dict = latest_dict
                self.strategy_state_dict["last_processed_timestamp"] = pd.to_datetime(self.strategy_state_dict["last_processed_timestamp"])
        os.chdir(pwd)

    def init_strategy_csv_log(self):
        date_str = str(dt.datetime.now().date()).replace("-", "")
        self.csv_strategy_log_file_path = f"csv_files/strategy_{date_str}.csv"
        add_row_to_csv(row=["process", "pnl"],
                       file_path=self.csv_strategy_log_file_path,
                       print_=True)

    def write_csv_n_json(self):
        date_str = str(dt.datetime.now().date()).replace("-", "")
        #write strategy state json
        self.strat_json_file_path = f"json_files/strategy_{date_str}.json"
        strategy_state_dict_copy = self.strategy_state_dict
        strategy_state_dict_copy["last_processed_timestamp"] = str(strategy_state_dict_copy["last_processed_timestamp"])
        save_dict_to_json_file(strategy_state_dict_copy, self.strat_json_file_path)
        # write strategy csv logs
        self.csv_strategy_log_file_path = f"csv_files/strategy_{date_str}.csv"
        add_row_to_csv(row=self.csv_log_row_list,
                       file_path=self.csv_strategy_log_file_path,
                       print_=True)

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

        self.trading_instru_obj_ref_dict = {"niftyce": self.nf_ce_obj,
                                            "bankniftyce": self.bnf_ce_obj,
                                            "niftype": self.nf_pe_obj,
                                            "bankniftype": self.bnf_pe_obj,
                                            }
        self.all_instru_obj_ref_dict = {"niftyfut": self.nf_fut_obj,
                                        "niftyce": self.nf_ce_obj,
                                        "niftype": self.nf_pe_obj,
                                        "bankniftyfut": self.bnf_fut_obj,
                                        "bankniftyce": self.bnf_ce_obj,
                                        "bankniftype": self.bnf_pe_obj,
                                        }

    def _init_dataprocessor(self):
        for objname in self.all_instru_obj_ref_dict.keys():
            self.all_instru_obj_ref_dict[objname].initialise()

    def _update_dataprocessor(self):
        for objname in self.all_instru_obj_ref_dict.keys():
            self.all_instru_obj_ref_dict[objname].update()
    def check_for_signal(self):
        if (self.nf_fut_obj.rank >= 30) \
                and (self.bnf_fut_obj.rank >= 30) \
                and (self.nf_ce_obj.rank >= 70) \
                and (self.nf_pe_obj.rank <= 30):
            if self.config["option_buy_underlying"] == "NIFTY":
                self.signal_security = "niftyce"
                self.strategy_state_dict["signals"] += 1
            elif self.config["option_buy_underlying"] == "BANKNIFTY":
                self.signal_security = "bankniftyce"
                self.strategy_state_dict["signals"] += 1
            else:
                print(f"Invalid config['option_buy_underlying']: {self.config['option_buy_underlying']}")
                self.signal_security = None
        elif (self.nf_fut_obj.rank <= 30) \
                and (self.bnf_fut_obj.rank <= 30) \
                and (self.nf_pe_obj.rank >= 70) \
                and (self.nf_ce_obj.rank <= 30):
            if self.config["option_buy_underlying"] == "NIFTY":
                self.signal_security = "niftype"
                self.strategy_state_dict["signals"] += 1
            elif self.config["option_buy_underlying"] == "BANKNIFTY":
                self.signal_security = "bankniftype"
                self.strategy_state_dict["signals"] += 1
            else:
                print(f"Invalid config['option_buy_underlying']: {self.config['option_buy_underlying']}")
                self.signal_security = None
        else:
            self.signal_security = None

        # todo remove when not testing
        self.signal_security = "niftype"

    def set_strategy_killswitch_codes(self):
        now = dt.datetime.now()
        strategy_opentime = self.config["program_start_time"]
        strategy_closetime = self.config["program_exit_time"]

        if self.strategy_state_dict["slhit"] >= self.config["max_stoploss_per_day"]:
            self.strategy_state_dict["status_code"] = 203
            printer_logger("max sl hit per day", self.logger, "info", True)
        elif self.strategy_state_dict["trades"] >= self.config["max_trades_per_day"]:
            self.strategy_state_dict["status_code"] = 204
            printer_logger("max trade per day", self.logger, "info", True)
        elif (now >= strategy_opentime) and (now < strategy_closetime):
            self.strategy_state_dict["status_code"] = 201
            printer_logger("outside strategy time", self.logger, "info", True)
        else:
            pass

    def send_buy_order_ifsignal_n_validcode(self):
        if self.signal_security in self.trading_instru_obj_ref_dict.keys():
            # if self.strategy_state_dict["status_code"] in [303, 304, 203, 204, 201]:
            #     printer_logger("skipping buy order function (in position/killswitch)", self.logger, "info", True)
            # else:
                self.trading_security = self.signal_security
                printer_logger(f"placing entry order after valid signal", self.logger, "info", True)
                self.order_dict["entryorder"]["symbol"] = self.trading_instru_obj_ref_dict[self.trading_security].trading_symbol
                self.order_dict["entryorder"]["quantity"] = self.config["num_of_sets"] * self.config["lots_per_set"] * self.trading_instru_obj_ref_dict[self.trading_security].lot_size
                self.order_dict["entryorder"]["limit_price"] = self.trading_instru_obj_ref_dict[self.trading_security].last_close_price

                buy_resp = self.orders.place_validity_limit_buy_nfo(self.order_dict["entryorder"]["symbol"],
                                                                    self.order_dict["entryorder"]["quantity"],
                                                                    self.order_dict["entryorder"]["limit_price"],
                                                                    self.config["entry_order_valid_min"],
                                                                    "entry")
                self.order_dict["entryorder"]["oid"] = buy_resp
                self.strategy_state_dict["status_code"] = 301

        else:
            print(f"buy order security set as {self.signal_security}, passing")

    def isif_buy_filled_or_cancelled(self):
        if self.order_dict["entryorder"]["status"] == "COMPLETE":
            self.strategy_state_dict["status_code"] = 303
        elif self.order_dict["entryorder"]["status"] == "CANCELLED":
            self.strategy_state_dict["status_code"] = 302
        else:
            pass


    def orders_handler(self):
        if self.strategy_state_dict["status_code"] in [500]:
            self.send_buy_order_ifsignal_n_validcode()
        elif self.strategy_state_dict["status_code"] in [301]:
            self.isif_buy_filled_or_cancelled()
        elif self.strategy_state_dict["status_code"] in [302]:
            self.buy_cancel_process()
        elif self.strategy_state_dict["status_code"] in [303]:
            self.send_sltp_orders()
            # self.send_global_sl_order()
        elif self.strategy_state_dict["status_code"] in [304]:
            print("awaiting exit for position")
        elif True:
            printer_logger("buy triggered going for complete/cancel/open process", self.logger, "info", True)
            order_status = self.orders.get_order_status(self.order_dict["entryorder"]["oid"])
            if order_status == "COMPLETE":
                self.buy_complete_process()
            elif order_status == "CANCELLED":
                self.buy_cancel_process()
            elif order_status == "OPEN":
                self.buy_open_process()
            else:
                raise Exception(f"order status other than complete,cancel, open: {order_status}")
        else:
            printer_logger("no action from orders handler", self.logger, "info", True)

    def buy_cancel_process(self):
        self.strategy_state_dict["status_code"] = 500
        self.trading_security = None
        self.order_dict["entryorder"] = creat_empty_order_dict()
        printer_logger("buy order cancelled process initiated", self.logger, "info", True)

    def buy_open_process(self):
        printer_logger("buy open process initiated", self.logger, "info", True)

    def update_order_status(self):
        if self.strategy_state_dict["status_code"] in [301, 303, 304, 401, 402]:
            self.order_dict["entryorder"]["status"] = self.orders.get_order_status(self.order_dict["entryorder"]["oid"])
            self.order_dict["tporder1"]["status"] = self.orders.get_order_status(self.order_dict["tporder1"]["oid"])
            self.order_dict["tporder2"]["status"] = self.orders.get_order_status(self.order_dict["tporder2"]["oid"])
            self.order_dict["tporder3"]["status"] = self.orders.get_order_status(self.order_dict["tporder3"]["oid"])

    def trade_exit_process(self):
        if self.order_dict["tporder3"]["status"] == "COMPLETE":
            self.trading_security = None
            self.order_dict["entryorder"] = creat_empty_order_dict()
            self.order_dict["tporder1"] = creat_empty_order_dict()
            self.order_dict["tporder2"] = creat_empty_order_dict()
            self.order_dict["tporder3"] = creat_empty_order_dict()
            # self.strategy_state_dict["slhit"] += 1
            self.strategy_state_dict["tradepnl"] = 0
        else:
            pass

    def send_sltp_orders(self):
        if self.trading_security in self.trading_instru_obj_ref_dict.keys():
            self.order_dict["tporder1"]["symbol"] = self.trading_instru_obj_ref_dict[self.trading_security].trading_symbol
            self.order_dict["tporder1"]["quantity"] = self.trading_instru_obj_ref_dict[self.trading_security].lot_size * self.config["num_of_sets"]
            self.order_dict["tporder1"]["limit_price"] = self.trading_instru_obj_ref_dict[self.trading_security].ti_1_tp_value

            self.order_dict["tporder2"]["symbol"] = self.trading_instru_obj_ref_dict[self.trading_security].trading_symbol
            self.order_dict["tporder2"]["quantity"] = self.trading_instru_obj_ref_dict[self.trading_security].lot_size * self.config["num_of_sets"]
            self.order_dict["tporder2"]["limit_price"] = self.trading_instru_obj_ref_dict[self.trading_security].ti_2_tp_value

            self.order_dict["tporder3"]["symbol"] = self.trading_instru_obj_ref_dict[self.trading_security].trading_symbol
            self.order_dict["tporder3"]["quantity"] = self.trading_instru_obj_ref_dict[self.trading_security].lot_size * self.config["num_of_sets"]
            self.order_dict["tporder3"]["limit_price"] = self.trading_instru_obj_ref_dict[self.trading_security].ti_3_tp_value

            for tp_od in [self.order_dict["tporder1"], self.order_dict["tporder2"], self.order_dict["tporder3"]]:
                order_response = self.orders.place_sl_market_sell_nfo(tp_od["symbol"], tp_od["quantity"], tp_od["limit_price"],
                                                           "tp")
                tp_od["oid"] = order_response

            self.strategy_state_dict["status_code"] = 304
        else:
            print(f"none stoploss orders, security set as {self.trading_security}, passing")

    def print_to_console(self):
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
        # print("Indicator signal/value/rank")
        # print("Trading signal for: ",self.trading_security)
        # # pprint(print_data_indicator)
        # print("-"*30)
        # print(self.nf_fut_obj.trading_symbol, "rank: ", self.nf_fut_obj.rank)
        # print(pd.DataFrame(print_data_indicator["nf_fu"]))
        # print("-"*30)
        # print(self.nf_ce_obj.trading_symbol, "rank: ", self.nf_ce_obj.rank)
        # print(pd.DataFrame(print_data_indicator["nf_ce"]))
        # print("-"*30)
        # print(self.nf_pe_obj.trading_symbol, "rank: ", self.nf_pe_obj.rank)
        # print(pd.DataFrame(print_data_indicator["nf_pe"]))
        # print("-"*30)
        # print(self.bnf_fut_obj.trading_symbol, "rank: ", self.bnf_fut_obj.rank)
        # print(pd.DataFrame(print_data_indicator["bnf_fu"]))
        # print("-"*30)
        # print(self.bnf_ce_obj.trading_symbol, "rank: ", self.bnf_ce_obj.rank)
        # print(pd.DataFrame(print_data_indicator["bnf_ce"]))
        # print("-"*30)
        # print(self.bnf_pe_obj.trading_symbol, "rank: ", self.bnf_pe_obj.rank)
        # print(pd.DataFrame(print_data_indicator["bnf_pe"]))
        # print("-" * 30)
        # print(print_data_strategy)
        # print("current open positions:", 0)
        # print("day pnl:", 0)
        # print("no of SL hit today:", 0)
        # print("no of exit done today:", 0)
        pprint(self.strategy_state_dict)
        print()
        print()

    def update_last_processed_timestamp(self):
        self.strategy_state_dict["last_processed_timestamp"] = max(self.nf_fut_obj.latest_timestamp,
                                                                   self.nf_ce_obj.latest_timestamp,
                                                                   self.nf_pe_obj.latest_timestamp,
                                                                   self.bnf_fut_obj.latest_timestamp,
                                                                   self.bnf_ce_obj.latest_timestamp,
                                                                   self.bnf_pe_obj.latest_timestamp,
                                                                   ).replace(tzinfo=None)

    def update_pnl(self):
        if self.order_dict["entryorder"]["oid"] == "":
            self.strategy_state_dict["tradepnl"] = 0
        else:
            buy_price = self.order_dict["entryorder"]["limit_price"]
            quantity_ = self.order_dict["entryorder"]["quantity"]
            self.strategy_state_dict["tradepnl"] = (self.trading_instru_obj_ref_dict[self.trading_security].last_close_price - buy_price) * quantity_

        self.strategy_state_dict["daypnl"] = self.strategy_state_dict["daypnl"] + self.strategy_state_dict["tradepnl"]

    def ready_for_next_candle(self):
        now = dt.datetime.now()
        # 2 multipled below because complete candle data is available after next candle time interval ends
        if self.config["candle_interval"] == "5minute":
            minute_delta = 2 * 5
        elif self.config["candle_interval"] == "1minute":
            minute_delta = 2 * 1
        else:
            minute_delta = 2 * 5
        last_processed_timestamp = self.strategy_state_dict["last_processed_timestamp"]
        if last_processed_timestamp is None:
            next_candle_time = now.replace(hour=9, minute=15, second=0, microsecond=0) + dt.timedelta(minutes=minute_delta) + dt.timedelta(minutes=self.config["entry_order_wait_min"])
        else:
            next_candle_time = last_processed_timestamp + dt.timedelta(minutes=minute_delta) + dt.timedelta(minutes=self.config["entry_order_wait_min"])

        if dt.datetime.now() >= next_candle_time:
            print(f"next candle available now:{now} candle:{next_candle_time} last:{last_processed_timestamp}")
            return True
        else:
            print(f"wait for candle now:{now} candle:{next_candle_time} last:{last_processed_timestamp}")
            return False

    def initialise(self):
        print("initialising strategy object")
        self.initialise_logs_n_files()
        # self.read_latest_strategy_dict()
        self._set_dataprocessor_obj()
        self._init_dataprocessor()
        self.print_to_console()
        self.strategy_initialised = True


    def update(self):
        if not is_market_holiday():
            if not self.strategy_initialised:
                self.initialise()
                self.strategy_state_dict["status_code"] = 101
            else:
                if is_market_open():
                    if self.ready_for_next_candle():
                        self._update_dataprocessor()
                        self.check_for_signal()
                        self.set_strategy_killswitch_codes()
                        self.orders_handler()
                        self.update_last_processed_timestamp()
                        self.update_pnl()
                        self.write_csv_n_json()
                        self.print_to_console()
                    else:
                        print("sleeping till next candle")
                        sleep(20)
                else:
                    self.strategy_state_dict["status_code"] = 102
                    sleep_till_time(9, 15, 30)
        else:
            self.strategy_state_dict["status_code"] = 101
            print("Market holdiay/weekend")
            exit()


