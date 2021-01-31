import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re
import urllib.parse
import time
import json


class Communicator:
    # App credentials
    client_id: str = os.getenv('kroger_app_client_id')
    client_secret: str = os.getenv('kroger_app_client_secret')
    # API credentials (stand in)
    access_token = None
    # API urls
    api_base: str = 'https://api.kroger.com/v1/'
    api_token: str = 'connect/oauth2/token'
    api_authorize: str = 'connect/oauth2/authorize'  # "human" consent w/ redirect endpoint

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

    def get_productinfo(self, product_id):
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

    def get_tokens(self):
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

    def add_to_cart(self, shopping_list: list[dict]):
        """

        :param shopping_list:  [{'upc': <>, 'quantity': <>}, ... ]
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
        print(req.status_code)
        print(req.text)

        return True
########################################################################################################################


class AppCommunicator(Communicator):

    def __init__(self):
        self.access_token = None

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
