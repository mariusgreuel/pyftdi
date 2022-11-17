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
slave = i2c.get_port(0x77)

BME68X_REG_CHIP_ID = 0xD0
BME68X_REG_SOFT_RESET = 0xE0
BME68X_CHIP_ID = 0x61

# BME68x soft reset
slave.write_to(BME68X_REG_SOFT_RESET, b'\xB6')

# Read a register from the I2C slave
status = slave.read_from(BME68X_REG_CHIP_ID, 1)
print(f"Status: 0x{status[0]:02X}")

if status[0] == BME68X_CHIP_ID:
    print(f"Found BME68x device")
