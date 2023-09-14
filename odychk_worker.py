#Background worker - logs results from Odyssey
import logging
from logging.handlers import RotatingFileHandler
import time
from datetime import datetime
from pymongo import MongoClient
import mongoconnect

import requests

#make an offset variable for ongoing time synchronization
seconds_offset = 0

#Global variables for downtime records
downtime_start = None
downtime_end = None

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
            set_bulk_result(check_ody_online())
            #Sleep until the top of the next minute
            sleep_amount = 60-int(seconds_offset)
            logger.debug("Sleeping for %s seconds", str(sleep_amount))
            time.sleep(sleep_amount)
        except Exception as exception:
            logger.critical("Couldn't set result of website check. Check database connection. Cause: %s", exception)

#See if the website is up (i.e. returns 200 w/in timeout period)
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
    logger.debug("Seconds offset: %s", seconds_offset)
    return result

#connect to the database
def bulk_db_connect(): #returns "results" collection
    dbclient = MongoClient()
    database = dbclient["odychk"]
    return database["results"] #returns the collection

def set_bulk_result(result_dict):
    bulk_db_connect().insert_one({"run_time": result_dict["run_time"], "result": result_dict["result"]})
    return

def log_downtime():
    #Calculate downtime:
    global downtime_end
    global downtime_start
    total_downtime = downtime_end - downtime_start
    #WRITE TO DB
    logger.info("Outage finished. Start: %s, Finish: %s, Length: %s.", downtime_start, downtime_end, total_downtime )
    #RESET VARS
    downtime_start = None
    downtime_end = None
    return

def outage_handler(_result, _run_time):
    global downtime_start
    #If the site is up, check to see if it was previously down. Log if so, because outage is complete
    if _result == "UP" or _result == "U" or _result == 1:
        if downtime_start is not None:
            log_downtime()
    #If site is down, either ignore (if ongoing) or log to file (if new)
    if _result == "DOWN" or _result == "D" or _result == 0:
        if downtime_start is None:
            downtime_start = _run_time
            logger.info("Downtime detected: %s", downtime_start)
        else:
            logger.debug("Ongoing outage at %s.", _run_time)
    return

def check_ody_online():
    run_time = datetime.utcnow()
    result = http_request()
    logger.debug("Website is %s at %s", result, str(run_time))
    #Pass to the outage handler to see if we're having an outage and act accordingly
    outage_handler(result, run_time)
    return {"result": result, "run_time": run_time}

#See if we're starting up the app mid-outage. Not strictly a "crash," but the worker should never really be down unless the system goes down
def crash_checker():
    logger.info("Checking to see if an outage was pending during downtime...")
    last_entry = mongoconnect.get_latest()
    logger.debug("Last entry: %s", str(last_entry))
    #Check for last entry being down at startup. This would imply that the worker went down during an outage and needs to scoop up the earlier data to resume counting
    #Potential problem -- might be unrecorded uptime while the worker was down. How to handle?
    #TODO think through these edge cases
    #TODO RESTRUCTURE THIS LOGIC -- NONSENSE CURRENTLY
    if last_entry["result"] == "DOWN" or last_entry["result"] == "D" or last_entry["result"] == 0:
        logger.info("Outage detected at startup. Rebuilding outage from old data...")
        last_down = mongoconnect.get_last_down()
        logger.info("Last logged \"Down\" entry: %s at %s", last_down["result"], last_down["run_time"])
        last_logged_outage = mongoconnect.get_last_outage()
        #If the last DOWN was after the last logged outage start time, then we started the script during an unlogged outage
        if last_down is not None and last_logged_outage is not None:
            if last_logged_outage["start_time"] < last_down["run_time"]:
                end_time = last_down["run_time"]
    else:
        logger.debug("No crash detected. Continuing...")
    return

if __name__ == "__main__":
    logger = logging.getLogger('ody_log')
    init_logger()
    crash_checker()
    main_loop()