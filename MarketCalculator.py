#!/usr/bin/env python3
from setup_logger import logger
import json
import requests
import sys

class MarketCalculator:

    def __init__(self, api, buyconfigs, currently_buying, auto_set_buy_price, buypct):

        self.api                = api
        self.settings           = self.api.get_settings()
        self.cardsjson          = self.api.get_cards()
        self.buyconfigs         = buyconfigs
        self.currently_buying   = currently_buying
        self.auto_set_buy_price = auto_set_buy_price
        self.buypct             = buypct

    def _calculate_bcx_from_card(self, card, cardid):
        logger.debug("Enter calculate_bcx_from_card")
        alpha_bcx = 0
        alpha_dec = 0
        alpha_xp = 0
        if alpha_xp in card:
            alpha_xp = card["alpha_xp"]
            logger.debug(f"alpha_xp: {alpha_xp}")
        xp = max(card["xp"] - alpha_xp, 0)
        logger.debug(f"xp: {xp}")
        burn_rate = self.settings["dec"]["burn_rate"][card["details"]["rarity"] - 1]
        logger.debug(f"burn_rate: {burn_rate}")
        if card["edition"] == 4 or (card["details"]["tier"] != None and  card["details"]["tier"] >= 4):
            burn_rate = self.settings["dec"]["untamed_burn_rate"][card["details"]["rarity"] - 1]
            logger.debug(f"burn_rate: {burn_rate}")
        if (alpha_xp):
            alpha_bcx_xp = self.settings["alpha_xp"][card["details"]["rarity"] - 1]
            logger.debug(f"alpha_bcx_xp: {alpha_bcx_xp}")
            if card["gold"]:
                alpha_bcx_xp = self.settings["gold_xp"][card["details"]["rarity"] - 1]
                logger.debug(f"alpha_bcx_xp: {alpha_bcx_xp}")
            alpha_bcx = max(alpha_xp / alpha_bcx_xp, 1)
            logger.debug(f"alpha_bcx: {alpha_bcx}")
            if card["gold"]:
                alpha_bcx = max(alpha_xp / alpha_bcx_xp, 1)
                logger.debug(f"alpha_bcx: {alpha_bcx}")
            alpha_dec = burn_rate * alpha_bcx * self.settings["dec"]["alpha_burn_bonus"]
            logger.debug(f"alpha_dec: {alpha_dec}")
            if card["gold"]:
                alpha_dec *= self.settings["dec"]["gold_burn_bonus"]
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
        bcx_xp = self.settings[xp_property][card["details"]["rarity"] - 1]
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
        card = self.api.get_specific_cards(cardid)
        return self._calculate_bcx_from_card(card, cardid)

    def _calc_cp_per_usd(self, cardid, price_usd):
        card = self.api.get_specific_cards(cardid)
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
        burn_rate = self.settings["dec"]["burn_rate"][card["details"]["rarity"] - 1]
        logger.debug(f"burn_rate: {burn_rate}")
        if card["edition"] == 4 or (card["details"]["tier"] != None and  card["details"]["tier"] >= 4):
            burn_rate = self.settings["dec"]["untamed_burn_rate"][card["details"]["rarity"] - 1]
            logger.debug(f"burn_rate: {burn_rate}")
        if (alpha_xp):
            alpha_bcx_xp = self.settings["alpha_xp"][card["details"]["rarity"] - 1]
            logger.debug(f"alpha_bcx_xp: {alpha_bcx_xp}")
            if card["gold"]:
                alpha_bcx_xp = self.settings["gold_xp"][card["details"]["rarity"] - 1]
                logger.debug(f"alpha_bcx_xp: {alpha_bcx_xp}")
            alpha_bcx = max(alpha_xp / alpha_bcx_xp, 1)
            logger.debug(f"alpha_bcx_xp: {alpha_bcx_xp}")
            if card["gold"]:
                alpha_bcx = max(alpha_xp / alpha_bcx_xp, 1)
                logger.debug(f"alpha_bcx: {alpha_bcx}")
            alpha_dec = burn_rate * alpha_bcx * self.settings["dec"]["alpha_burn_bonus"]
            if card["gold"]:
                alpha_dec *= self.settings["dec"]["gold_burn_bonus"]
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
        bcx_xp = self.settings[xp_property][card["details"]["rarity"] - 1]
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
            dec *= self.settings["dec"][gold_burn_bonus_prop]
        if (card["edition"] == 0):
            dec *= self.settings["dec"]["alpha_burn_bonus"]
        if (card["edition"] == 2):
            dec *= self.settings["dec"]["promo_burn_bonus"]
        total_dec = dec + alpha_dec
        if (card["details"]["tier"] != None and card["details"]["tier"] >= 7):
            total_dec = total_dec / 2;
        logger.debug("Exit calc_cp_per_usd")
        return total_dec / price_usd

    def calculate_desired(self, listing, trx_id, price, cardid):
        logger.debug("Enter check_desired")
        if str(listing["cards"])[4] != "-":
            card = self.api.get_specific_cards(cardid)
            cardid = str(card[0]["card_detail_id"])
        if len(cardid) > 3:
            raise Exception("skipping card set...")

        # Create a set of desired cardids and the corresponding buyconfig indices
        desired_cardids = set()
        desired_buyconfig_indices = set()
        for idx, buyconfig in enumerate(self.buyconfigs):
            if ((float(buyconfig["max_quantity"]) > 0)
            and (cardid in buyconfig["cards"])
            and (price <= float(buyconfig["prices"][cardid]))
            and (price <= float(buyconfig["max_price"]))
            and ((not buyconfig["gold_only"]) or (str(listing["cards"])[2] == "G"))
            and (buyconfig["min_bcx"] == 0 or self._calculate_bcx_from_cardID(str(listing["cards"])[2:-2]) >= buyconfig["min_bcx"])
            and (buyconfig["min_cp_per_usd"] == 0 or self._calc_cp_per_usd(str(listing["cards"])[2:-2], price) >= buyconfig["min_cp_per_usd"])):
                buyconfig["max_quantity"] = buyconfig["max_quantity"] - 1
                desired_cardids.add(cardid)
                desired_buyconfig_indices.add(idx)

        # Check if the current card is desired
        if cardid in desired_cardids:
            # Use the index stored in desired_buyconfig_indices to reference the correct buyconfig
            self.currently_buying.append({"id": trx_id, "buyconfig_idx": list(desired_buyconfig_indices)[0], "cardid": str(listing["cards"])[2:-2], "price": str(price)})
            logger.info("Card ID: " + cardid + " IS desired at $" + str(price))
            logger.debug("Exit check_desired")
            return True
        logger.debug("Card ID: " + cardid + " is not desired at $" + str(price))
        logger.debug("Exit check_desired")
        return False


    def check_prices(self):
        for buyconfig in self.buyconfigs:
          buyconfig["prices"] = {}
        if self.auto_set_buy_price:
            logger.info("checking prices...")
            try:
                cardsjson = self.api.get_for_sale_grouped()
                logger.debug(f"cardsjson: {cardsjson}")
                for buyconfig in self.buyconfigs:
                    for card in cardsjson:
                        if str(card["card_detail_id"]) in buyconfig["cards"] and card["gold"] == buyconfig["gold_only"]:
                            buyconfig["prices"][str(card["card_detail_id"])] = (card["low_price"] * (1 - (self.buypct / 100)))
                            logger.debug("Exit check_prices")
            except Exception as e:
                logger.exception("error occured while checking prices with cardsjson: "  + repr(e))
            return
        else:
            for buyconfig in self.buyconfigs:
                for cardid in buyconfig["cards"]:
                    buyconfig["prices"][cardid] = buyconfig["max_price"]
            logger.debug("Exit check_prices")
            return

