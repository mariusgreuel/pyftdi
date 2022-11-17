import logging
import os
import time

os.environ["BLINKA_FT232H"] = "1"

logger = logging.getLogger("pyftdi.d2xx")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
#logger.addHandler(handler)

import board
import digitalio

led_c0 = digitalio.DigitalInOut(board.C0)
led_c0.direction = digitalio.Direction.OUTPUT

led_c1 = digitalio.DigitalInOut(board.C1)
led_c1.direction = digitalio.Direction.OUTPUT

led_c2 = digitalio.DigitalInOut(board.C2)
led_c2.direction = digitalio.Direction.OUTPUT

led_c3 = digitalio.DigitalInOut(board.C3)
led_c3.direction = digitalio.Direction.OUTPUT

led_c4 = digitalio.DigitalInOut(board.C4)
led_c4.direction = digitalio.Direction.OUTPUT

led_c5 = digitalio.DigitalInOut(board.C5)
led_c5.direction = digitalio.Direction.OUTPUT

led_c6 = digitalio.DigitalInOut(board.C6)
led_c6.direction = digitalio.Direction.OUTPUT

led_c7 = digitalio.DigitalInOut(board.C7)
led_c7.direction = digitalio.Direction.OUTPUT

leds = (led_c0, led_c1, led_c2, led_c3, led_c4, led_c5, led_c6, led_c7)

while True:
    for i in range(8):
        leds[i].value ^= 1
        time.sleep(1/8)
