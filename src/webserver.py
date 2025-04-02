import os.path

from microdot import Microdot, send_file
from microdot.websocket import with_websocket

from src.config import config, Config


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
        
    @property
    def battlelog_file(self) -> str|None:
        if self.checkpoint_app is not None:
            battle_logger = self.checkpoint_app.battle_logger
            return battle_logger.ext_log_file


web_server = WebServer()
web_server.add_cfg_link(config)

# add handlers here

@web_server.get("/")
def send_index(request):
    self = request.app
    return send_file(
        self.cfg.WEB_MAIN_PATH
    )


@web_server.get("/assets/<path:path>")
def send_assets(request, path):
    self = request.app
    return send_file(
        os.path.join(
            self.cfg.WEB_STATIC_FOLDER,
            "assets",
            path
        )
    )


@web_server.get("/battle_log")
def download_battle_log(request):
    self = request.app
    return send_file(
        self.battle_log_file
    )


@web_server.route("/ws")
@with_websocket
async def handle_ws(request, ws):
    while True:
        data = await ws.receive()
        if data:
            action = json.loads(data).get("action")
            if action == "upload_config":
                await ws.send("config")
