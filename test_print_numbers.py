from utilsall.kite_make_connection import Kite
from strategy import Strategy
import config_nf
from time import sleep
from pprint import pprint
import warnings
import pandas as pd
pd.set_option("display.max_columns", None)
pd.set_option('display.width', 200)
warnings.filterwarnings("ignore")

kite_obj = Kite()
kite_obj.establish_connection()

strat = Strategy(kite_obj.object, config1.config)
strat._set_dataprocessor_obj()
strat.print_to_console()
while True:
    strat._update_dataprocessor()
    strat.print_to_console()
    sleep(5*1)

