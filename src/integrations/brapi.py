import os
import requests
from requests.adapters import HTTPAdapter, Retry
from integrations.lib.cache import cache_by_time


# Retry mechanism. If the status code is not 200, we retry the request up to 5 times.
class RetryIfNot200(Retry):
    def is_retry(self, method, status_code, has_retry_after=False):
        if status_code != 200:
            return True
        return False


def get_token():
    token = os.getenv("BRAPI_TOKEN", None)
    if token is None:
        raise Exception("Missing BRAPI_TOKEN environment variable")

    return token


@cache_by_time(60 * 15)
def fetch_stock_data(stock):
    token = get_token()

    requests_retry = requests.Session()
    retries = RetryIfNot200(total=5, backoff_factor=0)
    requests_retry.mount("https://", HTTPAdapter(max_retries=retries))

    # The free plan only allows data from 1 month range.
    url = f"https://brapi.dev/api/quote/{stock}?range=1mo&interval=1d&token={token}"
    request = requests_retry.get(url)
    request.raise_for_status()

    return request.json()
