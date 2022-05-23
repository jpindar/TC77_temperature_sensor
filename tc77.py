#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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


def init():
    global spi
    GPIO.setmode(GPIO.BCM)   # use the channel numbers on the Broadcom chip
    GPIO.setup(CS_PIN, GPIO.OUT)
    GPIO.output(CS_PIN, 1)
    spi = spidev.SpiDev()
    spi.open(0, 0)  # spi.open(bus, device)
    spi.mode = 0b00  # two bit pattern of clock polarity and phase [CPOL|CPHA]
    spi.max_speed_hz = 15200


def decode_twos_comp(val:int , bits:int) -> int:
    if (val & (1 << (bits - 1))) != 0:  # if msb is set
        val = val - (1 << bits)
    return val


def getTemperature() -> float:
    GPIO.output(CS_PIN, 0)
    raw: list[int] = spi.readbytes(2)
    GPIO.output(CS_PIN, 1)
    status: int = (raw[1] & 0x04) != 0  # always true?
    data: int = ((raw[0] << 8) + raw[1])
    if __name__ == '__main__':
        print(time.strftime('%Y/%m/%d %H:%M:%S') + ' status bit ' + str(status) + ' ' + format(data, '016b'), end='')
    data = data >> 3  # remove 3 lsbs.
    # now data is a 13 bit two's complement number  (16 bits - 3 = 13)
    data = decode_twos_comp(data, 13)
    float_data: float = float(data) * TEMPERATURE_STEP
    return float_data


if __name__ == '__main__':
    init()
    try:
        while True:
            Celsius: float = getTemperature()
            Fahrenheit: float = (Celsius * (9.0 / 5.0)) + 32
            print(format(Celsius, '7.3f') + "°C, " + format(Fahrenheit, '7.3f') + "°F")
            time.sleep(DELAY)
    except KeyboardInterrupt:
        pass
    finally:
        spi.close()
        GPIO.cleanup()
