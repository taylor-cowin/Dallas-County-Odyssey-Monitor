import pymongo
from pymongo import MongoClient
import logging

def db_connect():
    dbclient = MongoClient()
    db = dbclient["odychk"]
    return db["results"]

def get_latest():
    try:
        last_result = db_connect().find_one(sort=[('_id', pymongo.DESCENDING)])
    except:
        logging.critical("ERROR: could not get last db entry.")
    return last_result

def get_day():
    col = db_connect()
    return 0

def get_week():
    col = db_connect()
    return 0

def get_month():
    col = db_connect()
    return 0

#Push update to mongodb
def set_result(result_dict):
    db_connect().insert_one({"run_time": result_dict["run_time"], "result": result_dict["result"]})
    return