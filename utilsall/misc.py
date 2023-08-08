def create_print_dict(nf_fut, nf_ce, nf_pe, bnf_fut, bnf_ce, bnf_pe):
    return {"nf_fu": {"sma": {"value": nf_fut.ti_1_value,
                              "signal": nf_fut.ti_1_signal,
                              "weight": nf_fut.ti_1_weight,
                              "enabled": nf_fut.ti_1_enabled},
                      "vwap": {"value": nf_fut.ti_2_value,
                               "signal": nf_fut.ti_2_signal,
                               "weight": nf_fut.ti_2_enabled},
                      "super": {"value": nf_fut.ti_3_value,
                                "signal": nf_fut.ti_3_signal,
                                "weight": nf_fut.ti_3_weight,
                                "enabled": nf_fut.ti_3_enabled},
                      "macd": {"value": nf_fut.ti_4_value,
                               "signal": nf_fut.ti_4_signal,
                               "weight": nf_fut.ti_4_weight,
                               "enabled": nf_fut.ti_4_enabled},
                      "stoca": {"value": nf_fut.ti_5_value,
                                "signal": nf_fut.ti_5_signal,
                                "weight": nf_fut.ti_5_weight,
                                "enabled": nf_fut.ti_5_enabled},
                      "slma1": {"value": nf_fut.ti_1_sl_value,
                                "signal": None,
                                "weight": None,
                                "enabled": None},
                      "slma2": {"value": nf_fut.ti_2_sl_value,
                                "signal": None,
                                "weight": None,
                                "enabled": None},
                      "slma3": {"value": nf_fut.ti_3_sl_value,
                                "signal": None,
                                "weight": None,
                                "enabled": None},
                      "level": {"value": nf_fut.level_value,
                                "signal": nf_fut.level_signal,
                                "weight": nf_fut.level_weight,
                                "enabled": None},
                      "rank": nf_fut.rank,
                      "last_close_price": nf_fut.last_close_price,
                      "data_start_datetime": nf_fut.data_start_datetime,
                      "data_end_datetime": nf_fut.data_end_datetime,
                      },
            "nf_ce": {"sma": {"value": nf_ce.ti_1_value,
                              "signal": nf_ce.ti_1_signal,
                              "weight": nf_ce.ti_1_weight,
                              "enabled": nf_ce.ti_1_enabled},
                      "vwap": {"value": nf_ce.ti_2_value,
                               "signal": nf_ce.ti_2_signal,
                               "weight": nf_ce.ti_2_weight,
                               "enabled": nf_ce.ti_2_enabled},
                      "super": {"value": nf_ce.ti_3_value,
                                "signal": nf_ce.ti_3_signal,
                                "weight": nf_ce.ti_3_weight,
                                "enabled": nf_ce.ti_3_enabled},
                      "macd": {"value": nf_ce.ti_4_value,
                               "signal": nf_ce.ti_4_signal,
                               "weight": nf_ce.ti_4_weight,
                               "enabled": nf_ce.ti_4_enabled},
                      "stoca": {"value": nf_ce.ti_5_value,
                                "signal": nf_ce.ti_5_signal,
                                "weight": nf_ce.ti_5_weight,
                                "enabled": nf_ce.ti_5_enabled},
                      "slma1": {"value": nf_ce.ti_1_sl_value,
                                "signal": None,
                                "weight": None,
                                "enabled": None},
                      "slma2": {"value": nf_ce.ti_2_sl_value,
                                "signal": None,
                                "weight": None,
                                "enabled": None},
                      "slma3": {"value": nf_ce.ti_3_sl_value,
                                "signal": None,
                                "weight": None,
                                "enabled": None},
                      "level": {"value": nf_ce.level_value,
                                "signal": nf_ce.level_signal,
                                "weight": nf_ce.level_weight,
                                "enabled": None},
                      "rank": nf_ce.rank,
                      "last_close_price": nf_ce.last_close_price,
                      "data_start_datetime": nf_ce.data_start_datetime,
                      "data_end_datetime": nf_ce.data_end_datetime,
                      },
            "nf_pe": {"sma": {"value": nf_pe.ti_1_value,
                              "signal": nf_pe.ti_1_signal,
                              "weight": nf_pe.ti_1_weight,
                              "enabled": nf_pe.ti_1_enabled},
                      "vwap": {"value": nf_pe.ti_2_value,
                               "signal": nf_pe.ti_2_signal,
                               "weight": nf_pe.ti_2_weight,
                               "enabled": nf_pe.ti_2_enabled},
                      "super": {"value": nf_pe.ti_3_value,
                                "signal": nf_pe.ti_3_signal,
                                "weight": nf_pe.ti_3_weight,
                                "enabled": nf_pe.ti_3_enabled},
                      "macd": {"value": nf_pe.ti_4_value,
                               "signal": nf_pe.ti_4_signal,
                               "weight": nf_pe.ti_4_weight,
                               "enabled": nf_pe.ti_4_enabled},
                      "stoca": {"value": nf_pe.ti_5_value,
                                "signal": nf_pe.ti_5_signal,
                                "weight": nf_pe.ti_5_weight,
                                "enabled": nf_pe.ti_5_enabled},
                      "slma1": {"value": nf_pe.ti_1_sl_value,
                                "signal": None,
                                "weight": None,
                                "enabled": None},
                      "slma2": {"value": nf_pe.ti_2_sl_value,
                                "signal": None,
                                "weight": None,
                                "enabled": None},
                      "slma3": {"value": nf_pe.ti_3_sl_value,
                                "signal": None,
                                "weight": None,
                                "enabled": None},
                      "level": {"value": nf_pe.level_value,
                                "signal": nf_pe.level_signal,
                                "weight": nf_pe.level_weight,
                                "enabled": None},
                      "rank": nf_pe.rank,
                      "last_close_price": nf_pe.last_close_price,
                      "data_start_datetime": nf_pe.data_start_datetime,
                      "data_end_datetime": nf_pe.data_end_datetime,
                      },
            "bnf_fut": {"sma": {"value": bnf_fut.ti_1_value,
                              "signal": bnf_fut.ti_1_signal,
                              "weight": bnf_fut.ti_1_weight,
                              "enabled": bnf_fut.ti_1_enabled},
                      "vwap": {"value": bnf_fut.ti_2_value,
                               "signal": bnf_fut.ti_2_signal,
                               "weight": bnf_fut.ti_2_weight,
                               "enabled": bnf_fut.ti_2_enabled},
                      "super": {"value": bnf_fut.ti_3_value,
                                "signal": bnf_fut.ti_3_signal,
                                "weight": bnf_fut.ti_3_weight,
                                "enabled": bnf_fut.ti_3_enabled},
                      "macd": {"value": bnf_fut.ti_4_value,
                               "signal": bnf_fut.ti_4_signal,
                               "weight": bnf_fut.ti_4_weight,
                               "enabled": bnf_fut.ti_4_enabled},
                      "stoca": {"value": bnf_fut.ti_5_value,
                                "signal": bnf_fut.ti_5_signal,
                                "weight": bnf_fut.ti_5_weight,
                                "enabled": bnf_fut.ti_5_enabled},
                      "slma1": {"value": bnf_fut.ti_1_sl_value,
                                "signal": None,
                                "weight": None,
                                "enabled": None},
                      "slma2": {"value": bnf_fut.ti_2_sl_value,
                                "signal": None,
                                "weight": None,
                                "enabled": None},
                      "slma3": {"value": bnf_fut.ti_3_sl_value,
                                "signal": None,
                                "weight": None,
                                "enabled": None},
                      "level": {"value": bnf_fut.level_value,
                                "signal": bnf_fut.level_signal,
                                "weight": bnf_fut.level_weight,
                                "enabled": None},
                      "rank": bnf_fut.rank,
                      "last_close_price": bnf_fut.last_close_price,
                      "data_start_datetime": bnf_fut.data_start_datetime,
                      "data_end_datetime": bnf_fut.data_end_datetime,
                      },
            "bnf_ce": {"sma": {"value": bnf_ce.ti_1_value,
                              "signal": bnf_ce.ti_1_signal,
                              "weight": bnf_ce.ti_1_weight,
                              "enabled": bnf_ce.ti_1_enabled},
                      "vwap": {"value": bnf_ce.ti_2_value,
                               "signal": bnf_ce.ti_2_signal,
                               "weight": bnf_ce.ti_2_weight,
                               "enabled": bnf_ce.ti_2_enabled},
                      "super": {"value": bnf_ce.ti_3_value,
                                "signal": bnf_ce.ti_3_signal,
                                "weight": bnf_ce.ti_3_weight,
                                "enabled": bnf_ce.ti_3_enabled},
                      "macd": {"value": bnf_ce.ti_4_value,
                               "signal": bnf_ce.ti_4_signal,
                               "weight": bnf_ce.ti_4_weight,
                               "enabled": bnf_ce.ti_4_enabled},
                      "stoca": {"value": bnf_ce.ti_5_value,
                                "signal": bnf_ce.ti_5_signal,
                                "weight": bnf_ce.ti_5_weight,
                                "enabled": bnf_ce.ti_5_enabled},
                      "slma1": {"value": bnf_ce.ti_1_sl_value,
                                "signal": None,
                                "weight": None,
                                "enabled": None},
                      "slma2": {"value": bnf_ce.ti_2_sl_value,
                                "signal": None,
                                "weight": None,
                                "enabled": None},
                      "slma3": {"value": bnf_ce.ti_3_sl_value,
                                "signal": None,
                                "weight": None,
                                "enabled": None},
                      "level": {"value": bnf_ce.level_value,
                                "signal": bnf_ce.level_signal,
                                "weight": bnf_ce.level_weight,
                                "enabled": None},
                      "rank": bnf_ce.rank,
                      "last_close_price": bnf_ce.last_close_price,
                      "data_start_datetime": bnf_ce.data_start_datetime,
                      "data_end_datetime": bnf_ce.data_end_datetime,
                      },
            "bnf_pe": {"sma": {"value": bnf_pe.ti_1_value,
                              "signal": bnf_pe.ti_1_signal,
                              "weight": bnf_pe.ti_1_weight,
                              "enabled": bnf_pe.ti_1_enabled},
                      "vwap": {"value": bnf_pe.ti_2_value,
                               "signal": bnf_pe.ti_2_signal,
                               "weight": bnf_pe.ti_2_weight,
                               "enabled": bnf_pe.ti_2_enabled},
                      "super": {"value": bnf_pe.ti_3_value,
                                "signal": bnf_pe.ti_3_signal,
                                "weight": bnf_pe.ti_3_weight,
                                "enabled": bnf_pe.ti_3_enabled},
                      "macd": {"value": bnf_pe.ti_4_value,
                               "signal": bnf_pe.ti_4_signal,
                               "weight": bnf_pe.ti_4_weight,
                               "enabled": bnf_pe.ti_4_enabled},
                      "stoca": {"value": bnf_pe.ti_5_value,
                                "signal": bnf_pe.ti_5_signal,
                                "weight": bnf_pe.ti_5_weight,
                                "enabled": bnf_pe.ti_5_enabled},
                      "slma1": {"value": bnf_pe.ti_1_sl_value,
                                "signal": None,
                                "weight": None,
                                "enabled": None},
                      "slma2": {"value": bnf_pe.ti_2_sl_value,
                                "signal": None,
                                "weight": None,
                                "enabled": None},
                      "slma3": {"value": bnf_pe.ti_3_sl_value,
                                "signal": None,
                                "weight": None,
                                "enabled": None},
                      "level": {"value": bnf_pe.level_value,
                                "signal": bnf_pe.level_signal,
                                "weight": bnf_pe.level_weight,
                                "enabled": None},
                      "rank": bnf_pe.rank,
                      "last_close_price": bnf_pe.last_close_price,
                      "data_start_datetime": bnf_pe.data_start_datetime,
                      "data_end_datetime": bnf_pe.data_end_datetime,
                      }
            }