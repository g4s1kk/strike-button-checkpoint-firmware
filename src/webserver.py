import machine

import asyncio
import os.path
import json

from microdot import Microdot, send_file
from microdot.websocket import with_websocket

from src.config import config, Config
import src.webconf as webconf


class WebServer(Microdot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cfg = None
        self.checkpoint_app = None

    def add_checkpoint_app_link(self, checkpoint_app):
        self.checkpoint_app = checkpoint_app

    def add_cfg_link(self, cfg:Config=config):
        self.cfg = cfg

    def refresh_cfg(self):
        if self.cfg is not None:
            self.cfg.load_ext_cfg()

    def get_battle_log_current_content(self) -> list|None:
        if self.checkpoint_app is not None:
            battle_logger = self.checkpoint_app.battle_logger
            return battle_logger.buf
        
    def get_voltage(self):
        return 3.3
        
    @property
    def battlelog_file(self) -> str|None:
        if self.checkpoint_app is not None:
            battle_logger = self.checkpoint_app.battle_logger
            return battle_logger.ext_log_file


web_server = WebServer()
web_server.add_cfg_link(config)

# add handlers here

# @web_server.get("/")
# def send_index(request):
#     self = request.app
#     return send_file(
#         webconf.WEB_MAIN_PATH
#     )


# @web_server.get("/assets/<path:path>")
# def send_assets(request, path):
#     self = request.app
#     return send_file(
#         os.path.join(
#             webconf.WEB_STATIC_FOLDER,
#             "assets",
#             path
#         )
#     )


@web_server.get(f"/{webconf.WEB_DOWNLOAD_LOG_ENDPOINT}")
def download_battle_log(request):
    self = request.app
    return send_file(
        self.battle_log_file
    )


@web_server.route("/ws")
@with_websocket
async def handle_ws(request, ws):
    self = request.app
    while True:
        data = await ws.receive()
        resp = None
        if data:
            parsed = json.loads(data)
            action = parsed.get("action")
            if action == "get_report":
                resp = json.dumps(
                    self.get_battle_log_current_content()
                )
            if action == "upload_config":
                cfg_data = parsed.get("content")
                try:
                    with open(self.cfg.external_cfg_path, "w") as f:
                        f.write(cfg_data)
                    self.cfg.load_ext_cfg()
                    resp = "Config upload success"
                except Exception as e:
                    resp = str(e)
            if action == "start_game":
                checkpoint_app = self.checkpoint_app
                if checkpoint_app.game_start and not checkpoint_app.game_end:
                    resp = "Permission error: game already in progress"
                else:
                    if isinstance(checkpoint_app.checkpoint_run_task, asyncio.Task):
                        await checkpoint_app.checkpoint_run_task.cancel()
                    checkpoint_app.checkpoint_run_task = asyncio.create_task(checkpoint_app.run())
                    resp = "Game task recreated"
            if action == "get_status":
                checkpoint_app = self.checkpoint_app
                result = {
                    "COLOR": checkpoint_app.color,
                    "LOG_PATH": checkpoint_app.battle_logger.ext_log_file,
                    "GAME_STARTED": checkpoint_app.game_start,
                    "GAME_FINISHED": checkpoint_app.game_end,
                    "BATTERY_VOLTAGE": self.get_voltage()
                }
                resp = json.dumps(result)
            if action == "reboot":
                await ws.send("Shutting down")
                machine.reset()
            if action == "echo":
                msg_data = parsed.get("content")
                await ws.send(msg_data)
            if resp is not None:
                await ws.send(resp)
