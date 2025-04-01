import asyncio
from machine import Timer

import logging

import src.app as app
import src.config as cfg
import src.helpers as helpers
from src.webserver import web_server


# setup
logger = logging.getLogger(cfg.DEVICE_ID)
helpers.sync_machine_time()

async def main(
        checkpoint_app:app.CheckpointApp,
        web_server,
        battle_logger
    ):
    periodic_task = asyncio.create_task(
        helpers.do_periodical_job(battle_logger)
    )
    checkpoint_run_task = asyncio.create_task(checkpoint_app.run())
    asyncio.create_task(web_server.start_http_server())
    await checkpoint_run_task
    periodic_task.cancel()


try:
    debounce_timer = Timer(cfg.BUTTONS_DEBOUNCE_TIMER_ID)
    helpers.make_wlan()

    battle_logger = helpers.init_battlelogger()

    checkpoint_app = app.CheckpointApp(
        debounce_timer=debounce_timer,
        battle_logger=battle_logger
    )

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
