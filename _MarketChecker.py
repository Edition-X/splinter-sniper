import json
import requests
import time
import logging
import os

from beem import Hive
from setup_logger import get_logger

logger = get_logger(__name__)

class MarketChecker:
    def __init__(self, buyconfigs, currently_buying, auto_set_buy_price, sellpct, currently_selling, tip_pct):
        self.buyconfigs = buyconfigs
        self.currently_buying = currently_buying
        self.currently_selling = currently_selling
        self.auto_set_buy_price = auto_set_buy_price
        self.sellpct = sellpct
        self.tip_pct = tip_pct

        # Get Hive details from configuration file
        try:
            with open("config.json", "r") as config_file:
                config = json.load(config_file)
                HIVE_USERNAME = config["HIVE_USERNAME"]
                HIVE_ACTIVE_KEY = config["HIVE_ACTIVE_KEY"]
        except (FileNotFoundError, KeyError) as e:
            logger.error("Please make sure that the config.json file exists and contains the necessary keys.")
            sys.exit(1)
        
        self.hive = Hive(keys=HIVE_ACTIVE_KEY)
        self.blockchain = Blockchain(blockchain_instance=self.hive, mode="head")

    def _get_headers(self):
        return {
        }

    def check_buying_result(self, txa):
        """
        Check the result of a purchase on the Steem Monsters platform and potentially sell the purchased card.

        Parameters:
            txa (dict): Transaction object containing the transaction ID to check.

        Returns:
            None
        """
        logger.debug("Enter check_buying_result")
        n = 3
        url_purchase = "https://steemmonsters.com/transactions/lookup?trx_id="
        while n > 0:
            try:
                response = requests.request("GET", f"{url_purchase}{txa['trx_id']}", headers=self._get_headers())
                data = json.loads(response.text)
                if "trx_info" in data:
                    n = 0
                    buydata = json.loads(data["trx_info"]["data"])
                    if data["trx_info"]["success"]:
                        res = json.loads(data["trx_info"]["result"])
                        logger.info(f"{url_purchase}{txa['trx_id']}")
                        logger.info(f"Successfully bought card for: {res['total_dec']}DEC")
                        for buy in self.currently_buying:
                            if str(buy["id"]) in buydata["items"]:
                                logger.info(f"Bought card {buy['cardid']} for: {res['total_usd']}$")
                                if self.auto_set_buy_price and
                                    new_price = float(res["total_usd"]) + (float(res["total_usd"]) * (self.sellpct / 100))
                                    jsondata = f'{"cards":["{buy["cardid"]}"],"currency":"USD","price":{new_price},"fee_pct":500}'
                                    self.hive.custom_json("sm_sell_cards", json_data=jsondata, required_auths=[HIVE_USERNAME])
                                    logger.info(f"Selling {buy['cardid']} for {new_price}$")
                                    self.currently_selling.append(str(buy["cardid"]))
                                elif self.buyconfigs[buy["buyconfig_idx"]]["sell_for_pct_more"] > 0:
                                    new_price = float(res["total_usd"]) + (float(res["total_usd"]) * (self.buyconfigs[buy["buyconfig_idx"]]["sell_for_pct_more"] / 100))
                                    jsondata = f'{"cards":["{buy["cardid"]}"],"currency":"USD","price":{new_price},"fee_pct":500}'
                                    self.hive.custom_json("sm_sell_cards", json_data=jsondata, required_auths=[HIVE_USERNAME])
                                    logger.info(f"Selling {buy['cardid']} for {new_price}$")
                                    self.currently_selling.append(str(buy["cardid"]))
            except Exception as e:
                n -= 1
                logger.error(f"Error occurred while checking buying result: {e}")
                time.sleep(1)
        else:
            logger.error(f"Failed to check buying result for transaction {txa['trx_id']} after 3 attempts")

    def check_for_sold(self):
        """
        Check if any of the cards currently being sold have been sold.

        Returns:
            None
        """
        logger.debug("Enter check_for_sold")
        for sell in self.currently_selling:
            card = self.hive.get_market_history(sell, 1)
            if len(card) > 0:
                if card[0]["highest_bid"] == 0:
                    logger.info(f"{sell} has been sold")
                    self.currently_selling.remove(sell)


