import logging
import time
import pyetw
from pyftdi.gpio import GpioMpsseController

logging.basicConfig(level=logging.DEBUG, handlers=(pyetw.LoggerHandler(),))
logging.getLogger("pyftdi.ftdi").setLevel(logging.DEBUG)
logging.getLogger("pyftdi.d2xx").setLevel(logging.DEBUG)

gpio = GpioMpsseController()
gpio.configure("ftdi://::FT*/1", direction=0xFFFF, frequency=10)

pins = 16

index = 0
inc = 1
while True:
    for _ in range(2 * pins - 2):
        gpio.write(1 << index)

        time.sleep(0.1)

        if index == pins - 1:
            inc = -1
        elif index == 0:
            inc = 1

        index += inc

    gpio.write(0xFFFF)
    time.sleep(0.25)
    gpio.write(0x0000)
    time.sleep(0.25)
    gpio.write(0xFFFF)
    time.sleep(0.25)
    gpio.write(0x0000)
    time.sleep(0.25)
