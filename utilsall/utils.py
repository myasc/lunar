import csv
import os
import logging
import datetime as dt
from utilsall.expiryselector import ExpirySelector
from utilsall.fnocontractselector import FNOContractSelector
import json


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
        es.get_nearest_weekly()
        expiry_date = es.expiry_date
    else:
        raise Exception(f"Invalid instrument {instrument}")

    cs = FNOContractSelector(kite_obj, underlying, expiry_date, instrument, strike)
    id_ = cs.get_instrument_id()
    return id_


def logger_intialise(logfile_suffix):
    logger_obj = logging.getLogger(__name__)
    logger_obj.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(levelname)s:%(name)s:%(asctime)s:%(message)s")
    dt_str = str(dt.datetime.now()).replace(" ", "_").replace("-", "").replace(":", "").split(".")[0]
    filename = logfile_suffix + dt_str
    file_handler = logging.FileHandler(f"/Users/asc/Documents/atdv/lunar/log_files/{filename}.log")
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
    # todo this throws error sometimes filenotfoounderror, create emtpy file not working
    mode = 'a' if os.path.exists(file_path) else 'w'
    if mode == 'a':
        with open(file_path, mode, newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(row)
    else:
        with open(file_path, mode) as csvfile:
            pass
    if print_:
        print("added to csv: " + str(row))


def init_csv_logger(filename):
    dt_str = str(dt.datetime.now().date()).replace("-", "")[4:]
    # filename = str(self.event_id) + str(self.strategy_no) + dt_str
    csvlog_filepath = f"csv_logs/{filename}.csv"
    first_row = ['datetime', 'price', 'qty']
    add_row_to_csv(first_row, csvlog_filepath)


def save_dict_to_json_file(dictionary, json_file_path):
    # todo this function sometime doesn't add '}]' at end of jsonfile if error raised
    dictionary["loggedat"] = str(dt.datetime.now().isoformat())
    if not os.path.exists(json_file_path):
        with open(json_file_path, "w") as json_file:
            json_file.write("[]")

    with open(json_file_path, "r+") as json_file:
        data = json.load(json_file)
        data.append(dictionary)
        json_file.seek(0)
        json.dump(data, json_file)


def get_latest_json_dict(json_file_path):
    if not os.path.exists(json_file_path):
        return {}
    else:
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)
        latest_timestamp = dt.datetime.fromisoformat(data[0]["loggedat"])
        latest_dict = data[0]
        if len(data) > 1:
            for dict_ in data:
                timestamp = dt.datetime.fromisoformat(dict_["loggedat"])
                if timestamp > latest_timestamp:
                    latest_timestamp = timestamp
                    latest_dict = dict_

        return latest_dict
