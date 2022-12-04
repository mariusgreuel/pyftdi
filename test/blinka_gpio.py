import logging
import os
import time

#os.environ["BLINKA_FT232H"] = "1"
os.environ["BLINKA_FT2232H"] = "1"

logger = logging.getLogger("pyftdi.d2xx")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

import digitalio
from adafruit_blinka.microcontroller.ftdi_mpsse.mpsse.pin import Pin

leds = []
for i in range(0, 8):
    led = digitalio.DigitalInOut(Pin(i))
    led.direction = digitalio.Direction.OUTPUT
    leds.append(led)

index = 0
inc = 1
while True:
    leds[index].value = 1
    time.sleep(0.1)
    leds[index].value = 0
    if index == len(leds) - 1:
        inc = -1
    elif index == 0:
        inc = 1

    index += inc
