#!/usr/bin/env python3
from setup_logger import logger
from setup_hive import hive, HIVE_USERNAME
import json
import requests
import time

class MarketChecker:

    def __init__(self, api, buyconfigs, currently_buying, auto_set_buy_price, sellpct, currently_selling, tip_pct):
        self.api                = api
        self.buyconfigs         = buyconfigs
        self.currently_buying   = currently_buying
        self.currently_selling  = currently_selling
        self.auto_set_buy_price = auto_set_buy_price
        self.sellpct            = sellpct
        self.tip_pct            = tip_pct

    def _get_headers(self):
        return {
        }

    def check_buying_result(self, txa, dry_run) -> None:
        logger.debug("Enter check_buying_result")
        n = 3
        while n > 0:
            data = self.api.get_transaction(txa["trx_id"])
            logger.debug(f"data: {data}")
            if "trx_info" in data:
              n = 0
              buydata = json.loads(data["trx_info"]["data"])
              if(data["trx_info"]["success"] == True):
                res = json.loads(data["trx_info"]["result"])
                logger.info(f"Transaction ID: {txa['trx_id']}")
                print("############################")
                logger.info("successfully bought card for: " + str(res["total_dec"]) + "DEC")
                for buy in self.currently_buying:
                  if((str(buy["id"])) in buydata["items"]):
                    logger.info("bought card " + str(buy["cardid"]) +  " for: " + str(res["total_usd"]) + "$")
                    if self.auto_set_buy_price and self.buyconfigs[buy["buyconfig_idx"]]["sell_for_pct_more"] > 0:
                      new_price = float(res["total_usd"])  + (float(res["total_usd"]) * (self.sellpct / 100))
                      logger.debug(f"new_price: {new_price}")
                      jsondata = '{"cards":["' + str(buy["cardid"]) + '"],"currency":"USD","price":' + str(new_price) +',"fee_pct":500}'
                      logger.debug(f"jsondata: {jsondata}")
                      if dry_run:
                          with open("dry_run_transactions.txt", "w") as f:
                              f.write(f"selling data: {jsondata}\n")
                      else:
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
        history = self.api.get_player_market_history(HIVE_USERNAME)
        for entry in history:
          if entry["card_id"] in self.currently_selling and entry["type"] == "SELL":
            self.currently_selling.remove(entry["card_id"])
            logger.info("card " + str(entry["card_id"]) + "sold, sending " + str(self.tip_pct) + " tip")
            if self.tip_pct > 0:
              hive.custom_json('sm_token_transfer', json_data={"to":"edition-x","qty":float(entry["payment"][:-4]) * (self.tip_pct/100),"token":"DEC"}, required_auths=[HIVE_USERNAME])
        logger.debug("Exit check_for_sold")
