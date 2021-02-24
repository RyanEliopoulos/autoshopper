"""
    NOTE:  This program does not check for the edge case where the current process has outlived the months-long lifespan
            of a refresh token. After 6 months of idling the process may attempt to update the refresh token with
            an expired refresh token. I absolve myself of this responsibility.
"""

import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re
import urllib.parse
import time
import json
import datetime


class Communicator:
    # Thought I'd be clever with an abstract base class.. Not sure it was clever now.

    # App credentials
    client_id: str = os.getenv('kroger_app_client_id')
    client_secret: str = os.getenv('kroger_app_client_secret')

    # API credentials (stand in)
    access_token = None
    access_token_timestamp = datetime.datetime(1990, 1, 1, 1, 1)
    # API urls
    api_base: str = 'https://api.kroger.com/v1/'
    api_token: str = 'connect/oauth2/token'
    api_authorize: str = 'connect/oauth2/authorize'  # "human" consent w/ redirect endpoint
    # Pagination page
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

    def token_refresh(self):
        """
            Implemented by CustomerCommunicator
        :return:
        """
        raise NotImplementedError

    def valid_token(self) -> bool:
        """
            Evaluates the access token timestamp for freshness. Spec says 30m minutes. Will enforce 25 minutes.

            The base class variable "access_token_timestamp" will be overwritten by the CustomerCommunicator variable.
        :return:
        """

        now = datetime.datetime.now().timestamp()
        diff_seconds = self.access_token_timestamp - now
        diff_minutes = diff_seconds / 60

        if diff_minutes >= 25:
            return False
        return True

    def get_productinfo(self, product_id: str) -> dict:
        """
            Pulls product info from the API and returns json/dict format of the response for caller to sort out
        :return:
        """
        if not self.valid_token():
            self.token_refresh()

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
        :param page_size: How many results per page the API will reply with
        :return:  Results from the API query
        """

        if not self.valid_token():
            self.token_refresh()

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
            Useful idea? Verdict inconclusive
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
        access_token_timestamp = datetime.datetime(1990, 1, 1, 1, 1)  # Temp stand in. Epoch seconds.
        self.refresh_token = None
        self.authorization_code = None
        # Pagination index
        self.pagination_index = 1  # Helps product_search track state in case pagination is required

    def stage_tokens(self):
        """
            Reads a {'refresh_token': <>, 'timestamp': <epoch seconds>} object from disk, if it exists,
            evaluating the timestamp for validity.  Retrieves new access token if so, else engages human auth
            for a new access token/refresh token pair.

            Meant to be called at boot so that all methods querying the API can ask for a new token, if necessary.
        """

        try:
            # Attempting to load {'token': <>, 'timestamp': <epoch>} object
            with open('refresh_token.json', 'r') as token_file:
                token_info = json.load(token_file)

            # Evaluating token for freshness
            # Refresh tokens are good for 6 months as of 2/24/2021
            self.refresh_token = token_info['refresh_token']
            timestamp = token_info['timestamp']  # Epoch timestamp
            now = datetime.datetime.now().timestamp()
            diff_seconds = now - timestamp
            diff_minutes = diff_seconds / 60
            diff_hours = diff_minutes / 60
            diff_days = diff_hours / 24

            if diff_days < 150:
                # Token is still good.
                # Retrieving new access and refresh tokens
                self.token_refresh()
            else:
                # Declaring refresh token stale.
                # Will need user auth to retrieve new tokens.
                self.get_tokens()
        except FileNotFoundError:
            # Tokens not saved to disk
            # Querying API with human credentials instead
            self.get_tokens()

    def _get_authcode(self):
        """
            Requires Selenium to emulate customer input, authorizing the app to do it's thing.
            Kroger includes the authorization code as a param in the redirect url.

            Really need a good way to pause until the page is fully loaded. For now we just pause for 12
            seconds. That's not great.
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
        username_field.send_keys(self.username)
        time.sleep(1)
        password_field.send_keys(self.password)
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
        """
            Used in the event that no valid refresh tokens are available to generate new access and refresh tokens.
        """

        print("Please wait while we retrieve the API tokens..")
        self._get_authcode()
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'authorization_code'
            , 'redirect_uri': Communicator.redirect_uri
            , 'scope': 'profile.compact cart.basic:write product.compact'
            , 'code': self.authorization_code
        }
        target_url = Communicator.api_base + Communicator.api_token
        req = Communicator.request('post', target_url, headers=headers, data=data,
                                   auth=(Communicator.client_id, Communicator.client_secret))
        if req.status_code != 200:
            print('error retrieving tokens with authorization_code')
            print(req.text)
            exit(4)
        print("..Tokens retrieved")
        req = req.json()
        self.access_token = req['access_token']
        self.access_token_timestamp = datetime.datetime.now().timestamp()
        self.refresh_token = req['refresh_token']

        # Writing refresh token to disk
        self.save_token()

    def token_refresh(self):
        """
            Pulls new access and refresh tokens using an existing, valid refresh token.
            Up to caller to verify the refresh token is valid.
        """
        print("refreshing tokens")
        # Prepping request
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'refresh_token'
            , 'refresh_token': self.refresh_token
        }
        target_url = Communicator.api_base + Communicator.api_token

        # Evaluating response
        req = Communicator.request('post', target_url, headers=headers, data=data,
                                   auth=(Communicator.client_id, Communicator.client_secret))
        if req.status_code != 200:
            print("Error refreshing access token")
            print(req.text)
            exit(5)
        req = req.json()

        # Updating token variables
        self.access_token = req['access_token']
        self.access_token_timestamp = datetime.datetime.now().timestamp()
        self.refresh_token = req['refresh_token']
        # Writing refresh token to disk
        self.save_token()

    def save_token(self):
        """
            Saves the fresh token to disk along with a timestamp in epoch seconds.
            Called by get_tokens() and token_refresh()
        """

        try:
            timestamp = datetime.datetime.now().timestamp()
            jsn_object = {'refresh_token': self.refresh_token
                          , 'timestamp': timestamp}
            with open('refresh_token.json', 'w+') as token_file:
                json.dump(jsn_object, token_file)

        except Exception as e:
            print(f"Encountered error writing refresh token to disk: {e}")

    def add_to_cart(self, shopping_list: list[dict]) -> bool:
        """
        :param shopping_list:  [{'upc': <>, 'quantity': <>}, ... ]
        :return bool indicating success/failure
        """

        if not self.valid_token():
            self.token_refresh()

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
            print(req.status_code)
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
