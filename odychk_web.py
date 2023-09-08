import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from time import strftime

from flask import Flask, render_template, send_from_directory
from waitress import serve

import mongoconnect

debug = True;

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
    last_result = api_lastresult()
    last_run_time = strftime('%I:%M %p on %x', datetime.timetuple(last_result["run_time"]))
    return render_template('index.html', result=last_result["result"],last_run_time=last_run_time,one_day_uptime=mongoconnect.get_day(), one_week_uptime=mongoconnect.get_week(), one_month_uptime=mongoconnect.get_month(), one_year_uptime=mongoconnect.get_year())

@app.route("/api/data/last/")
def api_lastresult():
    last_result = mongoconnect.get_latest()
    """
    Needs to return a value for outside access as well as for the page.
    I think the template needs to incorporate API calls instead of passing variables
    from the backend via function calls.
    """
    return last_result

@app.route("/api/data/last/outage/")
def api_last_outage():
    return
    
@app.route("/api/data/last/day/")
def api_last_day():
    return

@app.route("/api/data/last/week/")
def api_last_week():
    return

@app.route("/api/data/last/month/")
def api_last_month():
    return

@app.route("/api/data/last/year/")
def api_last_year():
    return

#Favicon
@app.route('/favicon.ico/')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

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
            app.run()
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
