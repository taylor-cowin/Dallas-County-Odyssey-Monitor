#Background worker thread that pulls results from Odyssey
from datetime import datetime
import requests
import time
import mongoconnect
import logging

#Check to see if site is up and log result
def main_loop():
    logger = logging.getLogger('ody_log')
    #on first run, make sure we're starting at or near the start of the minute
    t = time.strftime('%S', datetime.now().timetuple())
    time_offset = 60-int(t)
    logger.info("Time Synchronization: Website checks will begin in " + str(time_offset) + " seconds...")
    time.sleep(time_offset)
    t = time.strftime('%H:%M:%S', datetime.now().timetuple())
    logger.info("Time synchronization complete. Beginning website check at " + t + "...")
    
    #The actual loop -- checks site once per minute
    while True:
        try:
            mongoconnect.set_result(check_site())
            time.sleep(60)
        except:
            logger.info("Couldn't set result of website check.")
def http_request():
    logger = logging.getLogger('ody_log')
    result = 'DOWN'
    try:
        r = requests.get('https://courtsportal.dallascounty.org/DALLASPROD', timeout=10)
        if r.status_code == 200:
            result = 'UP'
            return result
    except requests.exceptions.RequestException as e:
        logger.info(str(e))
        pass
        return result
    return result

def check_site():
    logger = logging.getLogger('ody_log')
    run_time = datetime.utcnow()
    logger.info("Called check_site() - about to check result. Run_time = " + str(run_time))
    result = http_request()
    logger.info(result + " at " + str(run_time))
    #Return a dict with the real results or an error result
    return {"result": result, "run_time": run_time}