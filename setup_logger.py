#!/usr/bin/env python3
from logging.handlers import TimedRotatingFileHandler
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if "DEBUG" in os.environ:
    logger.setLevel(logging.DEBUG)
filename = (f'logs/transactions-{datetime.now():%Y-%m-%w}.log')
formatter = logging.Formatter("%(asctime)s - %(message)s", "%Y-%m-%d:%H-%M-%S")
fileHandler = TimedRotatingFileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename),  when='midnight')
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)
