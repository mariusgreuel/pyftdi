import logging
import time
import pyetw
from pyftdi.gpio import GpioMpsseController

logging.basicConfig(level=logging.DEBUG, handlers=(pyetw.LoggerHandler(),))
logging.getLogger("pyftdi.ftdi").setLevel(logging.DEBUG)
logging.getLogger("pyftdi.d2xx").setLevel(logging.DEBUG)

gpio1 = GpioMpsseController()
gpio1.configure("ftdi://ftdi:2232h/1", direction=0xFFFF, frequency=10)
gpio2 = GpioMpsseController()
gpio2.configure("ftdi://ftdi:2232h/2", direction=0xFFFF, frequency=10)

pins = 32

index = 0
inc = 1
while True:
    for _ in range(2 * pins - 2):
        if index < 16:
            gpio1.write(1 << index)
            gpio2.write(0)
        else:
            gpio1.write(0)
            gpio2.write(1 << (index - 16))

        time.sleep(0.1)

        if index == pins - 1:
            inc = -1
        elif index == 0:
            inc = 1

        index += inc

    gpio1.write(0xFFFF)
    gpio2.write(0xFFFF)
    time.sleep(0.25)
    gpio1.write(0x0000)
    gpio2.write(0x0000)
    time.sleep(0.25)
    gpio1.write(0xFFFF)
    gpio2.write(0xFFFF)
    time.sleep(0.25)
    gpio1.write(0x0000)
    gpio2.write(0x0000)
    time.sleep(0.25)
