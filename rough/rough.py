import datetime as dt

now = dt.datetime.now()
print(now)
print(str(now.date()).replace("-",""))


file_path = '/Users/asc/Documents/atdv/lunar/csv_files/orders_20230816.csv'
mode = 'w'
with open(file_path, mode) as csvfile:
    pass