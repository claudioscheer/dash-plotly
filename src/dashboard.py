import os
import requests
import logging
from dash import Dash, html, dcc, callback, Output, Input
import plotly.graph_objects as go
import pandas as pd
from integrations import braziljournal as bj
from lib.cache import cache_by_time

logging.basicConfig(level=logging.DEBUG)


# Since this df is updated once a day, we can cache it for some time. In this case, for 12 hours.
@cache_by_time(60 * 60 * 12)
def get_stock_df(stock):
    stock_file = f"./data/stocks/{stock}.csv"
    if os.path.exists(stock_file):
        return pd.read_csv(stock_file)

    raise Exception(f"Missing stock data for {stock}.")


def get_news_df():
    news_file = f"./data/braziljournal.csv"
    if os.path.exists(news_file):
        return pd.read_csv(news_file)

    raise Exception(f"Missing news data")


app = Dash(__name__)
app.layout = html.Div(
    [
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(style={"flex": 1}),
                        dcc.Dropdown(
                            ["CEAB3", "PETR4", "WEGE3"],
                            "CEAB3",
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
                html.H1(
                    children="Notícias",
                    style={"textAlign": "center", "marginBottom": 48},
                ),
                dcc.Loading(
                    id="loading-news",
                    type="default",
                    children=[
                        html.Div(id="loading-output-news"),
                        html.Div(id="stock-news", className="news"),
                    ],
                ),
            ],
            style={"padding": 8, "flex": 1},
        ),
    ],
    style={
        "display": "flex",
        "flexDirection": "row",
        # "alignItems": "center",
        # "width": "100%",
        # "height": "100vh",
        # "minHeight": "500px",
    },
)


@callback(
    Output("stock-news", "children"),
    Input("available-stocks", "value"),
)
def update_news(stock):
    try:
        scraped_data = bj.scrape_stock(stock, retry=False, timeout=1)

        # If we want, at this point we can update the dataset with the scraped data. I won't do that as I'm assuming we are going to run as a background process.
        # Here is a snippet of how we could do that:
        # > data = bj.load_data()
        # > data = bj.update_dataset(bj.load_data(), scraped_data, stock)
        # > data.to_csv("./data/braziljournal.csv", index=False)

        logging.debug(f"Scraped {stock} successfully.")
    except requests.exceptions.Timeout:
        logging.debug(f"Scraping {stock} timed out. Using last data available.")

        news_df = get_news_df()
        scraped_data = news_df[news_df.stock == stock].to_dict("records")

    return html.Ul(
        [
            html.Li(
                html.A(
                    children=[
                        html.P(children=item["category"]),
                        html.H3(children=item["title"]),
                    ],
                    href=item["link"],
                ),
                style={"paddingBottom": 16},
            )
            for item in scraped_data
        ]
    )


@callback(Output("stock-graph", "figure"), Input("available-stocks", "value"))
def update_graph(stock):
    df = get_stock_df(stock)

    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df["Date"],
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
            )
        ]
    )
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        autosize=True,
        margin=dict(l=0, r=0, b=8, t=8, pad=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)

    return fig


if __name__ == "__main__":
    app.run(debug=True)
