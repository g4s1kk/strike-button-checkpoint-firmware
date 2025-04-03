import asyncio
from machine import Timer
import network

import ledbutton
import battlelogger as battlelogger

from src.config import config as cfg


def sync_machine_time(cfg=cfg):
    machine_rtc = cfg.machine_rtc
    ext_rtc_dttm = cfg.ext_rtc.datetime
    weekday = ext_rtc_dttm.isoweekday()
    Y, M, D, h, m, s, us, tz, fl = ext_rtc_dttm.tuple()
    machine_rtc.datetime((
        Y, M, D, weekday, h, m, s, us
    ))
    cfg.logger.info("Machine time syncronized.")


async def periodical_sync_machine_time():
    while True:
        sync_machine_time()
        asyncio.sleep(600)


def make_wlan():
    network.hostname(cfg.DEVICE_HOSTNAME)
    station = network.WLAN(network.AP_IF)
    station.active(True)
    station.config(
        essid=cfg.SSID,
        password=cfg.PASSWORD,
        authmode=network.AUTH_WPA2_PSK
    )
    cfg.logger.info(f"WLAN created: {station.ifconfig()[0]}")
    return station


def attach_buttons(debounce_timer):
    button_pad = ledbutton.ButtonPad(
        use_internal_resistor=False,
        debounce_timer=debounce_timer,
        debounce_period_ms=cfg.BUTTONS_DEBOUNCE_INTERVAL_MS
    )
    for color, pin in cfg.BUTTONS.items():
        button_pad.add_button(
            pin=pin,
            color=color
        )
    return button_pad


def attach_led():
    return ledbutton.SingleLed(
        cfg.LEDS_PAD_PIN,
        cname=cfg.NEUTRAL_COLOR,
        n_leds=cfg.LEDS_COUNT
    )


def init_battlelogger():
    return battlelogger.BattleLogger(
        device_id=cfg.DEVICE_ID,
        data_folder=cfg.BATTLELOG_FILE,
        backups_storage=cfg.STORAGE_PATH,
        encoding="UTF-8",
        rtc_instance=cfg.ext_rtc,
        tzinfo=cfg.game_timezone,
        debug=True
    )


def check_game_start():
    current_dttm = cfg.ext_rtc.datetime
    return current_dttm >= cfg.game_start_dttm


def check_game_end():
    current_dttm = cfg.ext_rtc.datetime
    return current_dttm >= cfg.game_end_dttm


class PeriodicExecutor:
    def __init__(self, period_seconds, timer_id=0):
        self._period = period_seconds * 1000 # convert to milliseconds
        self._timer = Timer(timer_id)
        self.set_alarm_off()
        self.logger = cfg.logger
        self._id = timer_id

    def set_alarm_on(self, t):
        self._alarm = 1

    def set_alarm_off(self):
        self._alarm = 0

    def __enter__(self):
        self._timer.init(
            period=self._period,
            mode=Timer.PERIODIC,
            callback=self.set_alarm_on
        )
        self.logger.info(f"Machine timer {self._id} started with period: {self._period}")
        return self

    def execute_if_alarm(self, *executables):
        if self._alarm == 1:
            results = list()
            self.set_alarm_off()
            for executable in executables:
                self.logger.info(f"Machine timer {self._id} execute callable: {executable.__name__}")
                results.append(
                    executable()
                )
            return results

        return [None for _ in executables]

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._timer.deinit()
        self.logger.info(f"Machine timer {self._id} stopped")
        return False
