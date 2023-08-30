import logging
import datetime as dt
import os
from utilsall.misc import reach_project_dir


def printer_logger(logfile_suffix):
    logger_obj = logging.getLogger(__name__)
    logger_obj.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(levelname)s:%(name)s:%(asctime)s:%(message)s")
    dt_str = str(dt.datetime.now().date()).replace("-", "")[4:]
    filename = logfile_suffix + dt_str
    pwd = os.getcwd()
    reach_project_dir()
    file = f"/log_files/{filename}.log"
    file_handler = logging.FileHandler(file)
    os.chdir(pwd)
    file_handler.setFormatter(formatter)
    logger_obj.addHandler(file_handler)
    return logger_obj

