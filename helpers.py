from machine import RTC, Timer
import network

import ledbutton
import libs.battlelogger as battlelogger

import config as cfg


def sync_machine_time():
    machine_rtc = RTC()
    machine_rtc.datetime(cfg.rtc_instance.timetuple())


def make_wlan():
    station = network.WLAN(network.AP_IF)
    station.config(
        essid=cfg.SSID,
        password=cfg.PASSWORD,
        authmode=network.AUTH_WPA2_PSK
    )
    station.active(True)
    cfg.logger.info(f"WLAN created: {station.ifconfig()[0]}")


def attach_buttons():
    buttons = ledbutton.ButtonPad()
    for color, pin in cfg.BUTTONS.items():
        buttons.add_button(pin, color)
    return buttons


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


def check_game_end():
    current_dttm = cfg.ext_rtc.datetime


class PeriodicExecutor:
    def __init__(self, period_seconds, timer_id=0):
        self._period = period_seconds * 1000 # convert to milliseconds
        self._timer = Timer(timer_id)
        self.set_alarm_off()

    def set_alarm_on(self):
        self._alarm = 1

    def set_alarm_off(self):
        self._alarm = 0

    def __enter__(self):
        self._timer.init(
            period=self._period,
            mode=Timer.PERIODIC,
            callback=self.set_alarm_on
        )
        return self

    def execute_if_alarm(self, *executables):
        if self._alarm == 1:
            self.set_alarm_off()
            results = list()
            for executable in executables:
                results.append(
                    executable()
                )
            return results

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._timer.deinit()
        return False
