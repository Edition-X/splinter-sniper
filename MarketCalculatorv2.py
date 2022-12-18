#!/usr/bin/env python3
from setup_logger import logger
from SplinterlandsAPI import SplinterlandsAPI
import json
import requests
import sys

class MarketCalculator:
    def __init__(self, api, buyconfigs, currently_buying, auto_set_buy_price, buypct):
        self.api = api
        self.buyconfigs = buyconfigs
        self.currently_buying = currently_buying
        self.auto_set_buy_price = auto_set_buy_price
        self.buypct = buypct

        self.settings = self.api.get_settings()

    def calculate_market_price(self, card_id, price_type):
        card = self.api.card_lookup(card_id)[0]
        market_price = 0
        if price_type == "sell":
            market_price = self._calculate_sell_price(card)
        elif price_type == "buy":
            market_price = self._calculate_buy_price(card)

        return market_price

    def _calculate_bcx_from_card(self, card):
        alpha_bcx = 0
        alpha_dec = 0
        alpha_xp = 0
        if alpha_xp in card:
            alpha_xp = card["alpha_xp"]
        xp = max(card["xp"] - alpha_xp, 0)
        burn_rate = self.settings["dec"]["burn_rate"][card["details"]["rarity"] - 1]
        if card["edition"] == 4 or (card["details"]["tier"] != None and  card["details"]["tier"] >= 4):
            burn_rate = self.settings["dec"]["untamed_burn_rate"][card["details"]["rarity"] - 1]
        if (alpha_xp):
            alpha_bcx_xp = self.settings["alpha_xp"][card["details"]["rarity"] - 1]
            if card["gold"]:
                alpha_bcx_xp = self.settings["gold_xp"][card["details"]["rarity"] - 1]
            alpha_bcx = max(alpha_xp / alpha_bcx_xp, 1)
            if card["gold"]:
                alpha_bcx = max(alpha_xp / alpha_bcx_xp, 1)
            alpha_dec = burn_rate * alpha_bcx * self.settings["dec"]["alpha_burn_bonus"]
            if card["gold"]:
                alpha_dec *= self.settings["dec"]["gold_burn_bonus"]

        xp_property = "error"
        if card["edition"] == 0 or (card["edition"] == 2 and int(card["details"]["id"]) < 100):
            if card["gold"]:
                xp_property = "gold_xp"
            else:
                xp_property = "alpha_xp"
        else:
            if card["gold"]:
                xp_property = "beta_gold_xp"
            else:
                xp_property = "beta_xp"
        bcx_xp = self.settings[xp_property][card["details"]["rarity"] - 1]
        bcx = max((xp + bcx_xp) / bcx_xp, 1)
        if card["gold"]:
            bcx = max(xp / bcx_xp, 1)
        if card["edition"] == 4 or (card["details"]["tier"] != None and card["details"]["tier"] >= 4):
            bcx = card["xp"]
        if (alpha_xp):
            bcx = bcx - 1
        return bcx

    def _calculate_sell_price(self, bcx):
        sell_price = self.settings["prices"]["sell_price_factor"] * bcx
        sell_price += self.settings["prices"]["sell_price_constant"]
        return sell_price

    def _calculate_buy_price(self, bcx):
        buy_price = self.settings["prices"]["buy_price_factor"] * bcx
        buy_price += self.settings["prices"]["buy_price_constant"]
        return buy_price

    def market_sell_price(self, card_id):
        return self.calculate_market_price(card_id, "sell")

    def market_buy_price(self, card_id):
        return self.calculate_market_price(card_id, "buy")

    def market_card_price(self, card_id, price_type):
        price = self.calculate_market_price(card_id, price_type)
        return f"{price:.2f}"

    def market_card_price_dict(self, card_id, price_type):
        price = self.calculate_market_price(card_id, price_type)
        return {"price": price}

