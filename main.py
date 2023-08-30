from strategy import Strategy
from utilsall.kite_make_connection import Kite
import config
from time import sleep

kite_obj = Kite()
kite_obj.establish_connection()

config_dict = config.config
strat_obj = Strategy(kite_obj.object, config_dict, testing=True)

if __name__ == '__main__':
    try:
        strat_obj.initialise()
        print("__class__", __name__, "main initialised")
    except Exception as e:
        print(e)
        raise e
    while True:
        try:
            strat_obj.update()
            print("__class__", __name__, "main updated")
            sleep(60*1)
        except Exception as e:
            print(e)
            raise e
