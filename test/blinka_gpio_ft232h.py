import logging
import os
import time
import pyetw

logging.basicConfig(level=logging.DEBUG, handlers=(pyetw.LoggerHandler(),))
logging.getLogger("pyftdi.ftdi").setLevel(logging.DEBUG)
logging.getLogger("pyftdi.d2xx").setLevel(logging.DEBUG)

os.environ["BLINKA_FT232H"] = "1"

logging.getLogger("pyftdi.ftdi").setLevel(logging.DEBUG)
logging.getLogger("pyftdi.d2xx").setLevel(logging.DEBUG)

import board
import digitalio

pins = (
    board.AD0, board.AD1, board.AD2, board.AD3, board.AD4, board.AD5, board.AD6, board.AD7,
    board.AC0, board.AC1, board.AC2, board.AC3, board.AC4, board.AC5, board.AC6, board.AC7,
)

leds = [digitalio.DigitalInOut(pin) for pin in pins]

for led in leds:
    led.direction = digitalio.Direction.OUTPUT

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
