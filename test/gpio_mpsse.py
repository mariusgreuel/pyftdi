import logging
import time
from pyftdi.gpio import GpioMpsseController

logger = logging.getLogger("pyftdi.d2xx")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
#logger.addHandler(handler)

gpio = GpioMpsseController()
gpio.configure('ftdi:///1', direction=0xFFFF, frequency=10)

index = 0
inc = 1
while True:
    for _ in range(2 * 16 - 2):
        gpio.write(1 << index)
        time.sleep(0.1)
        if index == 15:
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
