from sqlite3 import Time
from time import time
import requests
import datetime

def check_site():
    r = requests.get('https://courtsportal.dallascounty.org/DALLASPROD')

    if r.ok:
        result = 'UP'
    else:
        result = 'DOWN'

    last_run_time = datetime.datetime.now()
    return result, last_run_time

def create_page(result, last_run_time):
    result_string = 'Dallas County Odyssey is currently: ' + result
    if result == 'UP':
        text_color = '#FF3030'
    else:
        text_color = '#FF3030'
    print(result_string)
    print(text_color)
    print(last_run_time)

result, last_run_time = check_site()
create_page(result, last_run_time)
    