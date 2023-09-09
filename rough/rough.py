import datetime as dt
import math

# now = dt.datetime.now()
# print(now)
# print(str(now.date()).replace("-",""))
#
#
# file_path = '/Users/asc/Documents/atdv/lunar/csv_files/orders_20230816.csv'
# mode = 'w'
# with open(file_path, mode) as csvfile:
#     pass

now = dt.datetime.now()
open = now.replace(hour=1, minute=45, second=0, microsecond=0)
remain = open - now
print(remain)
print(remain.seconds/2)
print(math.floor(remain.seconds/2))
