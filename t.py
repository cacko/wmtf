import re
from datetime import datetime, tzinfo

CLOCK_START_PATTERN = re.compile(r"([123]\d?)/(1[012]?)\s+([01]\d):([012345]\d)", re.MULTILINE)

s = 'CLOCK OFF  alex.spasov (home)  16/11 10:02'

m = CLOCK_START_PATTERN.search(s)

day, month, hour, minute = map(int, m.groups())

d = datetime(
    year=datetime.now().year,
    month=month,
    day=day,
    hour=hour,
    minute=minute,
)
df = datetime.now() - d
print(str(df))
print(str(df).split(".")[0])