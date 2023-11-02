from strategy import Strategy
from utilsall.kite_make_connection import Kite
import config_nf
import config_bnf
from time import sleep

kite_obj = Kite()
kite_obj.establish_connection()

config_dict_nf = config_nf.config
strat_obj_nf = Strategy(kite_obj.object, config_dict_nf, testing=False)

config_dict_bnf = config_bnf.config
strat_obj_bnf = Strategy(kite_obj.object, config_dict_bnf, testing=True)

if __name__ == '__main__':
    while True:
        try:
            strat_obj_nf.update()
            # strat_obj_bnf.update()
            print("__class__", __name__, "main updated")
            # sleep(60*1)
        except Exception as e:
            print(e)
            raise e
