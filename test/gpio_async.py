import logging
import time
import pyetw

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
root_logger = logging.getLogger()
root_logger.handlers = []
root_logger.addHandler(pyetw.LoggerHandler())

from pyftdi.gpio import GpioAsyncController


logging.getLogger("pyftdi.ftdi").setLevel(logging.DEBUG)
logging.getLogger("pyftdi.d2xx").setLevel(logging.DEBUG)

gpio = GpioAsyncController()
gpio.configure("ftdi://::FT*/2", direction=0xFF)

index = 0
inc = 1
while True:
    gpio.write(1 << index)
    time.sleep(0.1)
    if index == 7:
        inc = -1
    elif index == 0:
        inc = 1

    index += inc
