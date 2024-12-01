import dash
from dash import callback, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from utils.functions import create_card
import pandas as pd
import plotly.express as px

dash.register_page(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    path="/puchase_overview",
)

import warnings

warnings.filterwarnings("ignore")

# dataset
df = pd.read_parquet(
    "data/ready/amazon_purchases.parquet",
    columns=[
        "Survey ResponseID",
        "Order Date Year",
        "Order Date Month",
        "Category",
        "Quantity",
        "Purchase Total",
    ],
)

# df = pd.read_parquet("data/ready/amazon_purchases.parquet")

# layout
layout = dbc.Container(
    [
        html.Div(
            [
                html.H2(
                    "Purchase overview",  # title
                    className="title",
                ),
                html.Br(),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H3(
                                    "Select Year",
                                    className="subtitle-small",
                                ),
                                dcc.Dropdown(
                                    id="year-dropdown",
                                    options=[
                                        {"label": "All (2018-2022)", "value": "All"}
                                    ]
                                    + [
                                        {"label": col, "value": col}
                                        for col in sorted(
                                            df["Order Date Year"].unique()
                                        )
                                    ],
                                    value="All",
                                    clearable=True,
                                    multi=False,
                                    placeholder="Select here",
                                    className="custom-dropdown",
                                ),
                            ],
                            width=4,
                        ),
                    ]
                ),
                html.Br(),
                dbc.Row(
                    [
                        dbc.Col(
                            create_card("Purchases", "purchases-card", "fa-list"),
                            width=4,
                        ),
                        dbc.Col(
                            create_card("Total Spend", "spend-card", "fa-coins"),
                            width=4,
                        ),
                        dbc.Col(
                            create_card("Top Category", "category-card", "fa-tags"),
                            width=4,
                        ),
                    ],
                ),
                html.Br(),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Loading(
                                dcc.Graph(
                                    id="sales-chart",
                                    config={"displayModeBar": False},
                                    className="chart-card",
                                    style={"height": "400px"},
                                ),
                                type="circle",
                                color="#f79500",
                            ),
                            width=6,
                        ),
                        dbc.Col(
                            dcc.Loading(
                                dcc.Graph(
                                    id="category-chart",
                                    config={"displayModeBar": False},
                                    className="chart-card",
                                    style={"height": "400px"},
                                ),
                                type="circle",
                                color="#f79500",
                            ),
                            width=6,
                        ),
                    ],
                ),
            ],
            className="page-content",
        )
    ],
    fluid=True,
)


# callback cards and graphs
@callback(
    [
        Output("purchases-card", "children"),
        Output("spend-card", "children"),
        Output("category-card", "children"),
        Output("sales-chart", "figure"),
        Output("category-chart", "figure"),
    ],
    [
        Input("year-dropdown", "value"),
    ],
)
def update_values(select_year):

    filtered_df = df.copy()

    # filter
    if select_year and select_year != "All":
        filtered_df = filtered_df[filtered_df["Order Date Year"] == select_year]

    # cards
    purchases_card = f"{filtered_df['Quantity'].count():,.0f}"
    spend_card = f"$ {round(filtered_df['Purchase Total'].sum(), -2):,.0f}"
    category_card = (
        filtered_df.groupby("Category")["Survey ResponseID"].nunique().idxmax()
    )

    # sales
    sales_chart = px.bar(
        filtered_df.groupby("Order Date Month", observed=True)["Purchase Total"]
        .sum()
        .reset_index(),
        x="Order Date Month",
        y="Purchase Total",
        text_auto=".2s",
        title="Total Monthly Spend",
    )

    sales_chart.update_traces(
        textposition="outside",
        marker_color="#f79500",
        hoverlabel=dict(bgcolor="rgba(255, 255, 255, 0.1)", font_size=12),
        hovertemplate="<b>%{x}</b><br>Value: %{y:,}<extra></extra>",
    )

    sales_chart.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        plot_bgcolor="rgba(0, 0, 0, 0)",
        yaxis=dict(showticklabels=False),
        margin=dict(l=35, r=35, t=60, b=40),
    )

    # category
    category_chart = px.treemap(
        filtered_df.groupby("Category", as_index=False, observed=True)["Quantity"]
        .count()
        .nlargest(5, columns="Quantity"),
        path=["Category"],
        values="Quantity",
        title="Top 5 Purchase Categories",
        color="Category",
        color_discrete_sequence=["#cb7721", "#b05611", "#ffb803", "#F79500", "#803f0c"],
    )

    category_chart.data[0].textinfo = "label+value"

    category_chart.update_traces(textfont=dict(size=13))

    category_chart.update_layout(margin=dict(l=35, r=35, t=60, b=35), hovermode=False)

    return purchases_card, spend_card, category_card, sales_chart, category_chart
