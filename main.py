import asyncio
import aiorepl
import micropython
from machine import Timer

import logging

import src.app as app
import src.helpers as helpers
from src.config import config as cfg
import src.webconf as webconf
from src.webserver import web_server


# setup
micropython.alloc_emergency_exception_buf(100)

logger = logging.getLogger(cfg.DEVICE_ID)
helpers.sync_machine_time()


# SPLIT LOG BACKUPS TASK AND RTC SYNC TASK, SYNC IT WITH MAIN LOOP
# FINISH BACKUPS TASK ON GAME END (MAYBE RUN IT INSIDE GAME RUN LOOP)

async def main(
        checkpoint_app:app.CheckpointApp,
        web_server
    ):
    sync_time_task = asyncio.create_task(helpers.periodical_sync_machine_time())
    checkpoint_app.checkpoint_run_task = asyncio.create_task(checkpoint_app.run())
    ws = asyncio.create_task(
        web_server.start_server(
            host=webconf.BACKEND_IP_ADDR,
            port=webconf.WEB_PORT
        )
    )
    repl = asyncio.create_task(aiorepl.task())
    tasks = [
        sync_time_task,
        checkpoint_app.checkpoint_run_task,
        ws,
        repl
    ]  
    asyncio.gather(*tasks)

try:
    debounce_timer = Timer(cfg.BUTTONS_DEBOUNCE_TIMER_ID)
    station = helpers.make_wlan()

    checkpoint_app = app.CheckpointApp(
        debounce_timer=debounce_timer
    )
    
    web_server.add_checkpoint_app_link(checkpoint_app)

    logger.info("Main module init finished")

    asyncio.run(
        main(
            checkpoint_app,
            web_server
        )
    )

except Exception as e:
    logger.exception(e)
    raise

finally:
    debounce_timer.deinit()
