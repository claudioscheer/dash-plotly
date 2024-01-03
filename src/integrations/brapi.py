import logging
import os
import sys
import requests
import datetime as dt
import pandas as pd
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter, Retry


# Retry mechanism. If the status code is not 200, we retry the request up to 5 times.
class RetryIfNot200(Retry):
    def is_retry(self, method, status_code, has_retry_after=False):
        if status_code != 200:
            return True
        return False


def get_stocks_from_argv():
    if len(sys.argv) < 2:
        raise Exception("Please provide at least one stock as argument.")
    return [str(x).upper() for x in sys.argv[1:]]


def get_token():
    token = os.getenv("BRAPI_TOKEN", None)
    if token is None:
        raise Exception("Missing BRAPI_TOKEN environment variable")

    return token


def fetch_stock_data(stock, token):
    requests_retry = requests.Session()
    retries = RetryIfNot200(total=5, backoff_factor=0)
    requests_retry.mount("https://", HTTPAdapter(max_retries=retries))

    url = f"https://brapi.dev/api/quote/{stock}?range=1d&interval=1d&token={token}"
    request = requests_retry.get(url)
    request.raise_for_status()

    return request.json()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv()

    token = get_token()

    stocks = get_stocks_from_argv()
    print(f"Starting scraping for {stocks}")

    for stock in stocks:
        logging.debug(f"Fetching stock {stock}...")

        # Data from d-1.
        stock_data = fetch_stock_data(stock, token)
        stock_historical_data = stock_data["results"][0]["historicalDataPrice"]

        parsed_stock_data = []
        for shd in stock_historical_data:
            parsed_stock_data.append(
                {
                    "Date": dt.datetime.fromtimestamp(shd["date"]).strftime("%Y-%m-%d"),
                    "Open": shd["open"],
                    "High": shd["high"],
                    "Low": shd["low"],
                    "Close": shd["close"],
                    "Volume": shd["volume"],
                }
            )

        if os.path.exists(f"./data/stocks/{stock}.csv"):
            df_data = pd.read_csv(f"./data/stocks/{stock}.csv")
        else:
            df_data = pd.DataFrame(
                columns=["Date", "Open", "High", "Low", "Close", "Volume"]
            )
        df_stock = pd.DataFrame(parsed_stock_data)

        df_data.set_index("Date", inplace=True)
        df_stock.set_index("Date", inplace=True)

        df_merged = df_data.combine_first(df_stock)
        df_merged.to_csv(f"./data/stocks/{stock}.csv")

        logging.debug(f"Done fetching stock {stock}.")
