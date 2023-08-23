import datetime as dt

config = {"program_trade_live": True,
          "program_start_time": dt.time(9, 30),
          "program_exit_time": dt.time(15, 15),
          "candle_interval": "5minute",
          "future_max_prev_days": 90,
          "options_max_prev_days": 60,
          "max_trades_per_day": 3,
          "max_stoploss_per_day": 2,
          "num_of_sets": 1, # quantity is decided based on lotsperset not numofsets
          "lots_per_set": 3,
          "option_buy_underlying": "NIFTY",
          "nifty_strike_ce": 19400,
          "nifty_strike_pe": 19400,
          "banknifty_strike_ce": 44200,
          "banknifty_strike_pe": 44200,
          "nifty_level_up": 19500,
          "nifty_level_down": 19300,
          "banknifty_level_up": 44300,
          "banknifty_level_down": 44100,
          "ti_1_sl_config": 10,
          "ti_2_sl_config": 15,
          "ti_3_sl_config": 20,
          "ti_1_config": 20,
          "ti_2_config": "VWAP",
          "ti_3_config": [7, 3],
          "ti_4_config": [12, 26, 9],
          "ti_5_config": 14,
          "ti_1_rank": 5,
          "ti_2_rank": 15,
          "ti_3_rank": 20,
          "ti_4_rank": 20,
          "ti_5_rank": 20,
          "future_levels_rank": 20,
          "ti_enabled_list": [1,2, 3, 4,5],
          "intraday_algo": True,
          "first_lot_exit": 15,  # if set is of 3 then exit 1 lot here
          "second_lot_exit": 30,  # if set is of 3 then exit 1 lot here
          "final_exit": "ind_sl",  # [based on technical indicator]
          "global_sl": 45,  # [odd events]
          "entry_order_wait_min": 2,  # min (this is after valid signal)
          "entry_order_valid_min": 3  # wait time for order fill
          }
