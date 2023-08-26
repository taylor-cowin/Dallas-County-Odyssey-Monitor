#package imports
from cmath import e
from flask import Flask, render_template
from datetime import datetime, timedelta
from waitress import serve
import threading

#local imports
from background import *
from mongoconnect import *

app = Flask(__name__)
def start_update_worker():
    print("Starting update worker thread...")
    update_daemon = threading.Thread(group=None, target=main_loop, daemon=True, name='Update Worker')
    try:
        update_daemon.start()
        print("Update worker thread started successfully...")
    except:
        print("ERROR: could not start update worker thread...")

#def start_waitress():
#    try:
#        print("Starting web server...")
#        serve(app, host='0.0.0.0', port=5000)
#        print("Web server started successfully...")
#    except:
#        print("ERROR: could not start web server.")
 
#start_waitress()
start_update_worker()


    
#waitress_thread = threading.Thread(start_waitress())

print("Ready to go...")

@app.errorhandler(404)
def pageNotFound(error):
    return "Error 404 - page not found."

@app.errorhandler(500)
def internal_error(error):
    return "Error 500 - internal server error."

@app.route("/")
def index(result=None, text_color=None,last_run_time=None):
    #get the current time and determine what time it was a minute ago
    #current_time = datetime.now()
    #minute_elapsed_time = current_time - timedelta(minutes=1)

    #get the latest entry from the database and breakdown for display
    last_result = get_latest()
    last_run_time = last_result["run_time"]
    result = last_result["result"]

    return render_template('index.html', result=result,last_run_time=last_run_time,one_day_uptime= -1, one_week_uptime=-1, one_month_uptime=-1, one_year_uptime=-1)