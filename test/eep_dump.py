import logging
from pyftdi.eeprom import FtdiEeprom

logger = logging.getLogger("pyftdi.d2xx")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
#logger.addHandler(handler)

eeprom = FtdiEeprom()
eeprom.open('ftdi:///1' )

for pos in range(0, len(eeprom.data), 16):
    print(' '.join(['%02x' % x for x in eeprom.data[pos:pos+16]]))
