import logging
import datetime as dt


def printer_logger(logfile_suffix):
    logger_obj = logging.getLogger(__name__)
    logger_obj.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(levelname)s:%(name)s:%(asctime)s:%(message)s")
    dt_str = str(dt.datetime.now().date()).replace("-", "")[4:]
    filename = logfile_suffix + dt_str
    file_handler = logging.FileHandler(f"/Users/asc/Documents/atdv/Lunar/log_files/{filename}.log")
    file_handler.setFormatter(formatter)
    logger_obj.addHandler(file_handler)
    return logger_obj

