#!/usr/bin/env python3
from setup_logger import logger
from setup_hive import HIVE_USERNAME, hive, blockchain
from SplinterlandsSDK import Api, Card
from MarketCalculator import MarketCalculator
from MarketChecker import MarketChecker
from threading import Thread
import os
import json
import time

# test
def get_config_vars():
    logger.debug("Enter get_config_vars")
    f = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json'))
    configfile = json.load(f)
    buyconfigs = configfile["buyconfigs"]
    currency = configfile["global_params"]["currency"]
    auto_set_buy_price = configfile["global_params"]["auto_set_buy_price"]
    buypct = configfile["global_params"]["buy_pct_below_market"]
    sellpct = configfile["global_params"]["sell_pct_above_buy"]
    tip_pct = configfile["global_params"]["tip_pct_of_profit"]
    f.close()
    logger.debug("Exit get_config_vars")
    return buyconfigs, currency, auto_set_buy_price, buypct, sellpct, tip_pct

def get_cards_to_buy(buyconfigs, cardsjson):
    logger.debug("Enter get_cards_to_buy")
    rarities  = Card.get_rarities()
    colors = Card.get_colors()
    editions = Card.get_editions()
    for buyconfig in buyconfigs:
        if(buyconfig["exclude_cl"]):
            cards_tmp = [card for card in cardsjson if rarities[card["rarity"]] in buyconfig["rarities"]
                         and colors[str(card["color"])] in buyconfig["elements"]
                         and str(card["type"]).lower() in str(buyconfig["types"]).lower() and int(card["id"]) < 330]
        else:
            cards_tmp = [card for card in cardsjson if rarities[card["rarity"]] in buyconfig["rarities"]
                         and colors[str(card["color"])] in buyconfig["elements"]
                         and str(card["type"]).lower() in str(buyconfig["types"]).lower()]
        all_eds = []
        for ed in buyconfig["editions"]:
            current_ed = [str(card["id"]) for card in cards_tmp if str(editions[str(ed)]) in card["editions"]]
            all_eds = all_eds + current_ed
        if len(buyconfig["cards"]) == 0:
            buyconfig["cards"] = all_eds
    logger.debug("Exit get_cards_to_buy")
    return

def main():
    # Get configuration variables from config.json
    buyconfigs, currency, auto_set_buy_price, buypct, sellpct, tip_pct = get_config_vars()
    currently_buying = []
    currently_selling = []

    logger.info("starting...")
    api = Api()
    calculator = MarketCalculator(api, buyconfigs, currently_buying, auto_set_buy_price, buypct)
    get_cards_to_buy(buyconfigs, calculator.cardsjson)
    calculator.check_prices()
    stream = blockchain.stream()
    checker = MarketChecker(api, buyconfigs, currently_buying, auto_set_buy_price, sellpct, currently_selling, tip_pct)
    last_checked = time.time()
    buying_dict = {"block_num": 0, "json_data": {}}
    purchaseOrderFlag = 0
    for op in stream:
        newBlock = op["block_num"] - buying_dict["block_num"]
        if buying_dict["block_num"] != 0:
            if newBlock >= 3 and purchaseOrderFlag == 0:
                hive.custom_json('sm_market_purchase', json_data=buying_dict["json_data"],
                                 required_auths=[HIVE_USERNAME])
                purchaseOrderFlag = 1

        if(time.time() - last_checked) > 600:
            logger.info(time.time())
            logger.info(last_checked)
            if auto_set_buy_price:
                calculator.check_prices()
            checker.check_for_sold()
            last_checked = time.time()
        if(op["type"] == 'custom_json'):
            if op["id"] == 'sm_sell_cards' and HIVE_USERNAME not in op["required_auths"]:
                try:
                    listings = []
                    if(op["json"][:1] == '['):
                        str_listings = op["json"].strip().replace(" ", "").replace("'", "")
                        listings = json.loads(str_listings)
                    else:
                        listings.append(json.loads(op["json"]))
                    for index, listing in enumerate(listings):
                        price = float(listing["price"])
                        cardid = str(listing["cards"])[5:-13]
                        if (calculator.calculate_desired(listing, op["trx_id"] + "-" + str(index), price, cardid) == True):
                            id = op["trx_id"]
                            jsondata_old = '{"items":["' + str(id) + '-' + str(index) + '"], "price":' + str(
                                price) + ', "currency":"' + str(currency) + '"}'

                            buying_dict["block_num"] = op["block_num"]
                            buying_dict["json_data"] = jsondata_old

                            logger.info(str(listing["cards"])[2] + "-" + cardid + " $" + str(price) + " - buying...")
                            purchaseOrderFlag = 0

                except Exception as e:
                    logger.exception("error occured while checking cards: " + repr(e))
            else:
                if(len(currently_buying) > 0 and HIVE_USERNAME in op["required_auths"]):
                    try:
                        t = Thread(target=checker.check_buying_result(op))
                        t.start()
                    except Exception as e:
                        logger.exception("error occured while buying: " + repr(e))


if __name__ == '__main__':
    main()
