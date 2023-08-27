#package imports
import threading
import os
import logging

from datetime import datetime
from time import strftime
from flask import Flask, render_template
from waitress import serve


#local imports
from background import main_loop
import mongoconnect

#config
template_dir = os.path.abspath('./static/templates/')

#Start app
app = Flask(__name__, template_folder=template_dir)

@app.route("/")
def index(result=None, text_color=None,last_run_time=None):
    #get the latest entry from the database and breakdown for display
    last_result = mongoconnect.get_latest()
    last_run_time = last_result["run_time"]
    last_run_time = strftime('%I:%M %p on %x', datetime.timetuple(last_run_time))
    result = last_result["result"]

    return render_template('index.html', result=result,last_run_time=last_run_time,one_day_uptime=mongoconnect.get_day(), one_week_uptime=mongoconnect.get_week(), one_month_uptime=mongoconnect.get_month(), one_year_uptime=mongoconnect.get_year())


def start_waitress():
    try:
        logging.info("Starting web server...")
        serve(app, host='0.0.0.0', port=5000)
        logging.info("Web server started successfully...")
    except:
        logging.critical("ERROR: could not start web server.")
 

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

if __name__ == "__main__":
    start_waitress()
    init_logger()
    start_update_worker()

logging.info("Ready to go...")

#@app.errorhandler(404)
#def pageNotFound(error):
#    return "Error 404 - page not found."

#@app.errorhandler(500)
#def internal_error(error):
#    logging.error("Error page was reached")
#    return "Error 500 - internal server error."

