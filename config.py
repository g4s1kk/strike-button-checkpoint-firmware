from machine import RTC

import datetime as dt
import json
import os.path
import logging


from boot import STORAGE_PATH, ext_rtc


machine_rtc = RTC()

LEDS_PAD_PIN = 4
LEDS_COUNT = 25
BUTTONS_DEBOUNCE_TIMER_ID = 3
BUTTONS_DEBOUNCE_INTERVAL_MS = 10


DEFAULTS = {
    "DEVICE_ID": "default_checkpoint",
    "BUTTONS": {
        "ORANGE": 16,
        "PINK": 17
    },
    "NEUTRAL_COLOR": "WHITE",
    "GAME_START_DTTM": ext_rtc.datetime.replace(tzinfo=None, hour=12, minute=0, second=0).isoformat(),
    "GAME_END_DTTM": ext_rtc.datetime.replace(tzinfo=None, hour=18, minute=0, second=0).isoformat(),
    "TZ_OFFSET_HOURS": 3,
    "SSID": "default_checkpoint",
    "PASSWORD": "12345678"
}

EXT_CFG_FILENAME = "config.json"
LOG_FILENAME = "app.log"
BATTLELOG_FILE = "/battle.log"
BATTLELOG_BACKUP_PERIOD = 600 # 600 sec


external_cfg_path = os.path.join(STORAGE_PATH, EXT_CFG_FILENAME)
if os.path.exists(external_cfg_path):
    with open(external_cfg_path, "r") as f:
        ENVIRON = json.load(f)
else:
    ENVIRON = DEFAULTS

INT_LOG_FILE = os.path.join("/", LOG_FILENAME)
EXT_LOG_FILE = os.path.join(STORAGE_PATH, LOG_FILENAME)
DEVICE_ID = ENVIRON["DEVICE_ID"]
BUTTONS = ENVIRON["BUTTONS"]
NEUTRAL_COLOR = ENVIRON["NEUTRAL_COLOR"]
GAME_START_DTTM = ENVIRON["GAME_START_DTTM"]
GAME_END_DTTM = ENVIRON["GAME_END_DTTM"]
TZ_OFFSET_HOURS = ENVIRON["TZ_OFFSET_HOURS"]
SSID = ENVIRON["SSID"]
PASSWORD = ENVIRON["PASSWORD"]


game_timezone = dt.timezone(dt.timedelta(hours=TZ_OFFSET_HOURS))
game_start_dttm = dt.datetime.fromisoformat(GAME_START_DTTM).astimezone(game_timezone)
game_end_dttm = dt.datetime.fromisoformat(GAME_END_DTTM).astimezone(game_timezone)

# configure logger
logger = logging.getLogger(DEVICE_ID)
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s-%(levelname)s-%(name)s:: %(message)s"
)
for log_file in [INT_LOG_FILE, EXT_LOG_FILE]:
    handler = logging.FileHandler(filename=log_file)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
debug_handler = logging.StreamHandler()
debug_handler.setFormatter(formatter)
logger.addHandler(debug_handler)
