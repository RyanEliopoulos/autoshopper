"""

    @TODO CustomerCommunicator needs a way to update the access token upon expiry.
          Might have to override base class implementation in order to handle the error case.  Could also track the
          expiry time and have each method call evaluate the need to refresh beforehand, removing the need to handle
          failure.


"""


import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re
import urllib.parse
import time


class Communicator:  # Abstract base class
    # App credentials
    client_id: str = os.getenv('kroger_app_client_id')
    client_secret: str = os.getenv('kroger_app_client_secret')
    # API credentials (stand in)
    access_token = None
    # API urls
    api_base: str = 'https://api.kroger.com/v1/'
    api_token: str = 'connect/oauth2/token'
    api_authorize: str = 'connect/oauth2/authorize'  # "human" consent w/ redirect endpoint
    # Pagination page (stand in)
    pagination_index = 1

    # Tenney road Fred Meyer
    location_id = '70100460'
    redirect_uri: str = 'http://localhost:8000'

    def __init__(self):
        raise NotImplementedError('Should never instantiate this class')

    def get_tokens(self):
        """
            Different implementations will account for the client_credentials and authorization_code
            grant types.
        """
        raise NotImplementedError('Subclass should implement this')

    def get_productinfo(self, product_id: str) -> dict:
        """
            Pulls product info from the API and returns json/dict format of the response for caller to sort out
        :return:
        """
        # Preparing request
        headers = {
            'Accept': 'application/json'
            , 'Authorization': 'Bearer ' + self.access_token
        }
        query_params = {
            'filter.locationId': Communicator.location_id
        }
        encoded_params = urllib.parse.urlencode(query_params)
        target_url = f'{Communicator.api_base}products/{product_id}?{encoded_params}'

        # Requesting info
        req = Communicator.request('get', target_url, headers=headers)
        if req.status_code != 200:
            print(f'Error retrieving info for product {product_id}')
            print(req.text)
        req = req.json()
        return req

    def product_search(self, search_term, page_size: int = 50, direction: str = None):
        """
            Important to note this method currently has the fulfillment method hardcoded to curbside pickup

        :param search_term:   Must be at least 3 characters long.
        :param direction: either 'next' or 'previous'. Increments/decrements the pagination index relative to the
                            value of the previous product_search method call.  Invoking method without a direction
                            value resets the pagination index to default = 1
        :return:
        """
        if direction == 'next':
            self.pagination_index += page_size
            if self.pagination_index > 1000:  # Can't exceed 1k or API cries
                self.pagination_index -= page_size
        elif direction == 'previous':
            self.pagination_index -= page_size
            if self.pagination_index < 1:  # Can't be below 1 or API cries
                self.pagination_index = 1
        elif direction is None:
            self.pagination_index = 1

        url = self.api_base + 'products'
        headers = {
            'Accept': 'application/json'
            , 'Authorization': f'Bearer {self.access_token}'
        }
        params = {
            'filter.term': search_term
            , 'filter.locationId': self.location_id
            , 'filter.limit': page_size  # Number of items the response may contain
            , 'filter.start': self.pagination_index  # Result index where the response with begin reading
            , 'filter.fullfillment': 'csp'  # curbside pickup
        }
        req = self.request('get', url=url, headers=headers, params=params)

        if req.status_code != 200:
            print('Something went wrong with the product search')
            print(req.status_code)
            print(req.text)
        req = req.json()
        return req

    @staticmethod
    def request(verb, url, headers=None, data=None, params=None, auth=None, json=None):
        """
            Centralized place for making calls to the requests library.
            Centralization might come in handy so..
        """
        # Pulling appropriate request method
        str_to_req = {
            'post': requests.post
            , 'get': requests.get
            , 'put': requests.put
        }
        req = str_to_req[verb]
        response = req(url, headers=headers, data=data, params=params, auth=auth, json=json)

        return response


########################################################################################################################


class CustomerCommunicator(Communicator):

    def __init__(self):
        # Customer credentials
        self.username = os.getenv('kroger_username')
        self.password = os.getenv('kroger_password')
        # API variables
        self.access_token = None
        self.refresh_token = None
        self.authorization_code = None
        # Pagination index
        self.pagination_index = 1  # Helps product_search track state in case pagination is required

    def _get_authcode(self):

        """
                Requires Selenium to emulate customer input, authorizing the app to do it's thing.
                Kroger includes the authorization code as a param in the redirect url.

                Really need a good way to pause until the page is fully loaded

            :return: None
            """
        # Preparing URL
        params = {
            'scope': 'profile.compact cart.basic:write product.compact'
            , 'client_id': Communicator.client_id
            , 'redirect_uri': Communicator.redirect_uri
            , 'response_type': 'code'
            , 'state': 'oftheunion'
        }
        encoded_params = urllib.parse.urlencode(params)
        target_url = Communicator.api_base + Communicator.api_authorize + '?' + encoded_params

        # Navigating with Selenium
        browser = webdriver.Firefox()
        browser.get(target_url)

        # Impersonating human authorization
        username_field = browser.find_element(By.ID, 'username')
        password_field = browser.find_element(By.ID, 'password')

        username_field.send_keys(os.getenv('kroger_username'))
        time.sleep(1)
        password_field.send_keys(os.getenv('kroger_password'))
        time.sleep(1)
        password_field.send_keys(Keys.ENTER)

        time.sleep(12)  # Hacky attempt at waiting for page to fully load

        # Retrieving auth code from the redirect URL
        full_url = browser.current_url
        pattern = re.compile(r'\?code=(.*)&')
        authorization_code = pattern.search(full_url).group(1)

        if not authorization_code:
            print("Error retrieving authorization code")
            print('full_url: ', full_url)
            exit(3)

        self.authorization_code = authorization_code

    def get_tokens(self, refresh=False):
        self._get_authcode()
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'authorization_code'
            , 'redirect_uri': Communicator.redirect_uri
            , 'scope': 'profile.compact'
            , 'code': self.authorization_code
        }
        target_url = Communicator.api_base + Communicator.api_token
        req = Communicator.request('post', target_url, headers=headers, data=data,
                                   auth=(Communicator.client_id, Communicator.client_secret))
        if req.status_code != 200:
            print('error retrieving tokens with authorization_code')
            print(req.text)
            exit(4)
        req = req.json()
        self.access_token = req['access_token']
        self.refresh_token = req['refresh_token']

    def add_to_cart(self, shopping_list: list[dict]) -> bool:
        """
        :param shopping_list:  [{'upc': <>, 'quantity': <>}, ... ]
        :return bool indicating success/failure
        """
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
            , 'Authorization': f'Bearer {self.access_token}'
        }
        data = {
            'items': shopping_list
        }
        target_url = f'{Communicator.api_base}cart/add'
        req = Communicator.request('put', target_url, headers=headers, json=data)
        if req.status_code != 204:
            print("error adding items to cart")
            print(req.text)
            exit()

        return True


########################################################################################################################


class AppCommunicator(Communicator):

    def __init__(self):
        self.access_token = None
        self.pagination_index = 1  # Helps product_search track state in case pagination is required

    def get_tokens(self):
        # Staging HTTP request content
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'client_credentials'
            , 'scope': 'product.compact'
        }
        target_url = Communicator.api_base + Communicator.api_token
        # Making Request
        req = Communicator.request('post', target_url, headers=headers, data=data,
                                   auth=(Communicator.client_id, Communicator.client_secret))
        if req.status_code != 200:
            print('Error retrieving access tokens with client credentials..')
            print(req.text)
            exit(1)
        req = req.json()
        self.access_token = req['access_token']
