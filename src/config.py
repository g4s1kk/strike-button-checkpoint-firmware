from machine import RTC

import datetime as dt
import json
import os.path
import logging

from rtdt import DS1307

from boot import STORAGE_PATH, ext_rtc


class Config:
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
    APP_ROOT_PATH = "/"
    WEB_STATIC_FOLDER = "/static"
    WEB_MAIN_FILE = "index.html"
    WEB_PORT = 8000
    WEB_DOWNLOAD_LOG_ENDPOINT = "battle_log"
    BACKEND_IP_ADDR = "192.168.0.10"

    LOG_LEVEL = logging.INFO
    DEBUG = True

    def __init__(self, storage_path:str, ext_rtc:DS1307):
        self.WEB_MAIN_PATH = os.path.join(self.WEB_STATIC_FOLDER, self.WEB_MAIN_FILE)
        self.STORAGE_PATH = storage_path
        self.ext_rtc = ext_rtc
        self.machine_rtc = RTC()
        self.external_cfg_path = os.path.join(self.STORAGE_PATH, self.EXT_CFG_FILENAME)
        self.ENVIRON = None
        self.load_ext_cfg()
        self.setup_logger()

    def load_ext_cfg(self, logger:logging.Logger|None=None):
        if os.path.exists(self.external_cfg_path):
            with open(self.external_cfg_path, "r") as f:
                self.ENVIRON = json.load(f)
            if logger is not None:
                logger.info(f"Ext cfg updated from {self.external_cfg_path}")
        else:
            self.ENVIRON = self.DEFAULTS
            if logger is not None:
                logger.info(f"Ext cfg updated from DEFAULTS")
        self.unpack_ext_cfg()
        self.setup_ecfg_depended_settings()
    
    def unpack_ext_cfg(self):
        self.DEVICE_ID = self.ENVIRON["DEVICE_ID"]
        self.BUTTONS = self.ENVIRON["BUTTONS"]
        self.NEUTRAL_COLOR = self.ENVIRON["NEUTRAL_COLOR"]
        self.GAME_START_DTTM = self.ENVIRON["GAME_START_DTTM"]
        self.GAME_END_DTTM = self.ENVIRON["GAME_END_DTTM"]
        self.TZ_OFFSET_HOURS = self.ENVIRON["TZ_OFFSET_HOURS"]
        self.SSID = self.ENVIRON["SSID"]
        self.PASSWORD = self.ENVIRON["PASSWORD"]

    def setup_ecfg_depended_settings(self):
        self.game_timezone = dt.timezone(
            dt.timedelta(hours=self.TZ_OFFSET_HOURS)
        )
        self.game_start_dttm = dt.datetime.\
            fromisoformat(self.GAME_START_DTTM).\
            astimezone(self.game_timezone)
        self.game_end_dttm = dt.datetime.\
            fromisoformat(self.GAME_END_DTTM).\
            astimezone(self.game_timezone)

    def setup_logger(self):
        INT_LOG_FILE = os.path.join(self.APP_ROOT_PATH, self.LOG_FILENAME)
        EXT_LOG_FILE = os.path.join(self.STORAGE_PATH, self.LOG_FILENAME)
        logger = logging.getLogger(self.DEVICE_ID)
        logger.setLevel(self.LOG_LEVEL)
        formatter = logging.Formatter(
            "%(asctime)s-%(levelname)s-%(name)s :: %(message)s"
        )
        for log_file in [INT_LOG_FILE, EXT_LOG_FILE]:
            handler = logging.FileHandler(filename=log_file)
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        if self.DEBUG:
            debug_handler = logging.StreamHandler()
            debug_handler.setFormatter(formatter)
            logger.addHandler(debug_handler)
        
        self.logger = logger


config = Config(
    storage_path=STORAGE_PATH,
    ext_rtc=ext_rtc
)
