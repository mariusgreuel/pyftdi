import logging
import pyetw
from pyftdi.eeprom import FtdiEeprom

logging.basicConfig(level=logging.DEBUG, handlers=(pyetw.LoggerHandler(),))
logging.getLogger("pyftdi.ftdi").setLevel(logging.DEBUG)
logging.getLogger("pyftdi.d2xx").setLevel(logging.DEBUG)

eeprom = FtdiEeprom()
eeprom.open("ftdi://::FT*/1")

for pos in range(0, len(eeprom.data), 16):
    print(" ".join(["%02x" % x for x in eeprom.data[pos : pos + 16]]))
