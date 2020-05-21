import datetime as dt
import time

tq1 = dt.datetime.now()

time.sleep(90)

tq2 = dt.datetime.now()

print((tq2-tq1).total_seconds())