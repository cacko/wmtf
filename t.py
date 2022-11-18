from datetime import datetime, timedelta
from time import sleep

s = "1:05"

h, m = [int(x) for x in s.split(":")]

td = timedelta(hours=h, minutes=m)



r = RunningTime(s)  
    
for x in range(3):
    print(r)
    sleep(10)