#!/usr/bin/env python3
import unittest
import sys
import mock
sys.path.insert(0, '..')
from main import get_config_vars, get_cards_to_buy
from MarketCalculator import MarketCalculator

class TestCalculateDesired(unittest.TestCase):

    def setUp(self):
        self.buyconfigs, _, self.auto_set_buy_price, self.buypct, _, _ = get_config_vars()
        self.obj = MarketCalculator(self.buyconfigs, [], self.auto_set_buy_price, self.buypct)

    def test_desired_card(self):
        # Create a MarketCalculator object
        get_cards_to_buy(self.buyconfigs, self.obj.cardsjson)

        self.obj.check_prices()

        # Set the variables needed for the test
        listing = {'cards': ['C3-332-EO7XTHJ800'], 'currency': 'USD', 'price': 0.016, 'fee_pct': 510}
        trx_id = "982df69916e95a2011f3417c2eb80078bfeea3bf"
        price = 0.001
        cardid = "332"

        # Set the expected output for the test
        expected_output = True


        # Check if the output of the method is as expected
        self.assertEqual(self.obj.calculate_desired(listing, trx_id, price, cardid), expected_output)

    # @mock.patch('requests.request')
    # def test_check_prices_auto_set_buy_price(self, mock_request):
    #     # Set the return value of the mock request to simulate a successful response
    #     mock_response = mock.Mock()
    #     mock_response.text = '{"card_detail_id": 123, "gold": True, "low_price": 100}'
    #     mock_request.return_value = mock_response

    #     # Set the auto_set_buy_price attribute of the instance to True
    #     self.obj.auto_set_buy_price = True

    #     # Set up some test data for the buyconfigs attribute
    #     self.obj.buyconfigs = [{"cards": [123], "gold_only": True}]

    #     # Set the buypct attribute of the instance to 10
    #     self.obj.buypct = 10

    #     # Call the check_prices method
    #     self.obj.check_prices()

    #     # Assert that the prices attribute of the first buyconfig has been set correctly
    #     self.assertEqual(self.obj.buyconfigs[0]["prices"], {123: 90})

    # def test_check_prices_not_auto_set_buy_price(self):
    #     # Set the auto_set_buy_price attribute of the instance to False
    #     self.obj.auto_set_buy_price = False

    #     # Set up some test data for the buyconfigs attribute
    #     self.obj.buyconfigs = [{"cards": [123], "max_price": 200}]

    #     # Call the check_prices method
    #     self.obj.check_prices()

    #     # Assert that the prices attribute of the first buyconfig has been set correctly
    #     self.assertEqual(self.obj.buyconfigs[0]["prices"], {123: 200})

# Run the tests
if __name__ == '__main__':
    unittest.main()
