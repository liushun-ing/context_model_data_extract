from dateutil.parser import parse
from datetime import timezone

test = '2010-08-05 09:13:50.927 +5:00'

dt = parse(test)
print(dt)

print(dt.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'))

rfc_timezones = {
    'CET': '+1:00',
    'CDT': '-5:00',
    'CEST': '+2:00',
    'COT': '-5:00',
    'PET': '-5:00',
    'IST': '+5:30',
    'CST': '+10:30',
    'BST': '+6:00',
    'GMT': '+8:00',
    'PDT': '-7:00',
    'PST': '-8:00',
    'EET': '+2:00'
}
