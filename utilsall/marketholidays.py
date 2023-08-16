import pandas as pd


class MarketHolidays:
    def __init__(self, file_path):
        self.file_path = file_path
        self.holiday_dates_dt = None
        self.fetch()

    def fetch(self):
        holiday_csv = pd.read_csv(self.file_path, usecols=['Date'], parse_dates=['Date'])
        holiday_list = holiday_csv['Date'].tolist()
        self.holiday_dates_dt = [timestamp.date() for timestamp in holiday_list]
