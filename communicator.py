import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re
import urllib.parse
import time


class Communicator:
    # App credentials
    client_id: str = os.getenv('kroger_app_client_id')
    client_secret: str = os.getenv('kroger_app_client_secret')
    access_token = None
    refresh_token = None
    authorization_code = None
    # Customer credentials
    username = os.getenv('kroger_username')
    password = os.getenv('kroger_password')
    # API urls
    api_base: str = 'https://api.kroger.com/v1/'
    api_token: str = 'connect/oauth2/token'
    api_authorize: str = 'connect/oauth2/authorize'  # "human" consent w/ redirect endpoint

    # Tenney road Fred Meyer
    location_id = '70100460'
    redirect_uri: str = 'http://localhost:8000'

    @staticmethod
    def get_tokens(grant_type='authorization_code'):
        """
            Authorization code means acting on behalf of a Kroger customer account.
            client_credentials is acting on behalf of our registered app 
            
        :return: None
        """""
        if grant_type == 'authorization_code':
            Communicator.get_authcode()
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = {
                'grant_type': 'authorization_code'
                , 'redirect_uri': Communicator.redirect_uri
                , 'scope': 'profile.compact'
                , 'code': Communicator.authorization_code
            }
            target_url = Communicator.api_base + Communicator.api_token
            req = Communicator.request('post', target_url, headers=headers, data=data,
                                       auth=(Communicator.client_id, Communicator.client_secret))
            if req.status_code != 200:
                print('error retrieving tokens with authorization_code')
                print(req.text)
                exit(4)
            print('Got access tokens with authorization code')
            print(req.text)
            req = req.json()
            Communicator.access_token = req['access_token']
            Communicator.refresh_token = req['refresh_token']

        elif grant_type == 'client_credentials':
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
            print(req)
            Communicator.access_token = req['access_token']

    @staticmethod
    def _get_authcode():
        """
            Requires Selenium to emulate customer input, authorizing the app to do it's thing.
            Kroger includes the authorization code as a param in the redirect url.

            Really need a good way to pause until the page is fully loaded

        :return: None
        """
        # Preparing URL
        params = {
            'scope': 'profile.compact cart.basic:write'
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

        print('Authorization code: ', authorization_code)
        Communicator.authorization_code = authorization_code

    @staticmethod
    def get_productinfo(product_id):
       """
            Pulls product info from the API and returns json/dict format of the response for caller to sort out
       :param product_id:
       :return:
       """



    @staticmethod
    def request(verb, url, headers=None, data=None, params=None, auth=None):
        """
            Centralized place for making calls to the requests library.
            Centralization might come in handy so..

        """

        # Pulling appropriate request method
        str_to_req = {
            'post': requests.post
            , 'get': requests.get
        }
        req = str_to_req[verb]
        response = req(url, headers=headers, data=data, params=params, auth=auth)

        return response


