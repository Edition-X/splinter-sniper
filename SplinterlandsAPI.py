#!/usr/bin/env python3
from setup_logger import logger
import json
import sys
import requests

class SplinterlandsAPI:
    def __init__(self):
        self.settings = self.get_settings()
        self.cardsjson = self.get_cards()

    def _get_headers(self):
        return {
        }

    def card_lookup(self, cardid):
        self.cardid = cardid
        try:
            card =  json.loads(requests.request("GET",
                            f"https://api.splinterlands.com/cards/find?ids={cardid}",
                            headers=self._get_headers()
                            ).text)
            return card
        except Exception as e:
            logger.exception("error getting cards: "  + repr(e))
            sys.exit(1)


    def get_cards(self):
        try:
            cardsjson = json.loads(requests.request("GET",
                            "https://api.splinterlands.com/cards/get_details",
                            headers=self._get_headers()
                            ).text)
            return cardsjson
        except Exception as e:
            logger.exception("error getting cards: "  + repr(e))
            sys.exit(1)

    def get_settings(self):
        try:
            settings = json.loads(requests.request("GET",
                            "https://api.splinterlands.com/settings",
                            headers=self._get_headers()
                            ).text)
            return settings
        except Exception as e:
            logger.exception("error getting settings: " + repr(e))
            sys.exit(1)
