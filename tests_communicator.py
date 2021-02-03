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

    def test_add_to_cart(self):
        # Prepping test
        customer_comm = CustomerCommunicator()
        customer_comm.get_tokens()
        self.assertIsInstance(customer_comm.access_token, str)
        self.assertIsInstance(customer_comm.refresh_token, str)
        # Getting product info
        product_id = '0021086500000'  # Heritage farms chicken thighs
        values = customer_comm.get_productinfo(product_id)
        self.assertEqual(values['data']['productId'], product_id)
        upc = values['data']['upc']
        # Building shopping list with newly acquired upc value
        shopping_list = [{'upc': upc,  'quantity': 2}]
        success: bool = customer_comm.add_to_cart(shopping_list)
        self.assertEqual(success, True)

    def test_product_search(self):
        search_term = "onion"  # must be lower case. Product descriptions are converted to lower.
        # Prepping test
        customer_comm = CustomerCommunicator()
        customer_comm.get_tokens()
        self.assertIsInstance(customer_comm.access_token, str)
        self.assertIsInstance(customer_comm.refresh_token, str)
        # Calling API
        product_array = customer_comm.product_search(search_term)['data']
        # Evaluating response data
        self.assertTrue(len(product_array > 3))
        for product in product_array:
            descr_string = product['description'].lower()
            self.assertTrue(search_term in descr_string)

    def test_productsearch_pagination(self):
        search_term = "milk"  # must be lower case. Product descriptions are converted to lower.
        # Prepping test
        cust_comm = CustomerCommunicator()
        cust_comm.get_tokens()
        self.assertIsInstance(cust_comm.access_token, str)
        # Calling API
        results = cust_comm.product_search(search_term)
        # Evaluating "meta" field returned from API call
        pagination_start = results['meta']['pagination']['start']
        self.assertEqual(pagination_start, 1)

        # Testing pagination - next
        next_results = cust_comm.product_search(search_term, direction='next')
        new_pagination_start = next_results['meta']['pagination']['start']
        self.assertEqual(new_pagination_start, 51)

        # Testing pagination - previous
        next_results = cust_comm.product_search(search_term, direction='previous')
        new_pagination_start = next_results['meta']['pagination']['start']
        self.assertEqual(new_pagination_start, 1)

        # Testing new search term (pagination_index should reset to 1)
        fresh_results = cust_comm.product_search("bacon")
        fresh_pagination_start = fresh_results['meta']['pagination']['start']
        self.assertEqual(fresh_pagination_start, 1)


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

    def test_product_search(self):
        search_term = "milk"  # must be lower case. Product descriptions are converted to lower.
        # Prepping test
        app_comm = AppCommunicator()
        app_comm.get_tokens()
        self.assertIsInstance(app_comm.access_token, str)
        # Calling API
        product_array = app_comm.product_search(search_term)['data']
        # Evaluating response data
        self.assertTrue(len(product_array) > 5)
        for product in product_array:
            descr_string = product['description'].lower()
            self.assertTrue(search_term in descr_string)

    def test_productsearch_pagination(self):
        search_term = "milk"  # must be lower case. Product descriptions are converted to lower.
        # Prepping test
        app_comm = AppCommunicator()
        app_comm.get_tokens()
        self.assertIsInstance(app_comm.access_token, str)
        # Calling API
        results = app_comm.product_search(search_term)
        # Evaluating "meta" field returned from API call
        pagination_start = results['meta']['pagination']['start']
        self.assertEqual(pagination_start, 1)

        # Testing pagination - next
        next_results = app_comm.product_search(search_term, direction='next')
        new_pagination_start = next_results['meta']['pagination']['start']
        self.assertEqual(new_pagination_start, 51)

        # Testing pagination - previous
        next_results = app_comm.product_search(search_term, direction='previous')
        new_pagination_start = next_results['meta']['pagination']['start']
        self.assertEqual(new_pagination_start, 1)

        # Testing new search term (pagination_index should reset to 1)
        fresh_results = app_comm.product_search("bacon")
        fresh_pagination_start = fresh_results['meta']['pagination']['start']
        self.assertEqual(fresh_pagination_start, 1)