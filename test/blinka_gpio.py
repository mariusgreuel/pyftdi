import logging
import os
import time

os.environ["BLINKA_FT232H"] = "1"

logger = logging.getLogger("pyftdi.d2xx")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
#logger.addHandler(handler)

import digitalio
from adafruit_blinka.microcontroller.ftdi_mpsse.mpsse.pin import Pin

leds = []
for i in range(12):
    led = digitalio.DigitalInOut(Pin(1+i))
    led.direction = digitalio.Direction.OUTPUT
    leds.append(led)

index = 0
inc = 1
while True:
    leds[index].value ^= 1
    time.sleep(0.1)
    leds[index].value ^= 1
    if index == 11:
        inc = -1
    elif index == 0:
        inc = 1

    index += inc
