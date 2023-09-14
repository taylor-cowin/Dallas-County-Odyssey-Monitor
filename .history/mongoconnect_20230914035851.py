import logging
from datetime import timedelta, datetime

import pymongo
from pymongo import MongoClient
from bson.codec_options import CodecOptions
import pytz

logger = logging.getLogger('ody_log')

#connect to the database and pull the results in local time or push them in utc
def db_connect_bulk():
    dbclient = MongoClient()
    db = dbclient["odychk"]
    col = db["results"]
    col = col.with_options(codec_options=CodecOptions(tz_aware=True,tzinfo=pytz.timezone('US/Central')))
    return col

#Connector for the outage DB
def db_connect_outage():
    dbclient = MongoClient()
    db = dbclient["odychk"]
    col = db["outages"]
    col = col.with_options(codec_options=CodecOptions(tz_aware=True,tzinfo=pytz.timezone('US/Central')))
    return col

#Get the most recent result to determine up/down
def get_latest():
    try:
        last_result = db_connect_bulk().find_one(sort=[('run_time', pymongo.DESCENDING)])
        #Strip the ID field
        del last_result["_id"]
    except Exception as exception:
        logger.critical("ERROR: could not get last db entry: %s", exception)
    return last_result

#The next 4 functions will pull the results for a given time period and calculate the uptime percentage
#add .01 to make sure we're grabbing enough entries. Laziest hack ever but whatever; it works. Don't @ me.
def get_day():
    time_delta = datetime.now(pytz.timezone("US/Central")) - timedelta(days=1.00000001)
    col = db_connect_bulk().find({"run_time": {'$gt': time_delta}},sort=[("run_time", pymongo.ASCENDING)])
    return col

def get_week():
    time_delta = datetime.now(pytz.timezone("US/Central")) - timedelta(days=7.0000000001)
    col = db_connect_bulk().find({"run_time": {'$gt': time_delta}},sort=[("run_time", pymongo.ASCENDING)])
    return col

def get_month():
    time_delta = datetime.now(pytz.timezone("US/Central")) - timedelta(days=30.000000001)
    col = db_connect_bulk().find({"run_time": {'$gt': time_delta}},sort=[("run_time", pymongo.ASCENDING)])
    return col

def get_year():
    time_delta = datetime.now(pytz.timezone("US/Central")) - timedelta(days=365.00000001)
    col = db_connect_bulk().find({"run_time": {'$gt': time_delta}},sort=[("run_time", pymongo.ASCENDING)])
    return col

def get_last_down():
    last_down = db_connect_bulk().find_one({"result": "DOWN"},sort=[('run_time', pymongo.DESCENDING)])
    return last_down

def get_last_outage():
    try:
        last_outage = db_connect_outage().find_one(sort=[('end_time', pymongo.DESCENDING)])
        #Strip the ID field
        del last_outage["_id"]
    except Exception as exception:
        logger.critical("ERROR: could not get last outage entry: %s", exception)
    return last_result


def get_day_percentage():
    return calculate_percentage(get_day(), "day")

def get_week_percentage():
    return calculate_percentage(get_week(), "week")

def get_month_percentage():
    return calculate_percentage(get_month(), "month")

def get_year_percentage():
    return calculate_percentage(get_year(), "year")

#Percentage calculation done here
def calculate_percentage(col_dict, time_offset):
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

# Count # of "DOWN" entries and calculate downtime by dividing by number of entries OR return defaults if down_count isn't initialized (infer 0)
    for entry in col_dict:
        if entry["result"] == "DOWN" or entry["result"] == "ERROR":
            down_count += 1
    try:
        if down_count > 0:
            #hashtagmaths
            uptime_percentage = round(float(100-float(100*float(down_count/len(col_dict)))), 2)
    except NameError:
        down_count = 0
        uptime_percentage = 100
    logger.debug("Total count: %s. Down count: %s. Uptime percentage: %s.", str(len(col_dict)), str(down_count), str(uptime_percentage))
    return uptime_percentage