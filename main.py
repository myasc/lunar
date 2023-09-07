from strategy import Strategy
from utilsall.kite_make_connection import Kite
import config1
import config2
from time import sleep

kite_obj = Kite()
kite_obj.establish_connection()

config_dict1 = config1.config
strat_obj1 = Strategy(kite_obj.object, config_dict1, testing=True)

config_dict2 = config2.config
strat_obj2 = Strategy(kite_obj.object, config_dict2, testing=True)

if __name__ == '__main__':
    try:
        strat_obj1.initialise()
        strat_obj2.initialise()
        print("__class__", __name__, "main initialised")
    except Exception as e:
        print(e)
        raise e
    while True:
        try:
            strat_obj1.update()
            strat_obj2.update()
            print("__class__", __name__, "main updated")
            sleep(60*1)
        except Exception as e:
            print(e)
            raise e
