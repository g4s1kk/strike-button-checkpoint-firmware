from machine import Pin, SPI

import os
import os.path

from sdcard import SDCard
from rtdt import DS1307


STORAGE_PATH = "/sd"


# mount storage
spi = SPI(1, baudrate=10**6, mosi=Pin(35), sck=Pin(36), miso=Pin(37))
cs = Pin(34, Pin.OUT)
sd = SDCard(spi, cs)
os.mount(sd, STORAGE_PATH)

# init external RTC device
ext_rtc = DS1307(scl=9, sda=8, timezone_offset_hours=3)
