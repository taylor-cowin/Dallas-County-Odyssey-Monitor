#Background worker - logs results from Odyssey
import logging
from logging.handlers import RotatingFileHandler
import time
from datetime import datetime
from pymongo import MongoClient

import requests

#make an offset variable for ongoing time synchronization
seconds_offset = 0

def init_logger():
    log_formatter = (
        logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
        )  
    log_handler = (
        RotatingFileHandler('odychk_worker.log',
                            encoding=None,
                            delay=False,
                            errors=None,
                            maxBytes=1024*25,
                            backupCount=10)
    )
    log_handler.setFormatter(log_formatter)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(log_handler)
    logger.info("Initialized logger...")

def main_loop():
    #on first run, make sure we're starting at or near the start of the minute
    time_now = time.strftime('%S', datetime.now().timetuple())
    time_offset = 60-int(time_now)
    logger.info("Time Synchronization: Website checks will begin in %s seconds...", str(time_offset))
    time.sleep(time_offset)
    time_now = time.strftime('%H:%M:%S', datetime.now().timetuple())
    logger.info("Time synchronization complete. Beginning website check at %s...", time_now)
    
    #The actual loop -- checks site once per minute
    while True:
        try:
            set_result(check_site())
            #Sleep until the top of the next minute
            sleep_amount = 60-int(seconds_offset)
            logger.debug("Sleeping for %s seconds", str(sleep_amount))
            time.sleep(sleep_amount)
        except Exception as exception:
            logger.critical("Couldn't set result of website check. Check database connection. Cause: %s", exception)

#See if the website is up
def http_request():
    #Default to down
    result = 'DOWN'
    try:
        #App was failing to return due to website failing to timeout -- do not remove timeout clause
        request = requests.get('https://courtsportal.dallascounty.org/DALLASPROD', timeout=10)
        if request.status_code == 200:
            result = 'UP'
    #This is the most common path for detecting down-- website is typically 200 or error
    except requests.exceptions.RequestException:
        pass
    global seconds_offset
    seconds_offset = time.strftime('%S', datetime.now().timetuple())
    logger.debug("Seconds offset: %s", str(seconds_offset))
    return result

#connect to the database
def db_connect():
    dbclient = MongoClient()
    database = dbclient["odychk"]
    return database["results"] #returns the collection

def set_result(result_dict):
    db_connect().insert_one({"run_time": result_dict["run_time"], "result": result_dict["result"]})
    return

def check_site():
    run_time = datetime.utcnow()
    result = http_request()
    logger.info("Website is %s at %s", result, str(run_time))
    return {"result": result, "run_time": run_time}

if __name__ == "__main__":
    logger = logging.getLogger('ody_log')
    init_logger()
    main_loop()