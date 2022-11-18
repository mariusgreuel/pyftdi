import logging
import time
from pyftdi.gpio import GpioMpsseController

logger = logging.getLogger("pyftdi.d2xx")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

gpio = GpioMpsseController()
gpio.configure("ftdi://::FT*/1", direction=0x0000, frequency=10)

logger.setLevel(logging.INFO)

index = 0
inc = 1
while True:
    value = gpio.read()[0]
    print(f"Port={value:04X}")
    time.sleep(0.1)
