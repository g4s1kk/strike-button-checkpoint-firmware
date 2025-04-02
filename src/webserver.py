import microdot
from microdot import websocket

from src.config import config, Config


class WebServer(microdot.Microdot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_checkpoint_app_link(self, checkpoint_app):
        self.checkpoint_app = checkpoint_app

    def add_cfg_link(self, cfg:Config=config):
        self.cfg = cfg

web_server = WebServer()
web_server.add_cfg_link(config)

# add handlers here

@web_server.get("/")
def send_frontend(request):

