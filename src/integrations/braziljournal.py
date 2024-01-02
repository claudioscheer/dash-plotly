import logging
import os
import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd
from requests.adapters import HTTPAdapter, Retry


def get_stocks_from_argv():
    if len(sys.argv) < 2:
        raise Exception("Please provide at least one stock as argument.")
    return [str(x).upper() for x in sys.argv[1:]]


# Retry mechanism. If the status code is not 200, we retry the request up to 5 times.
class RetryIfNot200(Retry):
    def is_retry(self, method, status_code, has_retry_after=False):
        if status_code != 200:
            return True
        return False


logging.basicConfig(level=logging.DEBUG)

requests_retry = requests.Session()
retries = RetryIfNot200(total=5, backoff_factor=2)
requests_retry.mount("https://", HTTPAdapter(max_retries=retries))

stocks = get_stocks_from_argv()
print(f"Starting scraping for {stocks}")

# The idea is to load the data from the CSV file if it exists, and append the new data to it.
# Using a real database would be better, as it would allow us to query the data more easily and use transactions.
if os.path.exists("./data/braziljournal.csv"):
    data = pd.read_csv("./data/braziljournal.csv")
else:
    data = pd.DataFrame(columns=["stock", "category", "title", "link"])

for stock in stocks:
    url = "https://braziljournal.com/?s={}".format(stock)
    response = requests_retry.get(url)

    if response.status_code != 200:
        raise Exception("Failed to load page {}".format(url))

    soup = BeautifulSoup(response.content, "html.parser")
    ul_allnews = soup.find("ul", {"id": "allnews"})

    if ul_allnews is None:
        raise Exception("Failed to find ul element with id allnews")

    # Delete the data for the current stock from the dataframe.
    data = data[data["stock"] != stock]

    for li in ul_allnews.find_all("li"):
        # Extract the category, title, and link.
        category = li.find("p", class_="boxarticle-infos-tag").text.strip()
        title = li.find("h2", class_="boxarticle-infos-title").text.strip()
        link = li.find("h2", class_="boxarticle-infos-title").a["href"]

        # Append the data to the list.
        data = data._append(
            {"stock": stock, "category": category, "title": title, "link": link},
            ignore_index=True,
        )

if not os.path.exists("./data"):
    os.makedirs("./data")

# Save the data to a CSV file.
df = pd.DataFrame(data)
df.to_csv("./data/braziljournal.csv", index=False)