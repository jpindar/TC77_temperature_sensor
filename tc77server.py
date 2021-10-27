#!/usr/bin/env python3
"""
   This uses a RaspberryPi to read the temperature from a Microchip TC77 sensor via SPI.

"""
from flask import Flask, request, render_template
import time
import datetime
import os
import tc77


app = Flask(__name__)


@app.route('/')
@app.route('/timeandtemp')
def show_both():
    Celsius = tc77.getTemperature()
    Fahrenheit = 9.0/5.0 * Celsius + 32.0
    now = datetime.datetime.now()
    templateData = {
        'title': 'Time and Temperature',
        'time': now.strftime("%Y-%m-%d %H:%M"),
        'tempC': "{:.1f}".format(Celsius),
        'tempF': "{:.1f}".format(Fahrenheit)
    }
    return render_template('temperature.html', **templateData)


@app.route('/temp')
def show_temp():
    Celsius = tc77.getTemperature()
    templateData = {
        'title': 'Temperature',
        'tempC': "{:.1f}".format(Celsius)
    }
    return render_template('temperatureonly.html', **templateData)


@app.route("/time")
def show_time():
    now = datetime.datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M")
    templateData = {
        'title': 'Time',
        'time': timeString
    }
    return render_template('time.html', **templateData)


# this fixes the CORS issue
@app.after_request
def after_request(response):
    # this is all that is necessary to allow access via GET and via iframes
    response.headers.add('Access-Control-Allow-Origin', '*')  # asterisk is wildcard meaning any site can access this
    return response


if __name__ == '__main__':
    tc77.init()
    # 0.0.0.0 means publicly available
    # app.run(host='0.0.0.0', port=80, debug=False)
    app.run(host='0.0.0.0', port=80, debug=True)

