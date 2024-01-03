import logging
import os
import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd
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


def scrape_stock(stock, retry=True, timeout=10):
    url = "https://braziljournal.com/?s={}".format(stock)
    if retry:
        requests_retry = requests.Session()
        retries = RetryIfNot200(total=5, backoff_factor=2)
        requests_retry.mount("https://", HTTPAdapter(max_retries=retries))

        response = requests_retry.get(url, timeout=timeout)
    else:
        response = requests.get(url, timeout=timeout)

    if response.status_code != 200:
        raise Exception("Failed to load page {}".format(url))

    soup = BeautifulSoup(response.content, "html.parser")
    ul_allnews = soup.find("ul", {"id": "allnews"})

    if ul_allnews is None:
        raise Exception("Failed to find ul element with id allnews.")

    data = []

    for li in ul_allnews.find_all("li"):
        # Extract the category, title, and link.
        category = li.find("p", class_="boxarticle-infos-tag").text.strip()
        title = li.find("h2", class_="boxarticle-infos-title").text.strip()
        link = li.find("h2", class_="boxarticle-infos-title").a["href"]

        data.append(
            {"stock": stock, "category": category, "title": title, "link": link}
        )

    return data


def load_data():
    # The idea is to load the data from the CSV file if it exists, and append the new data to it.
    # Using a real database would be better, as it would allow us to query the data more easily and use transactions.
    if os.path.exists("./data/braziljournal.csv"):
        data = pd.read_csv("./data/braziljournal.csv")
    else:
        os.makedirs("./data")
        data = pd.DataFrame(columns=["stock", "category", "title", "link"])

    return data


def update_dataset(data, scraped_data, stock):
    # Delete the data for the current stock from the dataframe.
    data = data[data["stock"] != stock]
    df_stock = pd.DataFrame(scraped_data)
    data = pd.concat([data, df_stock])

    return data


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    stocks = get_stocks_from_argv()
    logging.debug(f"Starting scraping for {stocks}.")

    data = load_data()
    for stock in stocks:
        scraped_data = scrape_stock(stock)
        data = update_dataset(data, scraped_data, stock)

    # Save the data to a CSV file.
    data.to_csv("./data/braziljournal.csv", index=False)
