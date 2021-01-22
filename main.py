import requests
import urllib.parse
from selenium import webdriver

client_id: str = 'autoshopper-94b93de382bf39746138ed21e8405a5b4927188131458247672'
client_secret: str = 'mEbTtN8lful792P3P0QNk06pKiCVADRaUV07dDn5'
redirect_uri: str = 'http://138.68.18.203:8002/tictac/login'

api_base: str = 'https://api.kroger.com/v1/'


params = {'scope': 'profile.compact, cart.basic:write, product.compact'
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

    # val = urllib.parse.urlencode(f'scope=profile.compact&client_id={client_id}&client_secret={client_secret}&redirect_uri={redirect_uri}&response_type=code&state=jomama')
    val = urllib.parse.urlencode(params)
    print(val)

    # Consenting to my app
    browser = webdriver.Firefox()
    browser.get(api_base + 'connect/oauth2/authorize?' + val)

    # Copy/pasting "code" from the redirect uri
    code = input('Whats the code?\n')
    print(code)

    # Attempting to get a









