from utilsall.ExpirySelector import ExpirySelector
from utilsall.fnocontractselector import FNOContractSelector

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

