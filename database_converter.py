import logging
from logging.handlers import RotatingFileHandler
from datetime import timedelta

from pymongo import MongoClient

def db_connect_bulk():
    dbclient = MongoClient()
    db = dbclient["odychk"]
    col = db["results"]
    return col

#Connector for the outage DB
def db_connect_outage():
    dbclient = MongoClient()
    db = dbclient["odychk"]
    col = db["outages"]
    return col

def init_logger():
    log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
    log_handler = RotatingFileHandler('db_conversion.log', encoding=None, delay=False, errors=None, maxBytes=1024*25, backupCount=10)
    log_handler.setFormatter(log_formatter)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(log_handler) 

def delete_old_outages():
    outage = db_connect_outage().find({})
    outage_list = list(outage)
    try:
        logger.info("Deleting previous outage entries...")
        db_connect_outage().delete_many({})
        logger.info("Deleted %i entries...", len(outage_list))
    except:
        logger.info("No outages detected. Proceeding with outage creation...")

#Defaults
start_time = None
end_time = None
total_time = None

def update_outages():
    global start_time
    global end_time
    global total_time

    logger.info("Updating outage -- Start: %s; End: %s; Total time: %s", start_time, end_time, total_time)


    db_connect_outage().insert_one({"start_time": start_time, "end_time": end_time, "total_time": total_time.seconds})

    #Reset variables at the end
    start_time = None
    end_time = None
    total_time = None

def calculate_outages():
    global start_time
    global end_time
    global total_time

    all_results = list(db_connect_bulk().find({}))

    for result in all_results:
        if result["result"] == "DOWN":
            #Check for start of outage
            if start_time is None:
                start_time = result["run_time"]
        if result["result"] == "UP":
            #Check for end of outage
            if start_time is not None:
                if end_time is None: #This should be the only possible outcome
                    end_time = result["run_time"]
                    total_time = end_time - start_time
                    logger.debug("Total time: %s", total_time)
                    update_outages()
                else:
                    logger.info("An error has occurred -- line 70")

if __name__ == "__main__":
    logger = logging.getLogger('converter_log')
    init_logger()
    logger.info("Starting database conversion...")
    delete_old_outages()
    calculate_outages()
    logger.info("Script finished. Database (should?) now be converted.")