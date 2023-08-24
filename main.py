from tkinter import N
from flask import Flask, render_template
import requests
import datetime

app = Flask(__name__)
@app.errorhandler(404)
def pageNotFound(error):
    return "Error 404 - page not found."

@app.errorhandler(500)
def internal_error(error):
    return "Error 500 - internal server error."

@app.route("/")
def index(result=None, text_color=None,last_run_time=None):
    r = requests.get('https://courtsportal.dallascounty.org/DALLASPROD')
    if r.ok:
        result = 'UP'
        text_color = '#FF3030'
    else:
        result = 'DOWN'
        text_color = '#FF3030'
    last_run_time = str(datetime.datetime.now())
    return render_template('index.html', result=result, text_color=text_color,last_run_time=last_run_time)
    