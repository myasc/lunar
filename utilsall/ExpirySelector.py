import datetime as dt
from MarketHolidays import MarketHolidays

class ExpirySelector:
    def __init__(self):
        self.dt_now = dt.datetime.now().date()
        self.holidays = None
        self.expiry_date = None
        self.get_holidays()

    def get_holidays(self):
        marketHolidays_obj = MarketHolidays("market_holidays_2005_to_2023.csv")
        self.holidays = marketHolidays_obj.holiday_dates_dt

    def get_nearest_weekly(self):
        if self.dt_now.weekday() == 3:
            self.expiry_date = self.dt_now
        else:
            finding_date = self.dt_now
            while finding_date.weekday() != 3:
                finding_date = finding_date + dt.timedelta(days=1)
            while finding_date in self.holidays:
                finding_date = finding_date - dt.timedelta(days=1)
            self.expiry_date = finding_date

    def get_nearest_monthly(self):
        last_date_of_month = self.dt_now.replace(month=(self.dt_now.month + 1), day=1) - dt.timedelta(days=1)
        if last_date_of_month.weekday() == 3:
            self.expiry_date = last_date_of_month
        else:
            finding_date = last_date_of_month
            while finding_date.weekday() != 3:
                finding_date = finding_date - dt.timedelta(days=1)
            while finding_date in self.holidays:
                finding_date = finding_date - dt.timedelta(days=1)
            self.expiry_date = finding_date



if __name__ == "__main__":
    ES = ExpirySelector()
    # ES.dt_now = dt.date(2023, 6, 28)
    print(ES.dt_now)
    ES.get_nearest_weekly()
    print(ES.expiry_date)
    ES.get_nearest_monthly()
    print(ES.expiry_date, "type: ", type(ES.expiry_date))