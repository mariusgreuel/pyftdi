import logging
import time
from pyftdi.gpio import GpioAsyncController

logger = logging.getLogger("pyftdi.d2xx")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

gpio = GpioAsyncController()
gpio.configure("ftdi://::FT*/1", direction=0xFF)

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
