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
from utilsall.misc import creat_empty_order_dict, reach_project_dir
from utilsall.misc import create_print_dict

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
        self.strategy_json_file_path = None
        self.trading_security = None
        self.signal_security = None
        self.trading_instru_obj_ref_dict = None
        self.all_instru_obj_ref_dict = None

        self.csv_log_row_list = []
        self.strategy_state_dict = dict()
        self.strategy_state_dict["logged_at"] = str(dt.datetime.now())
        self.strategy_state_dict["trading_symbol"] = None  # -1
        self.strategy_state_dict["holding_qty"] = 0  # -1
        self.strategy_state_dict["trading_instrument_token"] = 0  # -1
        self.strategy_state_dict["signals"] = 0  # -1
        self.strategy_state_dict["trades"] = 0  # -1
        self.strategy_state_dict["sl_hit"] = 0  # -1
        self.strategy_state_dict["tp_hit"] = 0  # -1
        self.strategy_state_dict["realised_pnl"] = 0  # -1
        self.strategy_state_dict["unrealised_pnl"] = 0  # -1
        self.strategy_state_dict["status_beacon"] = None  # -1
        self.strategy_state_dict["status_code"] = 500  # -1
        self.strategy_state_dict["last_processed_timestamp"] = None  # -1

        self.order_dict = dict()
        self.order_dict["entry_order"] = creat_empty_order_dict()
        self.order_dict["tp_order1"] = creat_empty_order_dict()
        self.order_dict["tp_order2"] = creat_empty_order_dict()
        self.order_dict["tp_order3"] = creat_empty_order_dict()
        self.order_dict["sl_global"] = creat_empty_order_dict()
        self.order_dict["sl_indicator"] = creat_empty_order_dict()

        self.strategy_initialised = False

    def initialise_logs_n_files(self):
        # called in initialise
        self.logger = logger_intialise("strategy")
        self.init_strategy_csv_log()
        self.init_strategy_json()
        printer_logger(f"{__class__.__name__}:logs and json initialised", self.logger, print_=True)

    def init_strategy_json(self):
        # called in initialise_logs_n_files
        """
        creates filename with suffix strategy_ and today's date
        goes to json files directory and checks
        if today's file exist, read the newest dictionary state and last processed timestamp
        else write initial state dictionary to json file
        :return:
        """
        date_str = str(dt.datetime.now().date()).replace("-", "")
        self.strategy_json_file_path = f"json_files/strategy_{date_str}.json"
        pwd = os.getcwd()
        reach_project_dir()
        if not os.path.exists(self.strategy_json_file_path):
            save_dict_to_json_file(self.strategy_state_dict, self.strategy_json_file_path)
        else:
            latest_dict = get_latest_json_dict(self.strategy_json_file_path)
            if latest_dict != {}:
                self.strategy_state_dict = latest_dict
                self.strategy_state_dict["last_processed_timestamp"] = pd.to_datetime(self.strategy_state_dict["last_processed_timestamp"])
        os.chdir(pwd)

    def init_strategy_csv_log(self):
        # called in initialise_logs_n_files
        date_str = str(dt.datetime.now().date()).replace("-", "")
        self.csv_strategy_log_file_path = f"csv_files/strategy_{date_str}.csv"
        add_row_to_csv(row=["process", "pnl"],
                       file_path=self.csv_strategy_log_file_path,
                       print_=True)

    def _set_dataprocessor_obj(self):
        # called in initialise
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

    def _update_dataprocessor(self):
        # called in initialise and update
        for objname in self.all_instru_obj_ref_dict.keys():
            self.all_instru_obj_ref_dict[objname].update()

    def count_signal(self):
        # called inside check_for_signal
        # only counting signal when not in position
        if self.strategy_state_dict["status_code"] in [500, 201, 202, 203, 204]:
            self.strategy_state_dict["signals"] += 1
        else:
            pass

    def check_for_signal(self):
        # called in update
        if (self.nf_fut_obj.rank >= 30) \
                and (self.bnf_fut_obj.rank >= 30) \
                and (self.nf_ce_obj.rank >= 70) \
                and (self.nf_pe_obj.rank <= 30):
            if self.config["option_buy_underlying"] == "NIFTY":
                self.signal_security = "niftyce"
                self.count_signal()
            elif self.config["option_buy_underlying"] == "BANKNIFTY":
                self.signal_security = "bankniftyce"
                self.count_signal()
            else:
                print(f"Invalid config['option_buy_underlying']: {self.config['option_buy_underlying']}")
                self.signal_security = None
        elif (self.nf_fut_obj.rank <= 30) \
                and (self.bnf_fut_obj.rank <= 30) \
                and (self.nf_pe_obj.rank >= 70) \
                and (self.nf_ce_obj.rank <= 30):
            if self.config["option_buy_underlying"] == "NIFTY":
                self.signal_security = "niftype"
                self.count_signal()
            elif self.config["option_buy_underlying"] == "BANKNIFTY":
                self.signal_security = "bankniftype"
                self.count_signal()
            else:
                print(f"Invalid config['option_buy_underlying']: {self.config['option_buy_underlying']}")
                self.signal_security = None
        else:
            self.signal_security = None

        # todo remove when not testing
        self.signal_security = "niftype"
        print("for testing signal security set as: ", self.signal_security)

    def set_strategy_kill_switch_codes(self):
        # called in update
        now = dt.datetime.now().time()
        strategy_open_time = self.config["program_start_time"]
        strategy_close_time = self.config["program_exit_time"]

        if self.strategy_state_dict["sl_hit"] >= self.config["max_stoploss_per_day"]:
            self.strategy_state_dict["status_code"] = 203
            printer_logger("max sl hit per day", self.logger, "info", True)
        elif self.strategy_state_dict["trades"] >= self.config["max_trades_per_day"]:
            self.strategy_state_dict["status_code"] = 204
            printer_logger("max trade per day", self.logger, "info", True)
        elif now <= strategy_open_time:
            self.strategy_state_dict["status_code"] = 201
            printer_logger("outside strategy start time", self.logger, "info", True)
        elif now > strategy_close_time:
            self.strategy_state_dict["status_code"] = 202
            printer_logger("outside strategy end time", self.logger, "info", True)
        else:
            pass

    def send_buy_order_if_signal_n_valid_code(self):
        # called in orders handler if status code 500, waiting for signal
        print("signal security: ", self.signal_security, "trading security: ", self.trading_security)
        if self.signal_security in self.trading_instru_obj_ref_dict.keys():
            self.trading_security = self.signal_security
            printer_logger(f"placing entry order after valid signal", self.logger, "info", True)
            self.order_dict["entry_order"]["symbol"] = self.trading_instru_obj_ref_dict[self.trading_security].trading_symbol
            self.order_dict["entry_order"]["quantity"] = self.config["num_of_sets"] * self.config["lots_per_set"] * self.trading_instru_obj_ref_dict[self.trading_security].lot_size
            self.order_dict["entry_order"]["limit_price"] = self.trading_instru_obj_ref_dict[self.trading_security].last_close_price

            buy_resp = self.orders.place_validity_limit_buy_nfo(self.order_dict["entry_order"]["symbol"],
                                                                self.order_dict["entry_order"]["quantity"],
                                                                self.order_dict["entry_order"]["limit_price"],
                                                                self.config["entry_order_valid_min"],
                                                                "entry")
            self.order_dict["entry_order"]["oid"] = buy_resp
            self.strategy_state_dict["status_code"] = 301
        else:
            print(f"buy order security set as {self.signal_security}, passing")

    def if_buy_filled_or_cancelled(self):
        # called in orders handler if status code 301, buy order sent
        if self.order_dict["entry_order"]["status"] == "COMPLETE":
            self.strategy_state_dict["status_code"] = 303
            self.strategy_state_dict["holding_qty"] = self.order_dict["entry_order"]["quantity"]
        elif self.order_dict["entry_order"]["status"] == "CANCELLED":
            self.strategy_state_dict["status_code"] = 302
        elif self.order_dict["entry_order"]["status"] == "OPEN":
            self.strategy_state_dict["status_code"] = 301
        else:
            self.strategy_state_dict["status_code"] = 601

    def buy_cancel_process(self):
        # called in orders handler if status code 302, buy order cancelled
        self.strategy_state_dict["status_code"] = 500
        self.trading_security = None
        self.signal_security = None
        self.strategy_state_dict["holding_qty"] = 0 # will be already zero, because not updated until order complete
        self.order_dict["entry_order"] = creat_empty_order_dict()
        printer_logger("buy order cancelled process initiated", self.logger, "info", True)

    def send_sl_tp_orders(self):
        # called in orders handler if status code 303, buy order complete
        self.send_tp_orders()
        self.send_global_sl()
        self.strategy_state_dict["status_code"] = 304
    def send_tp_orders(self):
        # called in send_sl_tp_orders
        if self.trading_security in self.trading_instru_obj_ref_dict.keys():
            self.order_dict["tp_order1"]["symbol"] = self.trading_instru_obj_ref_dict[self.trading_security].trading_symbol
            self.order_dict["tp_order1"]["quantity"] = self.trading_instru_obj_ref_dict[self.trading_security].lot_size * self.config["num_of_sets"]
            self.order_dict["tp_order1"]["limit_price"] = self.trading_instru_obj_ref_dict[self.trading_security].ti_1_tp_value

            self.order_dict["tp_order2"]["symbol"] = self.trading_instru_obj_ref_dict[self.trading_security].trading_symbol
            self.order_dict["tp_order2"]["quantity"] = self.trading_instru_obj_ref_dict[self.trading_security].lot_size * self.config["num_of_sets"]
            self.order_dict["tp_order2"]["limit_price"] = self.trading_instru_obj_ref_dict[self.trading_security].ti_2_tp_value

            self.order_dict["tp_order3"]["symbol"] = self.trading_instru_obj_ref_dict[self.trading_security].trading_symbol
            self.order_dict["tp_order3"]["quantity"] = self.trading_instru_obj_ref_dict[self.trading_security].lot_size * self.config["num_of_sets"]
            self.order_dict["tp_order3"]["limit_price"] = self.trading_instru_obj_ref_dict[self.trading_security].ti_3_tp_value

            if self.config["num_of_sets"] * self.config["lots_per_set"] <= 0:
                pass
            elif self.config["num_of_sets"] * self.config["lots_per_set"] == 1:
                for tp_od in [self.order_dict["tp_order1"]]:
                    tp_od["oid"] = self.orders.place_limit_sell_nfo(tp_od["symbol"], tp_od["quantity"], tp_od["limit_price"],
                                                               "tp")
            elif self.config["num_of_sets"] * self.config["lots_per_set"] == 2:
                for tp_od in [self.order_dict["tp_order1"], self.order_dict["tp_order2"]]:
                    tp_od["oid"] = self.orders.place_limit_sell_nfo(tp_od["symbol"], tp_od["quantity"], tp_od["limit_price"],
                                                               "tp")
            elif self.config["num_of_sets"] * self.config["lots_per_set"] >= 3:
                for tp_od in [self.order_dict["tp_order1"], self.order_dict["tp_order2"], self.order_dict["tp_order3"]]:
                    tp_od["oid"] = self.orders.place_limit_sell_nfo(tp_od["symbol"], tp_od["quantity"], tp_od["limit_price"],
                                                               "tp")
        else:
            print(f"none takeprofit orders, security set as {self.trading_security}, passing")

    def send_global_sl(self):
        # called in send_sl_tp_orders
        if self.trading_security in self.trading_instru_obj_ref_dict.keys():
            # if existing global sl exist but holding qty change due to take profit order complete
            if (self.order_dict["sl_global"]["status"] == "OPEN") and (self.order_dict["sl_global"]["quantity"] != self.strategy_state_dict["holding_qty"]):
                self.order_dict["sl_global"]["oid"] = self.orders.modify_qty_from_orderid(self.order_dict["sl_global"]["oid"],
                                                                                         self.strategy_state_dict["holding_qty"])
                self.order_dict["sl_global"]["quantity"] = self.strategy_state_dict["holding_qty"]
            else:
                self.order_dict["sl_global"]["symbol"] = self.order_dict["entry_order"]["symbol"]
                self.order_dict["sl_global"]["quantity"] = self.order_dict["entry_order"]["quantity"]
                self.order_dict["sl_global"]["limit_price"] = self.order_dict["entry_order"]["limit_price"] - \
                                                                  self.config["global_sl"]
                self.order_dict["sl_global"]["oid"] = self.orders.place_sl_market_sell_nfo(self.order_dict["sl_global"]["symbol"],
                                                               self.order_dict["sl_global"]["quantity"],
                                                               self.order_dict["sl_global"]["limit_price"],
                                                               "global_sl")
        else:
            print(f"none global sl orders, security set as {self.trading_security}, passing")

    def send_indi_sl_if_trigger(self):
        # called in orders handler if status code 304/401/402 i.e. in position with more than 0 holding qty
        if self.trading_instru_obj_ref_dict[self.trading_security].sl_indi_sell_signal:
            self.order_dict["sl_indicator"]["symbol"] = self.order_dict["entry_order"]["symbol"]
            self.order_dict["sl_indicator"]["quantity"] = self.strategy_state_dict["holding_qty"]
            self.order_dict["sl_indicator"]["limit_price"] = self.trading_instru_obj_ref_dict[self.trading_security].last_close_price
            self.order_dict["sl_indicator"]["oid"] = self.orders.place_market_sell_nfo(self.order_dict["sl_indicator"]["symbol"],
                                                                                      self.order_dict["sl_indicator"]["quantity"],
                                                                                      "indicator_sl")
            self.strategy_state_dict["status_code"] = 405
            self.strategy_state_dict["sl_hit"] += 1
        else:
            pass

    def if_global_sl_complete(self):
        # called in orders handler if status code 304/401/402 i.e. in position with more than 0 holding qty
        if self.order_dict["sl_global"]["status"] == "COMPLETE":
            self.strategy_state_dict["status_code"] = 404
            self.strategy_state_dict["sl_hit"] += 1

    def if_tp_1_complete(self):
        # called in orders handler if status code 304 i.e. sl & tp orders sent
        if self.order_dict["tp_order1"]["status"] == "COMPLETE":
            if self.config["num_of_sets"] * self.config["lots_per_set"] == 1:
                self.strategy_state_dict["status_code"] = 403
            else:
                self.strategy_state_dict["status_code"] = 401
            self.strategy_state_dict["holding_qty"] = self.strategy_state_dict["holding_qty"] - self.order_dict["tp_order1"]["quantity"]
            self.update_realised_pnl()
            self.send_global_sl()
    def if_tp_2_complete(self):
        if self.order_dict["tp_order2"]["status"] == "COMPLETE":
            # called in orders handler if status code 401 i.e. sl & tp1 complete
            if self.config["num_of_sets"] * self.config["lots_per_set"] == 2:
                self.strategy_state_dict["status_code"] = 403
            else:
                self.strategy_state_dict["status_code"] = 402
            self.strategy_state_dict["holding_qty"] = self.strategy_state_dict["holding_qty"] - self.order_dict["tp_order2"]["quantity"]
            self.update_realised_pnl()
            self.send_global_sl()
    def if_tp_3_complete(self):
        # called in orders handler if status code 402 i.e. sl & tp2 complete
        if self.order_dict["tp_order3"]["status"] == "COMPLETE":
            self.strategy_state_dict["status_code"] = 403
            self.strategy_state_dict["tp_hit"] += 1

    def update_order_status(self):
        # called in orders handler before everything
        if self.strategy_state_dict["status_code"] in [301]:
            self.order_dict["entry_order"]["status"] = self.orders.get_order_status(self.order_dict["entry_order"]["oid"])
        elif self.strategy_state_dict["status_code"] in [304]:
            self.order_dict["tp_order1"]["status"] = self.orders.get_order_status(self.order_dict["tp_order1"]["oid"])
            self.order_dict["sl_global"]["status"] = self.orders.get_order_status(self.order_dict["sl_global"]["oid"])
        elif self.strategy_state_dict["status_code"] in [401]:
            self.order_dict["tp_order2"]["status"] = self.orders.get_order_status(self.order_dict["tp_order2"]["oid"])
            self.order_dict["sl_global"]["status"] = self.orders.get_order_status(self.order_dict["sl_global"]["oid"])
        elif self.strategy_state_dict["status_code"] in [402]:
            self.order_dict["tp_order3"]["status"] = self.orders.get_order_status(self.order_dict["tp_order3"]["oid"])
            self.order_dict["sl_global"]["status"] = self.orders.get_order_status(self.order_dict["sl_global"]["oid"])
        elif self.strategy_state_dict["status_code"] in [403, 404, 405]:
            # trade exited
            pass
        else:
            pass

    def trade_exit_process(self):
        # called in orders handler if status code 403,404,405 trade exited by tp3,gsl,isl
        self.update_realised_pnl()
        self.orders.cancel_all_tagged_open_orders()
        # self.orders.marketsell_tagged_open_orders()
        # cancel all remain orders
        self.trading_security = None
        self.signal_security = None

        self.order_dict["entry_order"] = creat_empty_order_dict()
        self.order_dict["tp_order1"] = creat_empty_order_dict()
        self.order_dict["tp_order2"] = creat_empty_order_dict()
        self.order_dict["tp_order3"] = creat_empty_order_dict()
        self.order_dict["sl_global"] = creat_empty_order_dict()
        self.order_dict["sl_indicator"] = creat_empty_order_dict()

        self.strategy_state_dict["trades"] += 1

        self.strategy_state_dict["holding_qty"] = 0
        self.strategy_state_dict["unrealised_pnl"] = 0
        self.strategy_state_dict["status_code"] = 500
        printer_logger("trade exited process", self.logger, "info", True)

    def orders_handler(self):
        # called in update, triggers respective action as per state
        self.update_order_status()
        if self.strategy_state_dict["status_code"] in [500]:
            self.send_buy_order_if_signal_n_valid_code()
        elif self.strategy_state_dict["status_code"] in [301]:
            self.if_buy_filled_or_cancelled()
        elif self.strategy_state_dict["status_code"] in [302]:
            self.buy_cancel_process()
        elif self.strategy_state_dict["status_code"] in [303]:
            self.send_sl_tp_orders()
        elif self.strategy_state_dict["status_code"] in [304]:
            self.if_tp_1_complete()
            self.if_global_sl_complete()
            self.send_indi_sl_if_trigger()
        elif self.strategy_state_dict["status_code"] in [401]:
            self.if_tp_2_complete()
            self.if_global_sl_complete()
            self.send_indi_sl_if_trigger()
        elif self.strategy_state_dict["status_code"] in [402]:
            self.if_tp_3_complete()
            self.if_global_sl_complete()
            self.send_indi_sl_if_trigger()
        elif self.strategy_state_dict["status_code"] in [403, 404, 405]:
            self.trade_exit_process()
        elif self.strategy_state_dict["status_code"] in [202, 203, 204]:
            self.pull_the_plug()
        else:
            printer_logger(f"no action from orders handler, status code :{self.strategy_state_dict['status_code']}", self.logger, "info", True)

    def update_realised_pnl(self):
        # called in if_tp_1_complete, if_tp_2_complete, trade_exit_process
        status_code = self.strategy_state_dict["status_code"]
        if status_code in [401]:
            realised_price_delta1 = self.order_dict["tp_order1"]["limit_price"] - self.order_dict["entry_order"]["limit_price"]
            realised_qty1 = self.order_dict["tp_order1"]["quantity"]
            self.strategy_state_dict["realised_pnl"] += realised_price_delta1 * realised_qty1
        elif status_code in [402]:
            realised_price_delta2 = self.order_dict["tp_order2"]["limit_price"] - self.order_dict["entry_order"]["limit_price"]
            realised_qty2 = self.order_dict["tp_order2"]["quantity"]
            self.strategy_state_dict["realised_pnl"] += realised_price_delta2 * realised_qty2
        elif status_code in [403]:
            realised_price_delta3 = self.order_dict["tp_order3"]["limit_price"] - self.order_dict["entry_order"]["limit_price"]
            realised_qty3 = self.order_dict["tp_order3"]["quantity"]
            self.strategy_state_dict["realised_pnl"] += realised_price_delta3 * realised_qty3
        elif status_code in [404]:
            realised_price_delta_slg = self.order_dict["sl_global"]["limit_price"] - self.order_dict["entry_order"]["limit_price"]
            realised_qty_slg = self.order_dict["sl_global"]["quantity"]
            self.strategy_state_dict["realised_pnl"] += realised_price_delta_slg * realised_qty_slg
        elif status_code in [405]:
            realised_price_delta_sli = self.order_dict["sl_indicator"]["limit_price"] - self.order_dict["entry_order"]["limit_price"]
            realised_qty_sli = self.order_dict["sl_indicator"]["quantity"]
            self.strategy_state_dict["realised_pnl"] += realised_price_delta_sli * realised_qty_sli
        else:
            pass

    def pull_the_plug(self):
        self.orders.cancel_all_tagged_open_orders()
        self.orders.marketsell_tagged_open_orders()
        # exit()

    def update_unrealised_pnl(self):
        # called in update
        if self.strategy_state_dict["status_code"] in [304, 401, 402, 403, 404, 405]:
            buy_price = self.order_dict["entry_order"]["limit_price"]
            quantity_ = self.strategy_state_dict["holding_qty"]
            ltp = self.trading_instru_obj_ref_dict[self.trading_security].last_close_price
            self.strategy_state_dict["unrealised_pnl"] = (ltp - buy_price) * quantity_

    def update_last_processed_timestamp(self):
        # called in update
        self.strategy_state_dict["last_processed_timestamp"] = max(self.nf_fut_obj.latest_timestamp,
                                                                   self.nf_ce_obj.latest_timestamp,
                                                                   self.nf_pe_obj.latest_timestamp,
                                                                   self.bnf_fut_obj.latest_timestamp,
                                                                   self.bnf_ce_obj.latest_timestamp,
                                                                   self.bnf_pe_obj.latest_timestamp,
                                                                   ).replace(tzinfo=None)

    def set_status_beacon(self):
        if self.strategy_state_dict["status_code"] in [500, 301]:
            self.strategy_state_dict["status_beacon"] = "ON-WT"
        elif self.strategy_state_dict["status_code"] in [101, 102, 201, 202, 203, 204, 601]:
            self.strategy_state_dict["status_beacon"] = "#OFF"
        elif self.strategy_state_dict["status_code"] in [303, 304, 401, 402]:
            self.strategy_state_dict["status_beacon"] = "IN-POS"
        elif self.strategy_state_dict["status_code"] in [403, 404, 405, 406]:
            self.strategy_state_dict["status_beacon"] = "CLOSE-WT"



    def ready_for_next_candle(self):
        # called in update, to trigger next loop run
        now = dt.datetime.now()
        # 2 multiplied below because complete candle data is available after next candle time interval ends
        if self.config["candle_interval"] == "5minute":
            minute_delta = 2 * 5
        elif self.config["candle_interval"] == "1minute":
            minute_delta = 2 * 1
        else:
            minute_delta = 2 * 5
        last_processed_timestamp = pd.to_datetime(self.strategy_state_dict["last_processed_timestamp"])
        if last_processed_timestamp is None:
            next_candle_time = now.replace(hour=9, minute=15, second=0, microsecond=0) + dt.timedelta(minutes=minute_delta) + dt.timedelta(minutes=self.config["entry_order_wait_min"])
        else:
            next_candle_time = last_processed_timestamp + + dt.timedelta(minutes=minute_delta) + dt.timedelta(minutes=self.config["entry_order_wait_min"])

        if dt.datetime.now() >= next_candle_time:
            print(f"next candle available now:{now} candle:{next_candle_time} last:{last_processed_timestamp}")
            return True
        else:
            print(f"wait for candle now:{now} candle:{next_candle_time} last:{last_processed_timestamp}")
            return False

    def write_csv_n_json(self):
        # called in update
        #write strategy state json
        strategy_state_dict_copy = self.strategy_state_dict
        strategy_state_dict_copy["last_processed_timestamp"] = str(strategy_state_dict_copy["last_processed_timestamp"])
        save_dict_to_json_file(strategy_state_dict_copy, self.strategy_json_file_path)
        # write strategy csv logs
        add_row_to_csv(row=self.csv_log_row_list,
                       file_path=self.csv_strategy_log_file_path,
                       print_=True)

    def print_to_console(self):
        # called in update
        print_data_indicator = create_print_dict(self.nf_fut_obj,
                                                 self.nf_ce_obj,
                                                 self.nf_pe_obj,
                                                 self.bnf_fut_obj,
                                                 self.bnf_ce_obj,
                                                 self.bnf_pe_obj)
        print("current time: ", dt.datetime.now())
        print("Indicator signal/value/rank")
        print("Trading signal for: ",self.trading_security)
        pprint(print_data_indicator)
        print("-"*30, dt.datetime.now())
        print(self.nf_fut_obj.trading_symbol, "rank: ", self.nf_fut_obj.rank)
        print(pd.DataFrame(print_data_indicator["nf_fu"]))
        print("-"*30, dt.datetime.now())
        print(self.nf_ce_obj.trading_symbol, "rank: ", self.nf_ce_obj.rank)
        print(pd.DataFrame(print_data_indicator["nf_ce"]))
        print("-"*30, dt.datetime.now())
        print(self.nf_pe_obj.trading_symbol, "rank: ", self.nf_pe_obj.rank)
        print(pd.DataFrame(print_data_indicator["nf_pe"]))
        print("-"*30, dt.datetime.now())
        print(self.bnf_fut_obj.trading_symbol, "rank: ", self.bnf_fut_obj.rank)
        print(pd.DataFrame(print_data_indicator["bnf_fu"]))
        print("-"*30, dt.datetime.now())
        print(self.bnf_ce_obj.trading_symbol, "rank: ", self.bnf_ce_obj.rank)
        print(pd.DataFrame(print_data_indicator["bnf_ce"]))
        print("-"*30, dt.datetime.now())
        print(self.bnf_pe_obj.trading_symbol, "rank: ", self.bnf_pe_obj.rank)
        print(pd.DataFrame(print_data_indicator["bnf_pe"]))
        print("-" * 30, dt.datetime.now())
        pprint(self.strategy_state_dict)
        last_processed_timestamp = self.strategy_state_dict["last_processed_timestamp"]
        print(last_processed_timestamp, type(last_processed_timestamp))
        print(dt.datetime.now())
        print(dt.datetime.now())

    def initialise(self):
        print("initialising strategy object")
        self.initialise_logs_n_files()
        self._set_dataprocessor_obj()
        self._update_dataprocessor()
        self.strategy_initialised = True


    def update(self):
        try:
            if not is_market_holiday():
                if not self.strategy_initialised:
                    self.initialise()
                    self.strategy_state_dict["status_code"] = 500
                    self.print_to_console()
                else:
                    if is_market_open():
                        if self.ready_for_next_candle():
                            self._update_dataprocessor()
                            self.check_for_signal()
                            self.set_strategy_kill_switch_codes()
                            self.orders_handler()
                            self.update_last_processed_timestamp()
                            self.update_unrealised_pnl()
                            self.set_status_beacon()
                            self.write_csv_n_json()
                            self.print_to_console()
                        else:
                            print("waiting for next candle")
                            self.orders_handler()
                            sleep(20)
                    else:
                        self.strategy_state_dict["status_code"] = 102
                        self.write_csv_n_json()
                        self.print_to_console()
                        sleep_till_time(9, 15, 30)
            else:
                self.strategy_state_dict["status_code"] = 101
                self.write_csv_n_json()
                self.print_to_console()
                print("Market holiday/weekend")
                exit()
        except Exception as e:
            print(e)
            self.pull_the_plug()
            raise e
            exit()


