import logging
import pyetw
import pyftdi.serialext

logging.basicConfig(level=logging.DEBUG, handlers=(pyetw.LoggerHandler(),))
logging.getLogger("usb.core").setLevel(logging.DEBUG)
logging.getLogger("pyftdi.ftdi").setLevel(logging.DEBUG)
logging.getLogger("pyftdi.d2xx").setLevel(logging.DEBUG)

port = pyftdi.serialext.serial_for_url("ftdi://::FT*/1", baudrate=9600)
port.write(b"Hello World")
data = port.read(11)
print("Data: " + str(data))
