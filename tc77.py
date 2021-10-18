#!/usr/bin/env python
"""
   tc77.py
   use a RaspberryPi to read the temperature from a Microchip TC77 sensor via SPI
   TC77 datasheet:  https://www.microchip.com/en-us/product/TC77#document-table
   uses spiDev    https://pypi.org/project/spidev/

"""
import time
import spidev
import RPi.GPIO as GPIO

CS_PIN = 26
TEMPERATURE_STEP = 0.0625
DELAY = 0.5
spi = None

def init():
    global spi
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(CS_PIN, GPIO.OUT)
    GPIO.output(CS_PIN, 1)
    spi = spidev.SpiDev()
    spi.open(0,0)  # spi.open(bus, device)
    spi.mode = 0b00  # two bit pattern of clock polarity and phase [CPOL|CPHA]
    spi.max_speed_hz = 15200


def decode_twos_comp(val, bits):
    if (val & (1 << (bits-1))) !=0:  # if msb is set
        val = val - (1 << bits)
    return val

def getRawTemp():
    GPIO.output(CS_PIN, 0)
    raw = spi.readbytes(2)
    GPIO.output(CS_PIN, 1)
    return raw


if __name__ == '__main__':
    init()
    try:
        while True:
            raw = getRawTemp()
            status = (raw[1] & 0x04) != 0
            raw = ((raw[0] <<8) + raw[1])
            data = raw >> 3 # remove 3 lsbs.
            # now data is a 13 bit two's complement number  (16 bits -3 = 13)
            data = decode_twos_comp(data,13)
            Celsius = float(data) * TEMPERATURE_STEP
            Fahrenheit = (Celsius * (9.0/5.0)) + 32
            print(format(raw, '016b') + ", status bit " + str(status) + ", " + str(data) + ", " + format(Celsius, '7.3f') + "C, " + format(Fahrenheit, '7.3f') + "F ")
            time.sleep(DELAY)
    except KeyboardInterrupt:
        pass
    finally:
        spi.close()
        GPIO.cleanup()

