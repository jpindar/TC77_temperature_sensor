# TC77_temperature_sensor
Raspberry Pi software for reading the Microchip TC77 temperature sensor ic (https://www.microchip.com/en-us/product/TC77) , which is connected via SPI.

Files:

* tc77.py - repeatedly reads the sensor and prints the temperature
* tc77server.py - Flask app that uses tc77.py to read the temperature and serves a simple page to display it






