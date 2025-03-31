from machine import Timer

import logging

import config as cfg
import helpers


# setup
logger = logging.getLogger(cfg.DEVICE_ID)
helpers.sync_machine_time()

try:
    debounce_timer = Timer(cfg.BUTTONS_DEBOUNCE_TIMER_ID)
    helpers.make_wlan()

    led_panel = helpers.attach_led()
    button_pad = helpers.attach_buttons(debounce_timer)
    battle_logger = helpers.init_battlelogger()

    current_faction = button_pad._cname
    logger.info(f"Button pad initial state: {current_faction}")
    led_panel.on()
    game_start = False
    game_end = False
    stop_game_flag = False
    start_game_flag = False

    logger.info("Main module init finished")

    # game waiting loop
    with helpers.PeriodicExecutor(period_seconds=600, timer_id=0) as cron_600:
        with helpers.PeriodicExecutor(period_seconds=60, timer_id=1) as cron_60:
            logger.info("Game start pending")
            battle_logger.log(
                faction_id="SYSTEM",
                event="Game start pending"
            )
            while not game_start:
                cron_600.execute_if_alarm(
                    helpers.sync_machine_time
                )
                results = cron_60.execute_if_alarm(
                    helpers.check_game_start
                )
                game_start = results[0] or start_game_flag

    # game loop
    with helpers.PeriodicExecutor(cfg.BATTLELOG_BACKUP_PERIOD, timer_id=0) as cron_600:
        with helpers.PeriodicExecutor(period_seconds=60, timer_id=1) as cron_60:
            logger.info("Game started")
            battle_logger.log(
                faction_id="SYSTEM",
                event="Game started"
            )
            while not game_end:
                cron_600.execute_if_alarm(
                    battle_logger.save_backup,
                    helpers.sync_machine_time
                )
                results = cron_60.execute_if_alarm(
                    helpers.check_game_end
                )
                game_end = results[0] or stop_game_flag
                button_pad.check_pressed()
                if button_pad._cname != current_faction:
                    current_faction = button_pad._cname
                    logger.info(f"Button pad state changed: {current_faction}")
                    led_panel.on(rgb=button_pad.color)
                    battle_logger.log(
                        faction_id=current_faction.upper(),
                        event="Capture checkpoint"
                    )

    # teardown
    battle_logger.end()
    led_panel.on(cname=cfg.NEUTRAL_COLOR)
    logger.info("Game finished")
    battle_logger.log(
        faction_id="SYSTEM",
        event="Game finished"
    )
except Exception as e:
    logger.exception(e)
    raise
finally:
    debounce_timer.deinit()
