import logging
import pyetw
from pyftdi.ftdi import Ftdi

logging.basicConfig(level=logging.DEBUG, handlers=(pyetw.LoggerHandler(),))
logging.getLogger("pyftdi.ftdi").setLevel(logging.DEBUG)
logging.getLogger("pyftdi.d2xx").setLevel(logging.DEBUG)

ftdi = Ftdi()
ftdi.show_devices()
