from machine import Pin, SPI
import os
import os.path
import sys
import json

from sdcard import SDCard


EXT_CFG_FILENAME = "config.py"


spi = SPI(1, baudrate=10**6, mosi=Pin(35), sck=Pin(36), miso=Pin(37))
cs = Pin(34, Pin.OUT)
sd = SDCard(spi, cs)

storage_path = "/sd"
os.mount(sd, storage_path)

external_cfg_path = os.path.join(storage_path, EXT_CFG_FILENAME)
if os.path.exists(external_cfg_path):
    with open(external_cfg_path, "r") as f:
        ENVIRON = json.load(f)
else:
    ENVIRON = dict()
    
ENVIRON["STORAGE_PATH"] = storage_path
    
# configure logger
# here

# enable wlan access point
