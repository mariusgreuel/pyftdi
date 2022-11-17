import logging
import time
from pyftdi.gpio import GpioAsyncController

logger = logging.getLogger("pyftdi.d2xx")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

gpio = GpioAsyncController()
gpio.configure('ftdi:///1', direction=0xFF)

while True:
    gpio.write(0x00)
    time.sleep(1)
    gpio.write(0xFF)
    time.sleep(1)

gpio.close()
