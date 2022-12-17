import logging
import time
import pyetw
from pyftdi.gpio import GpioMpsseController

logging.basicConfig(level=logging.DEBUG, handlers=(pyetw.LoggerHandler(),))
logging.getLogger("pyftdi.ftdi").setLevel(logging.DEBUG)
logging.getLogger("pyftdi.d2xx").setLevel(logging.DEBUG)

gpio = GpioMpsseController()
gpio.configure("ftdi://::FT*/1", direction=0x0000, frequency=10)

logger.setLevel(logging.INFO)

index = 0
inc = 1
while True:
    value = gpio.read()[0]
    print(f"Port={value:04X}")
    time.sleep(0.1)
