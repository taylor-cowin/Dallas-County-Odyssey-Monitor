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
    
    while True:
        mongoconnect.set_result(check_site())
        time.sleep(60)

def check_site():
    run_time = datetime.utcnow()
    try:
        r = requests.get('https://courtsportal.dallascounty.org/DALLASPROD')
        if r.ok:
            result = 'UP'
        else:
            result = 'DOWN'
        return {"result": result, "run_time": run_time}
    except:
        return {"result": "ERROR", "run_time": run_time}
