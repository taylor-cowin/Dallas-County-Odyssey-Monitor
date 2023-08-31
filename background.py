#Background worker thread that pulls results from Odyssey
import logging
import time
from datetime import datetime

import requests

import mongoconnect


#Check to see if site is up and log result
def main_loop():
    logger = logging.getLogger('ody_log')
    #on first run, make sure we're starting at or near the start of the minute
    time_now = time.strftime('%S', datetime.now().timetuple())
    time_offset = 60-int(time_now)
    logger.debug("Time Synchronization: Website checks will begin in %s seconds...", str(time_offset))
    time.sleep(time_offset)
    time_now = time.strftime('%H:%M:%S', datetime.now().timetuple())
    logger.debug("Time synchronization complete. Beginning website check at %s...", time_now)
    #The actual loop -- checks site once per minute
    while True:
        try:
            mongoconnect.set_result(check_site())
            time.sleep(60)
        except Exception as exception:
            logger.critical("Couldn't set result of website check. Check database connection. Cause: %s", exception)

#See if the website is up
def http_request():
    #Default to down
    result = 'DOWN'
    try:
        #App was failing to return due to website failing to timeout -- do not remove timeout clause
        r = requests.get('https://courtsportal.dallascounty.org/DALLASPROD', timeout=10)
        if r.status_code == 200:
            result = 'UP'
    #This is the most common path -- website is typically 200 or error
    except requests.exceptions.RequestException:
        pass
    return result

def check_site():
    logger = logging.getLogger('ody_log')
    run_time = datetime.utcnow()
    result = http_request()
    logger.info("Website is %s at %s", result, str(run_time))
    return {"result": result, "run_time": run_time}
