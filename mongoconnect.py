from datetime import datetime
import pymongo
from pymongo import MongoClient

def get_latest():
    result = ""
    last_run_time = ""
    dbclient = MongoClient()
    db = dbclient["odychk"]
    col = db["results"]
    try:
        last_result = col.find_one(sort=[('_id', pymongo.DESCENDING)])
    except:
        print("ERROR: could not get last db result from mongo.")
    return last_result

def get_day():
    return 0

def get_week():
    return 0

def get_month():
    return 0

#Push update to mongodb
def set_result(result_dict):
    dbclient = MongoClient()
    db = dbclient["odychk"]
    col = db["results"]
    col.insert_one({"run_time": result_dict["run_time"], "result": result_dict["result"]})
    return