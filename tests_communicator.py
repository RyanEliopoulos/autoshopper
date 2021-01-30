import unittest
from communicator import AppCommunicator
from communicator import CustomerCommunicator


class CustomerCommunicatorTests(unittest.TestCase):

    def test_get_authcode(self):
        customer_comm = CustomerCommunicator()
        customer_comm._get_authcode()
        self.assertIsInstance(customer_comm.authorization_code, str)

    def test_get_tokens(self):
        customer_comm = CustomerCommunicator()
        customer_comm.get_tokens()
        self.assertIsInstance(customer_comm.access_token, str)
        self.assertIsInstance(customer_comm.refresh_token, str)

    def test_get_productinfo(self):
        # Prepping test
        customer_comm = CustomerCommunicator()
        customer_comm.get_tokens()
        self.assertIsInstance(customer_comm.access_token, str)
        self.assertIsInstance(customer_comm.refresh_token, str)
        product_id = '0021086500000'  # Heritage farms chicken thighs

        # Testing
        values = customer_comm.get_productinfo(product_id)
        self.assertEqual(values['data']['productId'], product_id)


class AppCommunicatorTests(unittest.TestCase):

    def test_get_tokens(self):
        app_comm = AppCommunicator()
        app_comm.get_tokens()

    def test_get_productinfo(self):
        # Prepping
        app_comm = AppCommunicator()
        app_comm.get_tokens()
        self.assertIsInstance(app_comm.access_token, str)
        product_id = '0021086500000'  # Heritage farms chicken thighs

        # Testing
        values = app_comm.get_productinfo(product_id)
        self.assertIsInstance(values, dict)
        self.assertEqual(values['data']['productId'], product_id)
