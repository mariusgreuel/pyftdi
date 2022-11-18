import logging
import time
from pyftdi.gpio import GpioSyncController

logger = logging.getLogger("pyftdi.d2xx")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

gpio = GpioSyncController()
gpio.configure("ftdi://::FT*/1", direction=0xFF)

logger.setLevel(logging.INFO)

index = 0
inc = 1
while True:
    gpio.exchange(1 << index)
    time.sleep(0.1)
    if index == 7:
        inc = -1
    elif index == 0:
        inc = 1

    index += inc
