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

def outage_calculator_verify_length(col):
    try:
        oldest_outage = col[0]
        #Set it to max time range datetime if it's older than that
        if oldest_outage["start"] <= time_delta:
            oldest_outage["start"] = time_delta
    except Exception as exception:
        col = None
    return col

#The next 4 functions will pull the results for a given time period and calculate the uptime percentage
#add .01 to make sure we're grabbing enough entries. Laziest hack ever but whatever; it works. Don't @ me.
def get_day():
    time_delta = datetime.now(pytz.timezone("US/Central")) - timedelta(days=1.00000001)
    #Get entries where end time is within the last day, then need to handle outages that cross over the time line.
    col = db_connect_outage().find({"end": {'$gt': time_delta}},sort=[("end", pymongo.ASCENDING)])
    #cast cursor to list then check the start time to see if it's greater than the time delta
    col = list(col)
    return outage_calculator_verify_length(col)

def get_week():
    time_delta = datetime.now(pytz.timezone("US/Central")) - timedelta(days=7.0000000001)
    col = db_connect_outage().find({"end": {'$gt': time_delta}},sort=[("end", pymongo.ASCENDING)])
    col = list(col)
    return outage_calculator_verify_length(col)


def get_month():
    time_delta = datetime.now(pytz.timezone("US/Central")) - timedelta(days=30.000000001)
    col = db_connect_outage().find({"end": {'$gt': time_delta}},sort=[("end", pymongo.ASCENDING)])
    col = list(col)
    return outage_calculator_verify_length(col)


def get_year():
    time_delta = datetime.now(pytz.timezone("US/Central")) - timedelta(days=365.00000001)
    col = db_connect_outage().find({"end": {'$gt': time_delta}},sort=[("end", pymongo.ASCENDING)])
    col = list(col)
    return outage_calculator_verify_length(col)


def get_last_up():
    last_up = db_connect_bulk().find_one({"result": "UP"},sort=[('run_time', pymongo.DESCENDING)])
    return last_up

def get_last_down():
    last_down = db_connect_bulk().find_one({"result": "DOWN"},sort=[('run_time', pymongo.DESCENDING)])
    return last_down
def get_last_outage():
    try:
        #Find the last outage by end time
        last_outage = db_connect_outage().find_one(sort=[('end_time', pymongo.DESCENDING)])
        #Strip the ID field
        del last_outage["_id"]
    except Exception as exception:
        logger.critical("ERROR: could not get last outage entry: %s", exception)
    return last_outage

#TODO What to do if the outage is ongoing at the start of the period? Need to calculate from some middle time period forward
def get_day_percentage():
    return calculate_percentage(get_day(), "day") #args = list of outages, time offset for percentage calculation function

def get_week_percentage():
    return calculate_percentage(get_week(), "week")

def get_month_percentage():
    return calculate_percentage(get_month(), "month")

def get_year_percentage():
    return calculate_percentage(get_year(), "year")

#Percentage calculation done here
def calculate_percentage(col_dict, time_offset):
    oldest_outage_start = col_dict[0]["start"] #GET THE OLDEST OUTAGE START IN THE SET
    
    #Only calculate percentages if enough time has been elapsed
    match time_offset:
        case "day":
            #if it hasn't been that long yet, set return to -1 to hide it from the website
            if (datetime.now(pytz.timezone("US/Central")) - timedelta(days=1)) < oldest_outage_start:
                return -1
        case "week":
            if (datetime.now(pytz.timezone("US/Central")) - timedelta(days=7)) < oldest_outage_start:
                return -1
        case "month":
            if (datetime.now(pytz.timezone("US/Central")) - timedelta(days=30)) < oldest_outage_start:
                return -1
        case "year":
            if (datetime.now(pytz.timezone("US/Central")) - timedelta(days=365)) < oldest_outage_start:
                return -1

#Gather all of the outages and pull their {"length"} value (int in minutes) and add them up to get average across a period
#Defaults set at top
    outage_time = 0
    uptime_percentage = 100
    for outage in col_dict:
        outage_time += outage["length"] #length in minutes
    if outage_time > 0:
        match time_offset:
            case "day":
                minutes = 1440
            case "week":
                minutes = 10080
            case "month":
                minutes = 43200
            case "year":
                minutes = 525600
        uptime_percentage = 100 - ((outage_time / minutes) * 100) #Get the percentage of time it was up by subtracting downtime percentage from 100
    logger.debug("Outages: %s. Outages length: %s. Uptime percentage: %s.", str(len(col_dict)), str(outage_time), str(uptime_percentage))
    return uptime_percentage