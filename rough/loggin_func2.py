# from logging_func import printer_logger
#
# logger = printer_logger("logtest")
# logger.info("test1")

import datetime as dt
print(dt.datetime.now())
print(str(dt.datetime.now()).replace(" ", "_").replace("-", "").replace(":", "").split(".")[0])

import logging

