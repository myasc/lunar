from strategy import Strategy
from utilsall.kite_make_connection import Kite
import config
from time import sleep

kite_obj = Kite()
kite_obj.establish_connection()

config_dict = config.config
strat_obj = Strategy(kite_obj.object, config_dict)

if __name__ == '__main__':
    try:
        strat_obj.initialise()
    except Exception as e:
        print(e)
        # raise e
    while True:
        try:
            strat_obj.update()
            sleep(60*1)
        except Exception as e:
            print(e)
            raise e
