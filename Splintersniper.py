#!/usr/bin/env python3
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from beem.blockchain import Blockchain
from beem import Hive
from threading import Thread
import os
import sys
import json
import requests
import logging
import time
import enum

class SplinterlandsApiClient(object):

    def __init__(self) -> None:
        super().__init__()

    def _get_headers(self):
        return {
        }

    def _calculate_bcx_from_card(self, card, cardid):
        logger.debug("Enter calculate_bcx_from_card")
        alpha_bcx = 0
        alpha_dec = 0
        alpha_xp = 0
        if card["alpha_xp"] != None:
            alpha_xp = card["alpha_xp"]
            logger.debug(f"alpha_xp: {alpha_xp}")
        xp = max(card["xp"] - alpha_xp, 0)
        logger.debug(f"xp: {xp}")
        burn_rate = settings["dec"]["burn_rate"][card["details"]["rarity"] - 1]
        logger.debug(f"burn_rate: {burn_rate}")
        if card["edition"] == 4 or (card["details"]["tier"] != None and  card["details"]["tier"] >= 4):
            burn_rate = settings["dec"]["untamed_burn_rate"][card["details"]["rarity"] - 1]
            logger.debug(f"burn_rate: {burn_rate}")
        if (alpha_xp):
            alpha_bcx_xp = settings["alpha_xp"][card["details"]["rarity"] - 1]
            logger.debug(f"alpha_bcx_xp: {alpha_bcx_xp}")
            if card["gold"]:
                alpha_bcx_xp = settings["gold_xp"][card["details"]["rarity"] - 1]
                logger.debug(f"alpha_bcx_xp: {alpha_bcx_xp}")
            alpha_bcx = max(alpha_xp / alpha_bcx_xp, 1)
            logger.debug(f"alpha_bcx: {alpha_bcx}")
            if card["gold"]:
                alpha_bcx = max(alpha_xp / alpha_bcx_xp, 1)
                logger.debug(f"alpha_bcx: {alpha_bcx}")
            alpha_dec = burn_rate * alpha_bcx * settings["dec"]["alpha_burn_bonus"]
            logger.debug(f"alpha_dec: {alpha_dec}")
            if card["gold"]:
                alpha_dec *= settings["dec"]["gold_burn_bonus"]
                logger.debug(f"alpha_dec: {alpha_dec}")

        xp_property = "error"
        logger.debug(f"xp_property: {xp_property}")
        if card["edition"] == 0 or (card["edition"] == 2 and int(card["details"]["id"]) < 100):
            if card["gold"]:
                xp_property = "gold_xp"
                logger.debug(f"xp_property: {xp_property}")
            else:
                xp_property = "alpha_xp"
                logger.debug(f"xp_property: {xp_property}")
        else:
            if card["gold"]:
                xp_property = "beta_gold_xp"
                logger.debug(f"xp_property: {xp_property}")
            else:
                xp_property = "beta_xp"
                logger.debug(f"xp_property: {xp_property}")
        bcx_xp = settings[xp_property][card["details"]["rarity"] - 1]
        logger.debug(f"bcx_xp: {bcx_xp}")
        bcx = max((xp + bcx_xp) / bcx_xp, 1)
        logger.debug(f"bcx: {bcx}")
        if card["gold"]:
            bcx = max(xp / bcx_xp, 1)
            logger.debug(f"bcx: {bcx}")
        if card["edition"] == 4 or (card["details"]["tier"] != None and card["details"]["tier"] >= 4):
            bcx = card["xp"]
            logger.debug(f"bcx: {bcx}")
        if (alpha_xp):
            bcx = bcx - 1
            logger.debug(f"bcx: {bcx}")
        logger.info(str(cardid) + ": " + str(bcx) + "bcx")
        logger.debug("Exit calculate_bcx_from_card")
        return bcx

    def _calculate_bcx_from_cardID(self, cardid):
        logger.debug("Enter calculate_bcx_from_cardID")
        logger.debug(url_card_lookup + str(cardid))
        logger.info("Multi BCX card")
        response = requests.request("GET", url_card_lookup + str(cardid), headers=self._get_headers())
        logger.debug(f"response: {response}")
        card = json.loads(str(response.text))[0]
        logger.debug("card: {card}")
        logger.debug("Exit calculate_bcx_from_cardID")
        return self._calculate_bcx_from_card(card, cardid)

    def _calc_cp_per_usd(self, cardid, price_usd):
        logger.debug("Enter calc_cp_per_usd")
        response = requests.request("GET", url_card_lookup + str(cardid), headers=self._get_headers())
        logger.debug(f"response: {response}")
        card = json.loads(str(response.text))[0]
        logger.debug("card: {card}")
        bcx = self._calculate_bcx_from_card(card, cardid)
        logger.debug(f"bcx: {bcx}")
        alpha_bcx = 0
        alpha_dec = 0
        alpha_xp = 0
        if card["alpha_xp"] != None:
            alpha_xp = card["alpha_xp"]
            logger.debug("alpha_xp: {alpha_xp}")
        xp = max(card["xp"] - alpha_xp, 0)
        logger.debug("xp: {xp}")
        burn_rate = settings["dec"]["burn_rate"][card["details"]["rarity"] - 1]
        logger.debug(f"burn_rate: {burn_rate}")
        if card["edition"] == 4 or (card["details"]["tier"] != None and  card["details"]["tier"] >= 4):
            burn_rate = settings["dec"]["untamed_burn_rate"][card["details"]["rarity"] - 1]
            logger.debug(f"burn_rate: {burn_rate}")
        if (alpha_xp):
            alpha_bcx_xp = settings["alpha_xp"][card["details"]["rarity"] - 1]
            logger.debug(f"alpha_bcx_xp: {alpha_bcx_xp}")
            if card["gold"]:
                alpha_bcx_xp = settings["gold_xp"][card["details"]["rarity"] - 1]
                logger.debug(f"alpha_bcx_xp: {alpha_bcx_xp}")
            alpha_bcx = max(alpha_xp / alpha_bcx_xp, 1)
            logger.debug(f"alpha_bcx_xp: {alpha_bcx_xp}")
            if card["gold"]:
                alpha_bcx = max(alpha_xp / alpha_bcx_xp, 1)
                logger.debug(f"alpha_bcx: {alpha_bcx}")
            alpha_dec = burn_rate * alpha_bcx * settings["dec"]["alpha_burn_bonus"]
            if card["gold"]:
                alpha_dec *= settings["dec"]["gold_burn_bonus"]
                logger.debug(f"alpha_dec: {alpha_dec}")
        xp_property = "error"
        logger.debug(f"xp_property: {xp_property}")
        if card["edition"] == 0 or (card["edition"] == 2 and int(card["details"]["id"]) < 100):
            if card["gold"]:
                xp_property = "gold_xp"
                logger.debug(f"xp_property: {xp_property}")
            else:
                xp_property = "alpha_xp"
                logger.debug(f"xp_property: {xp_property}")
        else:
            if card["gold"]:
                xp_property = "beta_gold_xp"
                logger.debug(f"xp_property: {xp_property}")
            else:
                xp_property = "beta_xp"
                logger.debug(f"xp_property: {xp_property}")
        bcx_xp = settings[xp_property][card["details"]["rarity"] - 1]
        logger.debug(f"bcx_xp: {bcx_xp}")
        bcx = max((xp + bcx_xp) / bcx_xp, 1)
        logger.debug(f"bcx: {bcx}")
        if card["gold"]:
            bcx = max(xp / bcx_xp, 1)
            logger.debug(f"bcx: {bcx}")
        if card["edition"] == 4 or (card["details"]["tier"] != None and card["details"]["tier"] >= 4):
            bcx = card["xp"]
            logger.debug(f"bcx: {bcx}")
        if (alpha_xp):
            bcx = bcx - 1
            logger.debug(f"bcx: {bcx}")
        dec = burn_rate * bcx
        logger.debug(f"bcx: {bcx}")
        if (card["gold"]):
            gold_burn_bonus_prop = "gold_burn_bonus"
            if card["details"]["tier"] != None and card["details"]["tier"] >= 7:
              gold_burn_bonus_prop = "gold_burn_bonus_2"
            dec *= settings["dec"][gold_burn_bonus_prop]
        if (card["edition"] == 0):
            dec *= settings["dec"]["alpha_burn_bonus"]
        if (card["edition"] == 2):
            dec *= settings["dec"]["promo_burn_bonus"]
        total_dec = dec + alpha_dec
        #if (card.xp >= getMaxXp(details, card.edition, card.gold)):
         # total_dec *= SM.settings.dec.max_burn_bonus;
        if (card["details"]["tier"] != None and card["details"]["tier"] >= 7):
            total_dec = total_dec / 2;
        logger.debug("Exit calc_cp_per_usd")
        return total_dec / price_usd

    def check_desired(self, listing, trx_id, price, cardid):
        logger.debug("Enter check_desired")
        if str(listing["cards"])[4] != "-":
            logger.warning("unable to parse: " + str(listing["cards"])[2:-2] +  ", looking up cardid...")
            response = requests.request("GET", url_card_lookup + (str(listing["cards"])[2:-2]), headers=self._get_headers())
            card = json.loads(str(response.text))
            logger.debug(f"card: {card}")
            cardid = str(card[0]["card_detail_id"])
            logger.debug(f"cardid: {cardid}")
        if len(cardid) > 3:
            raise Exception("skipping card set...")
        for buyconfig in buyconfigs:
            if ((float(buyconfig["max_quantity"]) > 0)
            and (cardid in buyconfig["cards"])
            and (price <= float(buyconfig["prices"][cardid]))
            and (price <= float(buyconfig["max_price"]))
            and ((not buyconfig["gold_only"]) or (str(listing["cards"])[2] == "G"))
            and (buyconfig["min_bcx"] == 0 or self._calculate_bcx_from_cardID(str(listing["cards"])[2:-2]) >= buyconfig["min_bcx"])
            and (buyconfig["min_cp_per_usd"] == 0 or self._calc_cp_per_usd(str(listing["cards"])[2:-2], price) >= buyconfig["min_cp_per_usd"])):
                buyconfig["max_quantity"] = buyconfig["max_quantity"] - 1
                currently_buying.append({"id": trx_id, "buyconfig_idx": buyconfigs.index(buyconfig), "cardid": str(listing["cards"])[2:-2]})
                logger.info("Card ID: " + cardid + " IS desired at $" + str(price))
                logger.debug("Exit check_desired")
                return True
        logger.info("Card ID: " + cardid + " is not desired at $" + str(price))
        logger.debug("Exit check_desired")
        return False

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
                for buy in currently_buying:
                  if((str(buy["id"])) in buydata["items"]):
                    logger.info("bought card " + str(buy["cardid"]) +  " for: " + str(res["total_usd"]) + "$")
                    if auto_set_buy_price:
                      new_price = float(res["total_usd"])  + (float(res["total_usd"]) * (sellpct / 100))
                      logger.debug(f"new_price: {new_price}")
                      jsondata = '{"cards":["' + str(buy["cardid"]) + '"],"currency":"USD","price":' + str(new_price) +',"fee_pct":500}'
                      logger.debug(f"jsondata: {jsondata}")
                      hive.custom_json('sm_sell_cards', json_data=jsondata, required_auths=[HIVE_USERNAME])
                      logger.info("selling " + str(buy["cardid"]) + " for " + str(new_price) + "$")
                      currently_selling.append(str(buy["cardid"]))
                    elif buyconfigs[buy["buyconfig_idx"]]["sell_for_pct_more"] > 0:
                      new_price = float(res["total_usd"])  + (float(res["total_usd"]) * (buyconfigs[buy["buyconfig_idx"]]["sell_for_pct_more"] / 100))
                      logger.debug(f"new_price: {new_price}")
                      jsondata = '{"cards":["' + str(buy["cardid"]) + '"],"currency":"USD","price":' + str(new_price) +',"fee_pct":500}'
                      logger.debug(f"jsondata: {jsondata}")
                      hive.custom_json('sm_sell_cards', json_data=jsondata, required_auths=[HIVE_USERNAME])
                      logger.info("selling " + str(buy["cardid"]) + " for " + str(new_price) + "$")
                      currently_selling.append(str(buy["cardid"]))
                    print("############################")
                    currently_buying.remove(buy)
                    logger.debug("Exit check_buying_result")
              else:
                for buy in currently_buying:
                  if((str(buy["id"])) in buydata["items"]):
                    buyconfigs[buy["buyconfig_idx"]]["max_quantity"] = buyconfigs[buy["buyconfig_idx"]]["max_quantity"] + 1
                    logger.error("buy failed: " + str(data["trx_info"]["error"]))
                    currently_buying.remove(buy)
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
          if entry["card_id"] in currently_selling and entry["type"] == "SELL":
            currently_selling.remove(entry["card_id"])
            logger.info("card " + str(entry["card_id"]) + "sold, sending " + str(tip_pct) + " tip")
            if tip_pct > 0:
              hive.custom_json('sm_token_transfer', json_data={"to":"edition-x","qty":float(entry["payment"][:-4]) * (tip_pct/100),"token":"DEC"}, required_auths=[HIVE_USERNAME])
        logger.debug("Exit check_for_sold")

    def check_prices(self):
        logger.debug("Enter check_prices")
        url_prices = "https://api.splinterlands.io/market/for_sale_grouped"
        for buyconfig in buyconfigs:
          buyconfig["prices"] = {}
        if auto_set_buy_price:
            logger.info("checking prices...")
            response = requests.request("GET", url_prices, headers=self._get_headers())
            logger.debug(f"response: {response}")
            try:
                cardsjson = json.loads(str(response.text))
            except Exception as e:
                logger.exception("error occured while checking prices with cardsjson: "  + repr(e))
            logger.debug(f"cardsjson: {cardsjson}")
            for buyconfig in buyconfigs:
              for card in cardsjson:
                if str(card["card_detail_id"]) in buyconfig["cards"] and card["gold"] == buyconfig["gold_only"]:
                  buyconfig["prices"][str(card["card_detail_id"])] = (card["low_price"] * (1 - (buypct / 100)))
            logger.debug("Exit check_prices")
            return
        else:
            for buyconfig in buyconfigs:
                for cardid in buyconfig["cards"]:
                    buyconfig["prices"][cardid] = buyconfig["max_price"]
            logger.debug("Exit check_prices")
            return

def get_config_vars():
    logger.debug("Enter get_config_vars")
    f = open(os.path.join(THIS_FOLDER, 'config.json'))
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

def get_cards_to_buy():
    logger.debug("Enter get_cards_to_buy")
    rarities = {
      1: "common",
      2: "rare",
      3: "epic",
      4: "legendary"
    }

    colors = {
      "Red": "fire",
      "Blue": "water",
      "Green": "earth",
      "White": "life",
      "Black": "death",
      "Gold": "dragon",
      "Gray": "neutral"
    }

    editions = {
      "alpha": 0,
      "beta": 1,
      "promo": 2,
      "reward": 3,
      "untamed": 4,
      "dice": 5,
      "chaos": 7
    }
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
            buyconfig["cards"] =  all_eds
    logger.debug("Exit get_cards_to_buy")
    return

def run():
    last_checked = time.time()
    for op in stream:
        if(time.time() - last_checked) > 600:
            logger.info(time.time())
            logger.info(last_checked)
            if auto_set_buy_price:
              client.check_prices()
            client.check_for_sold()
            last_checked = time.time()
        if(op["type"] == 'custom_json'):
            if op["id"] == 'sm_sell_cards' and HIVE_USERNAME not in op["required_auths"]:
              try:
                  listings = []
                  if(op["json"][:1] == '[' ):
                      str_listings = op["json"].strip().replace(" ", "").replace("'", "")
                      listings = json.loads(str_listings)
                  else:
                      listings.append(json.loads(op["json"]))
                  for index, listing in enumerate(listings):
                    price = float(listing["price"])
                    cardid = str(listing["cards"])[5:-13]
                    if (client.check_desired(listing, op["trx_id"] + "-" + str(index), price, cardid) == True):
                        id = op["trx_id"]
                        jsondata_old = '{"items":["'+ str(id) + '-' + str(index) + '"], "price":' + str(price) +', "currency":"' + str(currency) + '"}'
                        hive.custom_json('sm_market_purchase', json_data=jsondata_old, required_auths=[HIVE_USERNAME])
                        logger.info(str(listing["cards"])[2] + "-" + cardid + " $" + str(price) + " - buying...")
              except Exception as e:
                  logger.exception("error occured while checking cards: "  + repr(e))
            else:
              if(len(currently_buying) > 0 and HIVE_USERNAME in op["required_auths"]):
                  try:
                      t = Thread(target = client.check_buying_result(op))
                      t.start()
                  except Exception as e:
                      logger.exception("error occured while buying: "  + repr(e))

if __name__ == '__main__':
    ## Setup logging
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    if "DEBUG" in os.environ:
        logger.setLevel(logging.DEBUG)
    filename = (f'transactions-{datetime.now():%Y-%m-%w}.log')
    formatter = logging.Formatter("%(asctime)s - %(message)s", "%Y-%m-%d:%H-%M-%S")
    fileHandler = TimedRotatingFileHandler(os.path.join(THIS_FOLDER, filename),  when='midnight')
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)
    ## Get configuration variables from config.json
    buyconfigs, currency, auto_set_buy_price, buypct, sellpct, tip_pct = get_config_vars()
    ## Get Hive details from environment variables
    try:
        HIVE_USERNAME = os.environ['HIVE_USERNAME']
        HIVE_ACTIVE_KEY = os.environ['HIVE_ACTIVE_KEY']
    except KeyError:
        logger.error("Please set the following environment variables: [HIVE_USERNAME, HIVE_ACTIVE_KEY]")
        sys.exit(1)

    hive = Hive(keys=HIVE_ACTIVE_KEY)
    url_settings = "https://steemmonsters.com/settings"
    url_card_lookup = "https://steemmonsters.com/cards/find?ids="
    url_legs = "https://api.splinterlands.io/cards/get_details"
    headers = {
        }
    settings = json.loads(requests.request("GET", url_settings, headers=headers).text)
    response = requests.request("GET", url_legs, headers=headers)
    cardsjson = json.loads(str(response.text))
    currently_buying = []
    currently_selling = []

    logger.info("starting...")
    get_cards_to_buy()
    client = SplinterlandsApiClient()
    client.check_prices()
    blockchain = Blockchain(blockchain_instance=hive, mode="head")
    stream = blockchain.stream()
    run()
