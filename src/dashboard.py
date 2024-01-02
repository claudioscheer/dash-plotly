import os
import requests
import logging
from dotenv import load_dotenv
from dash import Dash, html, dcc, callback, Output, Input
import plotly.graph_objects as go
import pandas as pd
from integrations.braziljournal import scrape_stock
from integrations.brapi import fetch_stock_data

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

if not os.path.exists("./data/braziljournal.csv"):
    raise Exception(
        "Missing news data file. Run `python src/integrations/braziljournal.py CEAB3 WEGE3 PETR4` first."
    )

df = pd.read_csv("./data/braziljournal.csv")

app = Dash(__name__)
app.layout = html.Div(
    [
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(style={"flex": 1}),
                        dcc.Dropdown(
                            df.stock.unique(),
                            df.stock.unique()[0],
                            id="available-stocks",
                            style={"flex": 1},
                        ),
                        html.Div(style={"flex": 1}),
                    ],
                    style={"display": "flex", "flexDirection": "row"},
                ),
                dcc.Loading(
                    id="loading-graph",
                    type="default",
                    children=[
                        html.Div(id="loading-output-graph"),
                        dcc.Graph(id="stock-graph"),
                    ],
                ),
            ],
            style={"padding": 8, "flex": 1},
        ),
        html.Div(
            children=[
                html.H1(children="Notícias", style={"textAlign": "center"}),
                dcc.Loading(
                    id="loading-news",
                    type="default",
                    children=[
                        html.Div(id="loading-output-news"),
                        html.Div(id="stock-news"),
                    ],
                ),
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


@callback(
    Output("stock-news", "children"),
    Input("available-stocks", "value"),
)
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


@callback(Output("stock-graph", "figure"), Input("available-stocks", "value"))
def update_graph(value):
    stock_data = fetch_stock_data(value)

    df = pd.DataFrame(stock_data["results"][0]["historicalDataPrice"])
    # Convert the date from epoch to datetime.
    df["date"] = pd.to_datetime(df["date"], unit="s")

    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df["date"],
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],
            )
        ]
    )
    fig.update_layout(xaxis_rangeslider_visible=False)
    return fig


if __name__ == "__main__":
    app.run(debug=True)
