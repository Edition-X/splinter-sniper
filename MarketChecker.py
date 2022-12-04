#!/usr/bin/env python3
from setup_logger import logger
from setup_hive import hive, HIVE_USERNAME
import json
import requests
import time

class MarketChecker:

    def __init__(self, buyconfigs, currently_buying, auto_set_buy_price, sellpct, currently_selling, tip_pct):

        self.buyconfigs = buyconfigs
        self.currently_buying = currently_buying
        self.currently_selling = currently_selling
        self.auto_set_buy_price = auto_set_buy_price
        self.sellpct = sellpct
        self.tip_pct = tip_pct

    def _get_headers(self):
        return {
        }

    def check_buying_result(self, txa) -> None:
        logger.debug("Enter check_buying_result")
        n = 3
        url_purchase: str = "https://steemmonsters.com/transactions/lookup?trx_id="
        while n > 0:
            response = requests.request("GET", "".join([url_purchase, txa["trx_id"]]), headers=self._get_headers())
            logger.debug(f"response: {response}")
            data = json.loads(response.text)
            logger.debug(f"data: {data}")
            if "trx_info" in data:
              n = 0
              buydata = json.loads(data["trx_info"]["data"])
              logger.debug(f"buydata: {buydata}")
              if(data["trx_info"]["success"] == True):
                res = json.loads(data["trx_info"]["result"])
                logger.debug(f"res: {res}")
                logger.info("".join([url_purchase, txa["trx_id"]]))
                print("############################")
                logger.info("successfully bought card for: " + str(res["total_dec"]) + "DEC")
                logger.info(str(url_purchase) + str(txa["trx_id"]))
                for buy in self.currently_buying:
                  if((str(buy["id"])) in buydata["items"]):
                    logger.info("bought card " + str(buy["cardid"]) +  " for: " + str(res["total_usd"]) + "$")
                    if self.auto_set_buy_price and self.buyconfigs[buy["buyconfig_idx"]]["sell_for_pct_more"] > 0:
                      new_price = float(res["total_usd"])  + (float(res["total_usd"]) * (self.sellpct / 100))
                      logger.debug(f"new_price: {new_price}")
                      jsondata = '{"cards":["' + str(buy["cardid"]) + '"],"currency":"USD","price":' + str(new_price) +',"fee_pct":500}'
                      logger.debug(f"jsondata: {jsondata}")
                      hive.custom_json('sm_sell_cards', json_data=jsondata, required_auths=[HIVE_USERNAME])
                      logger.info("selling " + str(buy["cardid"]) + " for " + str(new_price) + "$")
                      self.currently_selling.append(str(buy["cardid"]))
                    elif self.buyconfigs[buy["buyconfig_idx"]]["sell_for_pct_more"] > 0:
                      new_price = float(res["total_usd"])  + (float(res["total_usd"]) * (self.buyconfigs[buy["buyconfig_idx"]]["sell_for_pct_more"] / 100))
                      logger.debug(f"new_price: {new_price}")
                      jsondata = '{"cards":["' + str(buy["cardid"]) + '"],"currency":"USD","price":' + str(new_price) +',"fee_pct":500}'
                      logger.debug(f"jsondata: {jsondata}")
                      hive.custom_json('sm_sell_cards', json_data=jsondata, required_auths=[HIVE_USERNAME])
                      logger.info("selling " + str(buy["cardid"]) + " for " + str(new_price) + "$")
                      self.currently_selling.append(str(buy["cardid"]))
                    print("############################")
                    self.currently_buying.remove(buy)
                    logger.debug("Exit check_buying_result")
              else:
                for buy in self.currently_buying:
                  if((str(buy["id"])) in buydata["items"]):
                    self.buyconfigs[buy["buyconfig_idx"]]["max_quantity"] = self.buyconfigs[buy["buyconfig_idx"]]["max_quantity"] + 1
                    logger.error("buy failed: " + str(data["trx_info"]["error"]))
                    self.currently_buying.remove(buy)
                    logger.debug("Exit check_buying_result")
            else:
              n -= 1
              time.sleep(1)
              logger.debug("Exit check_buying_result")

    def check_for_sold(self) -> None:
        logger.debug("Enter check_for_sold")
        url_player_trx: str = "https://api2.splinterlands.com/market/history?player="
        response = requests.request("GET", url_player_trx + str(HIVE_USERNAME), headers=self._get_headers())
        logger.debug(f"response: {response}")
        history = json.loads(response.text)
        logger.debug(f"history: {history}")
        for entry in history:
          if entry["card_id"] in self.currently_selling and entry["type"] == "SELL":
            self.currently_selling.remove(entry["card_id"])
            logger.info("card " + str(entry["card_id"]) + "sold, sending " + str(self.tip_pct) + " tip")
            if self.tip_pct > 0:
              hive.custom_json('sm_token_transfer', json_data={"to":"edition-x","qty":float(entry["payment"][:-4]) * (self.tip_pct/100),"token":"DEC"}, required_auths=[HIVE_USERNAME])
        logger.debug("Exit check_for_sold")
