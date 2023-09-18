import csv
import math
import os
import logging
import datetime as dt
import time

from utilsall.expiryselector import ExpirySelector
from utilsall.fnocontractselector import FNOContractSelector
from utilsall.marketholidays import MarketHolidays
import json

from utilsall.misc import reach_project_dir


def fetch_instru_token(kite_obj, underlying, strike, instrument):
    """
    :param kite_obj: Kite connect connection object
    :param underlying: all caps e.g. NIFTY, BANKNIFTY
    :param strike: strike price if options else None
    :param instrument: FUT for future and CE/PE for options
    :return: instrument id
    """
    es = ExpirySelector()
    if instrument == "FUT":
        es.get_nearest_monthly()
        expiry_date = es.expiry_date
    elif (instrument == "CE") or (instrument == "PE"):
        if underlying == "BANKNIFTY":
            es.get_nearest_weekly(expiry_weekday=2)
        else:
            es.get_nearest_weekly(expiry_weekday=3)
        expiry_date = es.expiry_date
    else:
        raise Exception(f"Invalid instrument {instrument}")

    cs = FNOContractSelector(kite_obj, underlying, expiry_date, instrument, strike)
    id_ = cs.get_instrument_id()
    print(id_)
    return id_


def logger_intialise(logfile_suffix):
    logger_obj = logging.getLogger(__name__)
    logger_obj.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(levelname)s:%(name)s:%(asctime)s:%(message)s")
    dt_str = str(dt.datetime.now()).replace(" ", "_").replace("-", "").replace(":", "").split(".")[0]
    filename = logfile_suffix + dt_str
    pwd = os.getcwd()
    reach_project_dir()
    file = f"log_files/{filename}.log"
    file_handler = logging.FileHandler(file)
    os.chdir(pwd)
    file_handler.setFormatter(formatter)
    logger_obj.addHandler(file_handler)
    return logger_obj


def printer_logger(mssg, logger, loglevel="info", print_=False):
    if print_:
        print(mssg)

    if loglevel == "info":
        logger.info(mssg)
    elif loglevel == "debug":
        logger.debug(mssg)
    elif loglevel == "error":
        logger.error(mssg)
    elif loglevel == "critical":
        logger.critical(mssg)
    elif loglevel == "exception":
        logger.exception(mssg)


def add_row_to_csv(row, file_path, print_=False):
    timestamp = str(dt.datetime.now().isoformat())
    row.append(timestamp)
    pwd = os.getcwd()
    reach_project_dir()
    mode = 'a' if os.path.exists(file_path) else 'w'
    if mode == 'a':
        with open(file_path, mode, newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(row)
    else:
        with open(file_path, mode) as csvfile:
            pass
    if print_:
        print(f"added to csv: {file_path}: " + str(row))
    os.chdir(pwd)


def init_csv_logger(filename):
    dt_str = str(dt.datetime.now().date()).replace("-", "")[4:]
    # filename = str(self.event_id) + str(self.strategy_no) + dt_str
    pwd = os.getcwd()
    reach_project_dir()
    csvlog_filepath = f"csv_files/{filename}.csv"
    first_row = ['datetime', 'price', 'qty']
    add_row_to_csv(first_row, csvlog_filepath)
    os.chdir(pwd)


def save_dict_to_json_file(dictionary, json_file_path):
    # todo this function sometime doesn't add '}]' at end of jsonfile if error raised
    dictionary["loggedat"] = str(dt.datetime.now().isoformat())
    pwd = os.getcwd()
    reach_project_dir()
    if not os.path.exists(json_file_path):
        with open(json_file_path, "w") as json_file:
            json_file.write("[]")

    with open(json_file_path, "r+") as json_file:
        data = json.load(json_file)
        data.append(dictionary)
        json_file.seek(0)
        json.dump(data, json_file)
    print(f"added to json: {json_file_path}: " + str(dictionary))
    os.chdir(pwd)



def get_latest_json_dict(json_file_path):
    pwd = os.getcwd()
    reach_project_dir()
    if not os.path.exists(json_file_path):
        os.chdir(pwd)
        print(f"read from json: {json_file_path}: " + "{}")
        return {}
    else:
        with open(json_file_path, "r") as json_file:
            data = json.loads(json_file.read())
        if len(data) > 1:
            latest_timestamp = dt.datetime.fromisoformat(data[0]["loggedat"])
            latest_dict = data[0]
            for dict_ in data:
                timestamp = dt.datetime.fromisoformat(dict_["loggedat"])
                if timestamp > latest_timestamp:
                    latest_timestamp = timestamp
                    latest_dict = dict_
        else:
            latest_dict = {}
        os.chdir(pwd)
        print(f"read from json: {json_file_path}: {latest_dict}")
        return latest_dict

def get_holidays():
    pwd = os.getcwd()
    reach_project_dir()
    file = "utilsall/market_holidays_2005_to_2023.csv"
    market_holidays_obj = MarketHolidays(file)
    os.chdir(pwd)
    return market_holidays_obj.holiday_dates_dt

def is_market_holiday():
    now = dt.datetime.now()
    if now.date() in get_holidays():
        print(f"market holiday {now}")
        return True
    elif now.weekday() in [5, 6]:
        print(f"market weekend {now} weekday:{now.weekday()}")
        return True
    else:
        return False

def is_market_open():
    now = dt.datetime.now()
    # now = dt.datetime(2023, 9, 17, 10, 0)
    market_opentime = dt.datetime(year=now.year, month=now.month,day=now.day, hour=9, minute=15)
    market_closetime = dt.datetime(year=now.year, month=now.month,day=now.day, hour=15, minute=30)
    if now.date() in get_holidays():
        print(f"market holiday {now}")
        return False
    elif now.weekday() in [5, 6]:
        print(f"market weekend {now} weekday:{now.weekday()}")
        return False
    elif (now >= market_opentime) and (now < market_closetime):
        print(f"market now open {now} weekday:{now.weekday()}")
        return True
    else:
        print(f"market now closed {now} weekday:{now.weekday()}")
        return False

def sleep_till_time(hour, minute, quick_check_at_secs=30):
    now = dt.datetime.now()
    open = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if open >= now:
        remain = (open - now).seconds
        if remain >= quick_check_at_secs:
            sleep_sec = math.floor(remain/2)
        else:
            sleep_sec = 5
        print(f"sleeping secs:{sleep_sec} now:{now} till:{open}")
        time.sleep(sleep_sec)
    else:
        pass
