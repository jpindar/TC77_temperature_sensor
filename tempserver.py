#!/usr/bin/env python3
"""
   This uses a RaspberryPi to read the temperature from a Microchip TC77 sensor via SPI.
   It's also my place for demonstrating basic flask functionality

"""
from flask import Flask, request, render_template
import spidev
import time
import datetime
import os
import RPi.GPIO as GPIO

pin = 26
TEMPERATURE_STEP = 0.0625


def init_spi():
    global spi
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 1)
    spi = spidev.SpiDev()
    spi.open(0,0)
    spi.mode = 0b00
    spi.max_speed_hz = 15200


def decode_twos_comp(val,bits):
    if (val & (1 << (bits-1))) !=0:  # if msb is set
        val = val - (1 << bits)      # find the negative value
    return val

def getTemperature():
    # time.sleep(0.05)  # doesn't read correctly without this
    GPIO.output(pin, 0)
    # time.sleep(0.1)  # doesn't read correctly without this
    raw = spi.readbytes(2)
    GPIO.output(pin, 1)
    # status = (raw[1] & 0x04) != 0
    raw = ((raw[0] <<8) + raw[1])
    data = raw >> 3 # remove 3 lsbs.
    # now data is a 13 bit two's complement number  (16 bits -3 = 13)
    data = decode_twos_comp(data,13)
    Celsius = float(data) * TEMPERATURE_STEP
    Fahrenheit = Celsius * (9.0 / 5.0) + 32
    return [Celsius,Fahrenheit]


app = Flask(__name__)


@app.route('/')
@app.route('/temperature')
def show_both():
    temperature = getTemperature()
    now = datetime.datetime.now()
    templateData = {
        'title': 'Time and Temperature',
        'time': now.strftime("%Y-%m-%d %H:%M"),
        'tempC': "{:.1f}".format(temperature[0]),
        'tempF': "{:.1f}".format(temperature[1])
    }
    return render_template('temperature.html', **templateData)


# add /temp to the url
@app.route('/temp')
def show_temp():
    temperature = getTemperature()
    templateData = {
        'title': 'Temperature',
        'tempC': "{:.1f}".format(temperature[0])
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


# this fixes the Cross-Origin Resource Sharing issue
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')  # asterisk is wildcard meaning any site can access this
    return response

if __name__ == '__main__':
    spi = None
    init_spi()
    # could use something like app.run(host='127.0.0.1', port=8080)
    # but 0.0.0.0 means publicly available
    app.run(host='0.0.0.0', port=80, debug=True)

    # this part of the code IS run when we cntl-c the server
    # We still get the "this channel is already in use" warning
    # but it doesn't matter
    spi.close()
    GPIO.cleanup()

