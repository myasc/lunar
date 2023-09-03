import pandas as pd
from utilsall.testprint import test_prints

class MarketHolidays:
    def __init__(self, file_path):
        self.file_path = file_path
        self.holiday_dates_dt = None
        self.fetch()
        test_prints(f"{__class__.__name__}, object created")

    def fetch(self):
        holiday_csv = pd.read_csv(self.file_path, usecols=['Date'], parse_dates=['Date'])
        holiday_list = holiday_csv['Date'].tolist()
        self.holiday_dates_dt = [timestamp.date() for timestamp in holiday_list]
        test_prints(f"{__class__.__name__}, read holidays as timestamp")

