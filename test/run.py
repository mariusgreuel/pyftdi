import logging
from pyftdi.i2c import I2cController

logger = logging.getLogger("pyftdi.d2xx")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# Instantiate an I2C controller
i2c = I2cController()

# Configure the first interface (IF/1) of the FTDI device as an I2C master
i2c.configure('ftdi://ftdi:232h/1')

# Get a port to an I2C slave device
slave = i2c.get_port(0x21)

# Send one byte, then receive one byte
slave.exchange([0x04], 1)

# Write a register to the I2C slave
slave.write_to(0x06, b'\x00')

# Read a register from the I2C slave
slave.read_from(0x00, 1)
