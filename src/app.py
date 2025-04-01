from machine import Timer

import asyncio
import logging
from battlelogger import BattleLogger

from src.config import config as cfg
import src.helpers as helpers


class CheckpointApp:
    def __init__(
            self,
            debounce_timer:Timer,
            battle_logger:BattleLogger,
        ):
        self.logger = logging.getLogger(cfg.DEVICE_ID)
        self.debounce_timer = debounce_timer
        self.setup_hardware()
        self.led_panel.on()
        self.color = self.button_pad._cname
        self.logger.info(f"Button pad initial state: {self.color}")
        self.game_start = False
        self.game_end = False
        self.logger.info("Checkpoint app init finished")

    def setup_hardware(self):
        self.led_panel = helpers.attach_led()
        self.button_pad = helpers.attach_buttons(self.debounce_timer)

    def write_system_log(self, msg:str):
        self.logger.info(msg)
        self.battle_logger.log(
            faction_id="SYSTEM",
            event=msg
        )

    async def wait_game_start(self):
        self.write_system_log("Game start pending")
        while not self.game_start:
            if helpers.check_game_start():
                self.game_start = True
                break
            await asyncio.sleep(15)
        return self.game_start

    async def wait_game_end(self):
        while not self.game_end:
            if helpers.check_game_end():
                self.game_end = True
                break
            await asyncio.sleep(15)
        return self.game_end
    
    def refresh_color(self):
        self.button_pad.check_pressed()
        if self.button_pad.color_name != self.color:
            self.color = self.button_pad.color_name
            self.logger.info(f"Color changed: {self.color}")
            self.led_panel.on(rgb=self.button_pad.rgb_color)
            self.battle_logger.log(
                faction_id=self.color.upper(),
                event="Capture checkpoint"
            )

    def game_end_teardown(self):
        self.battle_logger.end()
        self.led_panel.on(cname=cfg.NEUTRAL_COLOR)
        self.write_system_log("Game finished")
    
    async def run(self):
        game_start = asyncio.create_task(self.wait_game_start())
        await game_start
        self.write_system_log("Game started")
        game_end = asyncio.create_task(self.wait_game_end())
        while not self.game_end:
            self.refresh_color()
            yield
        self.game_end_teardown()
