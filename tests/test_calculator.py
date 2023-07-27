#!/usr/bin/env python3
import unittest
import sys
from types import SimpleNamespace
sys.path.insert(0, '..')
from main import get_config_vars, get_cards_to_buy
from SplinterlandsSDK import Api
from MarketCalculator import MarketCalculator

class TestCalculateDesired(unittest.TestCase):
    def test_desired_card(self):
        args = SimpleNamespace(config='test_config.json')
        buyconfigs, _, auto_set_buy_price, buypct, _, _ = get_config_vars(args)
        api = Api()
        # Create a MarketCalculator object
        obj = MarketCalculator(api, buyconfigs, [], auto_set_buy_price, buypct)
        get_cards_to_buy(buyconfigs, obj.cardsjson)

        obj.check_prices()

        # Set the variables needed for the test
        listing = {'cards': ['C3-332-EO7XTHJ800'], 'currency': 'USD', 'price': 0.016, 'fee_pct': 510}
        trx_id = "982df69916e95a2011f3417c2eb80078bfeea3bf"
        price = 0.001
        cardid = "332"

        # Set the expected output for the test
        expected_output = True


        # Check if the output of the method is as expected
        self.assertEqual(obj.calculate_desired(listing, trx_id, price, cardid), expected_output)

# Run the tests
if __name__ == '__main__':
    unittest.main()
