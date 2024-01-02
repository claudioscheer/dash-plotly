import requests
import logging
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
from integrations.braziljournal import scrape_stock

logging.basicConfig(level=logging.DEBUG)

df = pd.read_csv("./data/braziljournal.csv")

app = Dash(__name__)
app.layout = html.Div(
    [
        html.Div(
            children=[
                dcc.Dropdown(
                    df.stock.unique(), df.stock.unique()[0], id="available-stocks"
                ),
                dcc.Graph(id="stock-graph"),
            ],
            style={"padding": 8, "flex": 1},
        ),
        html.Div(
            children=[
                html.H1(children="Notícias", style={"textAlign": "center"}),
                html.Div(id="stock-news"),
            ],
            style={"padding": 8, "flex": 1},
        ),
    ],
    style={
        "display": "flex",
        "flexDirection": "row",
        # "align-items": "center",
        # "width": "100%",
        # "height": "100vh",
    },
)


@callback(Output("stock-news", "children"), Input("available-stocks", "value"))
def update_news(value):
    try:
        scraped_data = scrape_stock(value, retry=False, timeout=1)
        logging.debug(f"Scraped {value} successfully.")
    except requests.exceptions.Timeout:
        logging.debug(f"Scraping {value} timed out. Using last data available.")
        scraped_data = df[df.stock == value].to_dict("records")

    return html.Ul(
        [
            html.Li(
                html.A(
                    children=[
                        html.P(children=item["category"]),
                        html.H2(children=item["title"]),
                    ],
                    href=item["link"],
                )
            )
            for item in scraped_data
        ]
    )


if __name__ == "__main__":
    app.run(debug=True)
