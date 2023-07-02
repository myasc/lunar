import math


def round_to_nearest_x(current_price, x):
    return int(math.ceil(current_price / x)) * x


class StrikeSelector:
    def atm(self, current_price, tradingsymbol):
        if tradingsymbol=="BANKNIFTY":
            return round_to_nearest_x(current_price, 100)
        else:
            return round_to_nearest_x(current_price, 50)


if __name__=="__main__":
    ss = StrikeSelector()
    print(ss.atm(17249,"BANKNIFT"))


