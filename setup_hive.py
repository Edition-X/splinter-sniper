#!/usr/bin/env python3
from beem.blockchain import Blockchain
from beem import Hive
from setup_logger import logger
import sys
import os

 ## Get Hive details from environment variables
try:
    HIVE_USERNAME = os.environ['HIVE_USERNAME']
    HIVE_ACTIVE_KEY = os.environ['HIVE_ACTIVE_KEY']
except KeyError:
    logger.error("Please set the following environment variables: [HIVE_USERNAME, HIVE_ACTIVE_KEY]")
    sys.exit(1)
hive = Hive(keys=HIVE_ACTIVE_KEY)
blockchain = Blockchain(blockchain_instance=hive, mode="head")
