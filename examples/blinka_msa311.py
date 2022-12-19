import logging
import os
import time
import pyetw

logging.basicConfig(level=logging.DEBUG, handlers=(pyetw.LoggerHandler(),))
logging.getLogger("pyftdi.ftdi").setLevel(logging.DEBUG)
logging.getLogger("pyftdi.d2xx").setLevel(logging.DEBUG)

os.environ["BLINKA_FT232H"] = "1"

import board
import digitalio
from adafruit_msa3xx import MSA311
from adafruit_blinka.microcontroller.ftdi_mpsse.mpsse.pin import Pin

# spi = board.SPI()
i2c = board.I2C()
msa = MSA311(i2c)

leds = []
for i in range(3, 16):
    led = digitalio.DigitalInOut(Pin(i))
    led.direction = digitalio.Direction.OUTPUT
    leds.append(led)

logger.setLevel(logging.INFO)

index = 0
inc = 1
while True:
    leds[index].value = 1

    print("MSA311: %f %f %f" % msa.acceleration)
    time.sleep(0.1)

    leds[index].value = 0
    if index == len(leds) - 1:
        inc = -1
    elif index == 0:
        inc = 1

    index += inc
