import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from time import strftime
from bson import json_util

from flask import Flask, render_template, send_from_directory
from waitress import serve

import mongoconnect

debug = True

#config
template_dir = os.path.abspath('./static/templates/')

#Start app
app = Flask(__name__, template_folder=template_dir)
logger = logging.getLogger('ody_log')

#The main website
@app.route("/", methods=['GET'])
def index():
    #get the latest entry from the database and breakdown for display
    logger.debug("Index.html accessed...")
    last_result = api_lastresult() ##PROBABLY MOVING THIS TO JSON.fetch() in the html template. need to only request the later dates in html if date has passed to avoid excess calls
    last_run_time = strftime('%I:%M %p on %x', datetime.timetuple(last_result["run_time"]))
    return render_template('index.html', result=last_result["result"],last_run_time=last_run_time,one_day_uptime=mongoconnect.get_day(), one_week_uptime=mongoconnect.get_week(), one_month_uptime=mongoconnect.get_month(), one_year_uptime=mongoconnect.get_year())

@app.route("/api/data/last/")
def api_lastresult():
    last_result = json_util.loads(json_util.dumps(mongoconnect.get_latest()))
    return last_result

"""
@app.route("/api/data/last/outage/")
def api_last_outage():
    last_outage = mongoconnect.get_outage()
    return last_outage
"""

### TODO NEED TO ADD SEPARATE API CALLS FOR PERCENTAGES -- THIS IS BROKEN BECAUSE IT'S CALLING FOR FLOAT PERCENT AND NOT THE LIST OF RESULTS
@app.route("/api/data/last/day/")
def api_last_day():
    data = mongoconnect.get_day()
    json = json_util.loads(json_util.dumps(list_process(data)))
    return json

@app.route("/api/data/last/day/percentage")
def api_last_day_percentage():
    last_day_percentage =  json_util.dumps(mongoconnect.get_day_percentage())
    return last_day_percentage

@app.route("/api/data/last/week/")
def api_last_week():
    data = mongoconnect.get_week()
    json = json_util.loads(json_util.dumps(list_process(data)))
    return json

@app.route("/api/data/last/week/percentage")
def api_last_week_percentage():
    data = json_util.dumps(mongoconnect.get_week_percentage())
    return data

@app.route("/api/data/last/month/")
def api_last_month():
    data = mongoconnect.get_month()
    json = json_util.loads(json_util.dumps(list_process(data)))
    return json

@app.route("/api/data/last/month/percentage")
def api_last_month_percentage():
    data = json_util.dumps(mongoconnect.get_month_percentage())
    return data

@app.route("/api/data/last/year/")
def api_last_year():
    last_year = mongoconnect.get_year()
    return last_year

@app.route('/favicon.ico/')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

def list_process(data):
    list_data = list(data)
    for entry in list_data:
        del entry["_id"]
    return list_data

#Starts the web server
def start_waitress():
    if debug:
        try:
            logger.info("Starting Waitress web server...")
            serve(app, host='0.0.0.0', port=5000)
            logger.info("Web server started successfully...")
        except Exception as exception:
            logger.critical("ERROR: Could not start web server. %s", exception)
    else:
        try:
            logger.debug("Starting web server...")
            #app.run()
            logger.info("Web server started successfully...")
        except Exception as exception:
            logger.critical("ERROR: Could not start debug web server. %s", exception)
 
def init_logger():
    log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
    log_handler = RotatingFileHandler('odychk.log', encoding=None, delay=False, errors=None, maxBytes=1024*25, backupCount=30)
    log_handler.setFormatter(log_formatter)
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    logger.addHandler(log_handler)

#Startup calls
if __name__ == "__main__":
    init_logger()
    start_waitress()
    logger.info("Ready to go...")
