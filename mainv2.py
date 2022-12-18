#!/usr/bin/env python3
from setup_logger import logger
from SplinterlandsAPI import SplinterlandsAPI
from MarketCalculator import MarketCalculator
import os
import json

def get_config_vars():
    logger.debug("Enter get_config_vars")
    f = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json'))
    configfile = json.load(f)
    buyconfigs = configfile["buyconfigs"]
    auto_set_buy_price = configfile["global_params"]["auto_set_buy_price"]
    buypct = configfile["global_params"]["buy_pct_below_market"]
    f.close()
    logger.debug("Exit get_config_vars")
    return buyconfigs, auto_set_buy_price, buypct

def main():
    currently_buying = []
    buyconfigs, auto_set_buy_price, buypct = get_config_vars()
    logger.info("Starting...")
    api = SplinterlandsAPI()
    calculator = MarketCalculator(api, buyconfigs, currently_buying, auto_set_buy_price, buypct)
    # calculator.check_prices()

if __name__ == "__main__":
    main()

