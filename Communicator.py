"""
    Ultimately want program to function even if it can't connect/access the API.
    Set a status attribute to reflect ability, then check in contrller after instantiating?

    Should token management be broken into an "Authenticator" class?
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
import DBInterface
import Logger


class Communicator:
    """
        The DBInterface reference allows Communicator to retrieve
        existing tokens and keep the refresh token updated.
    """
    def __init__(self, db_interface: DBInterface):
        # API details
        self.api_base: str = 'https://api.kroger.com/v1/'
        self.api_token: str = 'connect/oauth2/token'
        self.api_authorize: str = 'connect/oauth2/authorize'  # "human" consent w/ redirect endpoint
        self.redirect_uri: str = 'http://localhost:8000'
        self.location_id: str = os.getenv('kroger_api_location_id')
        # App credentials
        self.client_id = os.getenv('kroger_app_client_id')
        self.client_secret = os.getenv('kroger_app_client_secret')
        # Token management
        self.db_interface: DBInterface = db_interface
        tokens: dict = self.init_tokens()
        self.access_token: str = tokens['access_token']
        self.access_token_timestamp: float = tokens['access_timestamp']
        self.refresh_token: str = tokens['refresh_token']
        self.refresh_token_timestamp: float = tokens['refresh_timestamp']

    def _get_authcode(self) -> str:
        """
        Requires Selenium to emulate customer input, authorizing the app to do it's thing.
        Kroger includes the authorization code as a param in the redirect url.

        Really need a good way to pause until the page is fully loaded. For now we just pause for 12
        seconds. That's not great.
        """
        # Preparing URl
        params: dict = {
            'scope': 'profile.compact cart.basic:write product.compact'
            , 'client_id': self.client_id
            , 'redirect_uri': self.redirect_uri
            , 'response_type': 'code'
            , 'state': 'oftheunion'
        }
        encoded_params = urllib.parse.urlencode(params)
        target_url = self.api_base + self.api_authorize + '?' + encoded_params

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
        authorization_code: str = pattern.search(full_url).group(1)

        if not authorization_code:
            Logger.Logger.log_error('Error retrieving authorization code')
            print("Error retrieving authorization code")
            print('full_url: ', full_url)
            exit(1)

        return authorization_code

    def valid_token(self, timestamp: float, token_type: str) -> bool:
        """
        Token validity check
        Access tokens have 30 minute expiration
        Refresh tokens have 6 month expiration
        :param timestamp: Unix epoch
        :param token_type: <access>, <refresh>
        """
        now: float = datetime.datetime.now().timestamp()
        diff_seconds: float = now - timestamp
        diff_minutes = diff_seconds / 60
        if token_type == 'access':
            if diff_minutes >= 25:
                return False
            return True
        elif token_type == 'refresh':
            diff_hours = diff_minutes / 60
            diff_days = diff_hours / 24
            if diff_days >= 140:  # ~5 months
                return False
            return True

    def tokens_from_authcode(self) -> tuple[int, tuple]:
        """
        Emulates human input to kick start API access.
        Commits new refresh token to DB
        :return:  (int: 0 upon success, else -1,
                   tuple(access_token, access_timestamp, refresh_token, refresh_timestamp) success, else (None,)
        """
        authcode: str = self._get_authcode()
        headers: dict = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data: dict = {
            'grant_type': 'authorization_code'
            , 'redirect_uri': self.redirect_uri
            , 'scope': 'profile.compact cart.basic:write product.compact'
            , 'code': authcode
        }
        target_url: str = self.api_base + self.api_token
        req = requests.post(target_url, headers=headers, data=data,
                            auth=(self.client_id, self.client_secret))
        if req.status_code != 200:
            Logger.Logger.log_error('Error retrieving tokens with auth code --- ' + req.text)
            print('error retrieving tokens with authorization_code')
            print(req.text)
            return -1, (req.text,)
        req = req.json()
        access_timestamp: float = datetime.datetime.now().timestamp()
        access_token: str = req['access_token']
        refresh_token: str = req['refresh_token']
        refresh_timestamp: float = access_timestamp
        print("..Tokens retrieved. Writing to database")
        ret = self.db_interface.update_token(refresh_token, refresh_timestamp)
        if ret[0] != 0:
            Logger.Logger.log_error('Error updating refresh token from authcode in db' + ret[1])
            exit(1)
        return 0, (access_token, access_timestamp, refresh_token, refresh_timestamp)

    def token_refresh(self):
        """
        Pulls new access and refresh tokens using an existing, valid refresh token.
        Up to caller to verify the refresh token is valid.
        :return:
        """
        # Prepping request
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'refresh_token'
            , 'refresh_token': self.refresh_token
        }
        target_url: str = self.api_base + self.api_token
        # Evaluating response
        req = requests.post(target_url, headers=headers, data=data,
                            auth=(self.client_id, self.client_secret))
        if req.status_code != 200:
            Logger.Logger.log_error('Failed to refresh tokens in token_refresh()' + req.text)
            print("Error refreshing access token")
            print(req.text)
            exit(1)
        req = req.json()
        # Updating token variables
        self.access_token = req['access_token']
        self.access_token_timestamp = datetime.datetime.now().timestamp()
        self.refresh_token = req['refresh_token']
        self.refresh_token_timestamp = self.access_token_timestamp
        ret = self.db_interface.update_token(self.refresh_token, self.refresh_token_timestamp)
        if ret[0] != 0:
            Logger.Logger.log_error('Error writing new refresh token to DB ' + ret[1])
            Logger.Logger.log_error('Refresh token is:' + self.refresh_token)
            exit(1)

    def init_tokens(self) -> dict:
        """
        Fetches the access and refresh tokens from disk or from oauth flow
        :return {'access_token: <>,
                  'access_token_timestamp: <> ,
                  'refresh_token': <>,
                  'refresh_token_timestamp: <>}
        """
        refresh_token: str = ''
        refresh_timestamp: float = 0.0
        access_token: str = ''
        access_timestamp: float = 0.0
        # Checking for tokens on disk first
        ret = self.db_interface.retrieve_token()
        if ret[0] == -1:
            # Fatal - error reading from database
            Logger.Logger.log_error('Error reading tokens from DB' + ret[1])
            print('Error reading tokens from DB')
            exit(1)
        elif ret[0] == 1:
            # No tokens in the database
            tokens: tuple = self.tokens_from_authcode()
            access_token = tokens[1][0]
            access_timestamp = tokens[1][1]
            refresh_token = tokens[1][2]
            refresh_timestamp = tokens[1][3]
        elif ret[0] == 0:
            # Retrieved refresh token
            refresh_token = ret[1][0]
            refresh_timestamp = ret[1][1]
            if self.valid_token(float(refresh_timestamp), token_type='refresh'):
                # Exchanging refresh token
                self.refresh_token = refresh_token
                self.token_refresh()  # updates token attributes
                access_token = self.access_token
                access_timestamp = self.access_token_timestamp
                refresh_token = self.refresh_token
                refresh_timestamp = self.refresh_token_timestamp
            else:
                tokens: tuple = self.tokens_from_authcode()
                access_token = tokens[1][0]
                access_timestamp = tokens[1][1]
                refresh_token = tokens[1][2]
                refresh_timestamp = tokens[1][3]
        ret_dict = {
            'access_token': access_token,
            'access_timestamp': access_timestamp,
            'refresh_token': refresh_token,
            'refresh_timestamp': refresh_timestamp
        }
        return ret_dict

    def add_to_cart(self, shopping_list: list[dict]) -> bool:
        """
        :param shopping_list:  [{'upc': <>, 'quantity': <>}, ... ]
        :return bool indicating success/failure
        """
        if not self.valid_token(self.access_token_timestamp, 'access'):
            self.token_refresh()

        headers: dict = {
            'Content-Type': 'application/x-www-form-urlencoded'
            , 'Authorization': f'Bearer {self.access_token}'
        }
        data: dict = {
            'items': shopping_list
        }
        target_url: str = f'{self.api_base}cart/add'
        req = requests.put(target_url, headers=headers, json=data)
        if req.status_code != 204:
            Logger.Logger.log_error('Error adding to cart ' + req.text)
            print("error adding items to cart")
            print(req.status_code)
            print(req.text)
            exit(1)

        return True