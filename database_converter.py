import logging
from logging import RotatingFileHandler
from datetime import timedelta, datetime

import pymongo
from pymongo import MongoClient
from bson.codec_options import CodecOptions
import pytz

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

def init_logger():
    log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
    log_handler = RotatingFileHandler('db_conversion.log', encoding=None, delay=False, errors=None, maxBytes=1024*25, backupCount=10)
    log_handler.setFormatter(log_formatter)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(log_handler)
    return 













if __name__ == "__main__":
    init_logger()
    logger = logging.getLogger('converter_log')