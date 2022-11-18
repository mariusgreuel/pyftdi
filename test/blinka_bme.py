import logging
import os
import time

os.environ["BLINKA_FT232H"] = "1"

logger = logging.getLogger("pyftdi.d2xx")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

import board
import adafruit_bme680

i2c = board.I2C()

bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, refresh_rate=1)
bme680.sea_level_pressure = 1013.25

logger.setLevel(logging.INFO)

while True:
    temperature = bme680.temperature
    humidity = bme680.relative_humidity

    print(f"Temperature: {temperature:0.1f}C, Humidity: {humidity:0.1f}%")

    time.sleep(1)
