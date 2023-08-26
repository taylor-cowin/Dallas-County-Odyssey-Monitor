#package imports
from distutils.debug import DEBUG
from distutils.log import INFO, debug
from time import strftime, strptime
from flask import Flask, render_template
from datetime import datetime, timedelta
#from waitress import serve
import threading
import os
import logging

#local imports
from background import *
import mongoconnect

#config
template_dir = os.path.abspath('./static/templates/')

#Start app
app = Flask(__name__, template_folder=template_dir)

def init_logger():
    logging.basicConfig(filename="odychk.log", level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')

def start_update_worker():
    logging.info("Starting update worker thread...")
    update_daemon = threading.Thread(group=None, target=main_loop, daemon=True, name='Update Worker')
    try:
        update_daemon.start()
        logging.info("Update worker thread started successfully...")
    except:
        logging.info("ERROR: could not start update worker thread...")

#def start_waitress():
#    try:
#        print("Starting web server...")
#        serve(app, host='0.0.0.0', port=5000)
#        print("Web server started successfully...")
#    except:
#        print("ERROR: could not start web server.")
 
init_logger()
#start_waitress()
start_update_worker()

logging.info("Ready to go...")

@app.errorhandler(404)
def pageNotFound(error):
    return "Error 404 - page not found."

@app.errorhandler(500)
def internal_error(error):
    logging.error("Error page was reached")
    return "Error 500 - internal server error."

@app.route("/")
def index(result=None, text_color=None,last_run_time=None):
    #get the latest entry from the database and breakdown for display
    last_result = mongoconnect.get_latest()
    last_run_time = last_result["run_time"]
    last_run_time = strptime(last_run_time, '%Y-%m-%d %H:%M:%S')
    last_run_time = strftime('%H:%M', last_run_time)
    result = last_result["result"]

    return render_template('index.html', result=result,last_run_time=last_run_time,one_day_uptime= 1, one_week_uptime=1, one_month_uptime=1, one_year_uptime=1)