from datetime import datetime
import requests
import time
import mongoconnect

 #Check to see if site is up and log result
def main_loop():
    while True:
        mongoconnect.set_result(check_site())
        time.sleep(60)

def check_site():
    run_time = time.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%SZ")
    try:
        r = requests.get('https://courtsportal.dallascounty.org/DALLASPROD')
        if r.ok:
            result = 'UP'
        else:
            result = 'DOWN'
        return {"result": result, "run_time": run_time}
    except:
        return {"result": "ERROR", "run_time": run_time}