from sqlite3 import Time
from time import time
import requests
import datetime

r = requests.get('https://courtsportal.dallascounty.org/DALLASPROD')

if r.ok:
    result = 'UP'
    text_color = '#66CD00'
else:
    result = 'DOWN'
    text_color = '#FF3030'

result_string = 'Dallas County Odyssey is currently: ' + result
print(result_string)

last_run_time = datetime.datetime.now() #use JS to do the math in browser
print(last_run_time)