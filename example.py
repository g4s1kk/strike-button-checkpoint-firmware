from machine import Pin, SPI
import os

from sdcard import SDCard
from rtdt import DS1307

import ledbutton as lb
import batlelogger as bl


led = lb.Led(4, leds_count=25)
btn1 = lb.Button(16)
btn2 = lb.Button(17)

rtc = DS1307(scl=9, sda=8, timezone_offset_hours=3)



def run():
    try:
        batlog = bl.BattleLogger(
            device_id="checkpoint-1",
            data_folder="/battle_log",
            backups_storage=storage_path,
            encoding="UTF-8",
            rtc_instance=rtc,
            tzinfo=rtc.timezone,
            debug=True
        )
        led.on(lb.CNAMES.WHITE)
        while True:
            if btn1.is_pressed():
                led.on(lb.CNAMES.ORANGE)
                batlog.log(fraction_id="ORANGE", event="Got checkpoint")
            if btn2.is_pressed():
                led.on(lb.CNAMES.PINK)
                batlog.log(fraction_id="PINK", event="Got checkpoint")
    finally:
        led.off()
        batlog.end()
