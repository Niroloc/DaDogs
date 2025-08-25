import logging
import sys
from traceback import format_exc

from config.constants import LOGS
from utils.bot import DaDogsBot
from setup_db import do_setup

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        filename=LOGS,
        format="%(pathname)s -- %(asctime)s -- [%(levelname)s] -- \"%(message)s \"")
    logging.info("Setting up db...")
    do_setup()
    logging.info("Db is settled")

    logging.info("Initializing bot...")
    try:
        bot = DaDogsBot()
    except:
        logging.error("Initializing bot failed!")
        logging.error(format_exc())
        sys.exit(1)

    logging.info("Starting service...")
    bot.run()
