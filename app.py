import logging
import os
import threading
from datetime import datetime
from logging.handlers import RotatingFileHandler
from time import strftime

from flask import Flask, render_template
from waitress import serve

import mongoconnect

from background import main_loop

#config
template_dir = os.path.abspath('./static/templates/')

#Start app
app = Flask(__name__, template_folder=template_dir)
logger = logging.getLogger('ody_log')

#The main website
@app.route("/")
#I legitimately can't remember why these args exist. But the site works and I ain't gonna fight it.
def index(result=None,last_run_time=None):
    #get the latest entry from the database and breakdown for display
    last_result = mongoconnect.get_latest()
    last_run_time = last_result["run_time"]
    last_run_time = strftime('%I:%M %p on %x', datetime.timetuple(last_run_time))
    result = last_result["result"]
    return render_template('index.html', result=result,last_run_time=last_run_time,one_day_uptime=mongoconnect.get_day(), one_week_uptime=mongoconnect.get_week(), one_month_uptime=mongoconnect.get_month(), one_year_uptime=mongoconnect.get_year())

#Favicon
#@app.route('/favicon.ico')
#def favicon():
#    return send_from_directory('/static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

#Starts the web server
def start_waitress():
    try:
        logger.info("Starting web server...")
        serve(app, host='0.0.0.0', port=5000)
        logger.info("Web server started successfully...")
    except Exception as exception:
        logger.critical("ERROR: Could not start web server. %s", exception)
 
def init_logger():
    log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
    log_handler = RotatingFileHandler('odychk.log', encoding=None, delay=False, errors=None, maxBytes=1024*25, backupCount=30)
    log_handler.setFormatter(log_formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(log_handler)

#Launch the background thread to pull info to the db from Odyssey
def start_update_worker():
    logger.debug("Starting update worker thread...")
    update_daemon = threading.Thread(group=None, target=main_loop, daemon=True, name='Update Worker')
    try:
        update_daemon.start()
        logger.info("Update worker thread started successfully...")
    except Exception as exception:
        logger.critical("ERROR: could not start update worker thread. %s.", exception)

#Startup calls
if __name__ == "__main__":
    init_logger()
    start_update_worker()
    start_waitress()
    logger.info("Ready to go...")
