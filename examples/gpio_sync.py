import logging
import time
import pyetw
from pyftdi.gpio import GpioSyncController

logging.basicConfig(level=logging.DEBUG, handlers=(pyetw.LoggerHandler(),))
logging.getLogger("usb.core").setLevel(logging.DEBUG)
logging.getLogger("pyftdi.ftdi").setLevel(logging.DEBUG)
logging.getLogger("pyftdi.d2xx").setLevel(logging.DEBUG)

pins = 8

gpio = GpioSyncController()
gpio.configure("ftdi://::FT*/1", direction=(1 << pins) - 1)

index = 0
inc = 1
while True:
    gpio.exchange(1 << index)
    time.sleep(0.1)
    if index == pins - 1:
        inc = -1
    elif index == 0:
        inc = 1

    index += inc
