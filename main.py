import requests
import urllib.parse
import os
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Customer credentials
username = os.getenv('kroger_username')
password = os.getenv('kroger_password')


# App credentials
client_id: str = 'autoshopper-94b93de382bf39746138ed21e8405a5b4927188131458247672'
client_secret: str = 'mEbTtN8lful792P3P0QNk06pKiCVADRaUV07dDn5'
redirect_uri: str = 'http://138.68.18.203:8002/tictac/login'

api_base: str = 'https://api.kroger.com/v1/'


params = {'scope': 'profile.compact cart.basic:write product.compact'
          , 'client_id': client_id
          , 'redirect_uri': redirect_uri
          , 'response_type': 'code'
          , 'state': 'jomama'}


def authorize_app() -> str:
    req = requests.get(api_base + 'connect/oauth2/authorize', params=params)
    print(req.text)
    print(req.status_code)
    print(req.url)
    print(req.cookies)

    val = urllib.parse.urlencode(params)
    print(val)

    # Beginning authorization code process
    browser = webdriver.Firefox()
    browser.get(api_base + 'connect/oauth2/authorize?' + val)

    # "Manually" consenting to app permissions
    username_field = browser.find_element(By.ID, 'username')
    password_field = browser.find_element(By.ID, 'password')

    username_field.send_keys(username)
    time.sleep(1)
    password_field.send_keys(password)
    time.sleep(1)
    password_field.send_keys(Keys.ENTER)

    # Hacky wait since we don't know when the page will load
    time.sleep(5)

    # Now need to parse the url to extract the "code"
    full_url = browser.current_url
    print("fuller_url:" +full_url)
    pattern = re.compile(r'\?code=(.*)&')
    authorization_code = pattern.search(full_url).group(1)

    return authorization_code



auth_code = authorize_app()








