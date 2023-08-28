import logging
from datetime import timedelta, datetime

import pymongo
from pymongo import MongoClient
from bson.codec_options import CodecOptions
import pytz

#connect to the database and pull the results in local time or push them in utc
def db_connect(args):
    dbclient = MongoClient()
    db = dbclient["odychk"]
    col = db["results"]
    if args == "local":
        col = col.with_options(codec_options=CodecOptions(tz_aware=True,tzinfo=pytz.timezone('US/Central')))
    return col

#Get the most recent result to determine up/down
def get_latest():
    try:
        last_result = db_connect("local").find_one(sort=[('_id', pymongo.DESCENDING)])
    except:
        logger = logging.getLogger('ody_log')
        logger.critical("ERROR: could not get last db entry.")
    return last_result

#The next 4 functions will pull the results for a given time period and calculate the uptime percentage
#add .01 to make sure we're grabbing enough entries
def get_day():
    time_delta = datetime.now(pytz.timezone("US/Central")) - timedelta(days=1.01)
    col = db_connect("local").find({"run_time": {'$gt': time_delta}},sort=[("run_time", pymongo.ASCENDING)]) # NEED TO SORT THESE TO MAKE THE POSITION 0 OLDEST
    return calculate_percentage(col, "day") #24 hour uptime

def get_week():
    time_delta = datetime.now(pytz.timezone("US/Central")) - timedelta(days=7.01)
    col = db_connect("local").find({"run_time": {'$gt': time_delta}},sort=[("run_time", pymongo.ASCENDING)])
    return calculate_percentage(col, "week") #168 hour uptime

def get_month():
    time_delta = datetime.now(pytz.timezone("US/Central")) - timedelta(days=30.01)
    col = db_connect("local").find({"run_time": {'$gt': time_delta}},sort=[("run_time", pymongo.ASCENDING)])
    return calculate_percentage(col, "month") #30 day uptime

def get_year():
    time_delta = datetime.now(pytz.timezone("US/Central")) - timedelta(days=365.01)
    col = db_connect("local").find({"run_time": {'$gt': time_delta}},sort=[("run_time", pymongo.ASCENDING)])
    return calculate_percentage(col, "year") #1 year uptime

#Percentage calculation done here
def calculate_percentage(col_dict, time_offset):
    logger = logging.getLogger('ody_log')
    #Start by converting cursor to list
    col_dict = list(col_dict)
    oldest_date = col_dict[0]["run_time"] #GET THE OLDEST DATE IN THE SET
    
    match time_offset:
        case "day":
            #if it hasn't been that long yet, set return to -1 to hide it from the website
            if (datetime.now(pytz.timezone("US/Central")) - timedelta(days=1)) < oldest_date:
                return -1
        case "week":
            if (datetime.now(pytz.timezone("US/Central")) - timedelta(days=7)) < oldest_date:
                return -1
        case "month":
            if (datetime.now(pytz.timezone("US/Central")) - timedelta(days=30)) < oldest_date:
                return -1
        case "year":
            if (datetime.now(pytz.timezone("US/Central")) - timedelta(days=365)) < oldest_date:
                return -1

    #default values
    down_count = 0
    uptime_percentage = 100
    for entry in col_dict:
        if entry["result"] == "DOWN":
            down_count += 1
       #remove the errors
       # elif(entry["result"] == "ERROR"):
       #     col_dict.remove(entry)
    if down_count > 0:
        #hashtagmaths
        uptime_percentage = round(float(100-float(100*float(down_count/ len(col_dict)))), 2)
    logger.info("Total count: " + str(len(col_dict)))
    logger.info("Down count: " + str(down_count))
    logger.info("uptime percentage: " + str(uptime_percentage))

    return uptime_percentage

#Push update to mongodb
def set_result(result_dict):
    db_connect("utc").insert_one({"run_time": result_dict["run_time"], "result": result_dict["result"]})
    return