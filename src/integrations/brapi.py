import os
import requests


def get_token():
    token = os.getenv("BRAPI_TOKEN", None)
    if token is None:
        raise Exception("Missing BRAPI_TOKEN environment variable")

    return token


def fetch_stock_data(stock):
    token = get_token()

    # The free plan only allows data from 1 month range.
    url = "https://brapi.dev/api/quote/{}?range=1mo&interval=1d&token={}".format(
        stock, token
    )
    request = requests.get(url)
    request.raise_for_status()

    json_data = request.json()
    return json_data
