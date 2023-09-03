import datetime as dt

now = dt.datetime.now()

for i in range(8):
    print("now: ", now, now.weekday())
    now = now + dt.timedelta(days=1)