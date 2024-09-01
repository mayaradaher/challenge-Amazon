import dash
from dash import callback, dcc, html, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

dash.register_page(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    path="/customer_demographics",
)

# dataset
df = pd.read_parquet("data/ready/amazon_survey.parquet")

# layout
layout = dbc.Container(
    [
        html.Div(
            [
                html.H2(
                    "Customer demographics",  # title
                    className="title",
                ),
                html.H3(
                    "5,027 Users",  # title
                    className="subtitle-small",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Loading(
                                dcc.Graph(
                                    id="gender-chart",
                                    config={"displayModeBar": False},
                                    className="chart-card",
                                    style={"height": "280px"},
                                ),
                                type="circle",
                                color="#f79500",
                            ),
                            width=4,
                        ),
                        dbc.Col(
                            dcc.Loading(
                                dcc.Graph(
                                    id="age-chart",
                                    config={"displayModeBar": False},
                                    className="chart-card",
                                    style={"height": "280px"},
                                ),
                                type="circle",
                                color="#f79500",
                            ),
                            width=4,
                        ),
                        dbc.Col(
                            dcc.Loading(
                                dcc.Graph(
                                    id="education-chart",
                                    config={"displayModeBar": False},
                                    className="chart-card",
                                    style={"height": "280px"},
                                ),
                                type="circle",
                                color="#f79500",
                            ),
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
                                    id="state-chart",
                                    config={"displayModeBar": False},
                                    className="chart-card",
                                    style={"height": "337px"},
                                ),
                                type="circle",
                                color="#f79500",
                            ),
                            width=6,
                        ),
                        dbc.Col(
                            dcc.Loading(
                                dcc.Graph(
                                    id="income-chart",
                                    config={"displayModeBar": False},
                                    className="chart-card",
                                    style={"height": "337px"},
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
        Output("gender-chart", "figure"),
        Output("age-chart", "figure"),
        Output("education-chart", "figure"),
        Output("state-chart", "figure"),
        Output("income-chart", "figure"),
        Input("gender-chart", "id"),
        Input("age-chart", "id"),
        Input("education-chart", "id"),
        Input("state-chart", "id"),
        Input("income-chart", "id"),
    ],
)
def update_chart(gender, age, education, state, income):

    # gender
    gender_chart = px.pie(
        df,
        names="Q-demos-gender",
        hole=0.4,
        color="Q-demos-gender",
        title="Gender",
        color_discrete_map={
            "Female": "#f79500",
            "Male": "#b05611",
            "Other or prefer not to say": "#5e2d07",
        },
    )

    gender_chart.update_traces(
        textposition="outside",
        textinfo="percent+label",
        rotation=180,
        showlegend=False,
        texttemplate="%{label}<br>%{percent:.1%}",
        hoverlabel=dict(bgcolor="rgba(255, 255, 255, 0.1)", font_size=12),
        hovertemplate="<b>%{label}</b><br>Value: %{value:,}<br>",
    )

    gender_chart.update_layout(
        yaxis=dict(showticklabels=False), margin=dict(l=15, r=15, t=60, b=15)
    )

    # age
    age_counts = df["Q-demos-age"].value_counts().reset_index()
    age_counts.columns = ["Q-demos-age", "Count"]

    age_order = ["18 - 24", "25 - 34", "35 - 44", "45 - 54", "55 - 64", "65+"]
    age_counts["Q-demos-age"] = pd.Categorical(
        age_counts["Q-demos-age"], categories=age_order, ordered=True
    )

    age_counts = age_counts.sort_values(by="Q-demos-age")

    age_chart = px.bar(
        age_counts,
        x="Q-demos-age",
        y="Count",
        text_auto=".2s",
        text="Count",
        title="Age",
    )

    age_chart.update_traces(
        marker_color="#b05611",
        textposition="auto",
        hoverlabel=dict(bgcolor="rgba(255, 255, 255, 0.1)", font_size=12),
        hovertemplate="<b>%{x}</b><br>Value: %{y:,}<extra></extra>",
    )

    age_chart.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        plot_bgcolor="rgba(0, 0, 0, 0)",
        yaxis=dict(showticklabels=False),
        margin=dict(l=15, r=15, t=60, b=15),
    )

    # education
    education_counts = df["Q-demos-education"].value_counts().reset_index()
    education_counts.columns = ["Q-demos-education", "Count"]

    education_order = [
        "Prefer not to say",
        "Graduate or professional degree",
        "Bachelor's degree",
        "High school diploma or GED",
        "Some high school or less",
    ]
    education_counts["Q-demos-education"] = pd.Categorical(
        education_counts["Q-demos-education"], categories=education_order, ordered=True
    )

    education_counts = education_counts.sort_values(by="Q-demos-education")

    education_chart = px.bar(
        education_counts,
        y="Q-demos-education",
        x="Count",
        text_auto=".2s",
        text="Count",
        title="Education Level",
    )

    education_chart.update_traces(
        marker_color="#f79500",
        textposition="auto",
        hoverlabel=dict(bgcolor="rgba(255, 255, 255, 0.1)", font_size=12),
        hovertemplate="<b>%{y}</b><br>Value: %{x:,}<extra></extra>",
    )

    education_chart.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        plot_bgcolor="rgba(0, 0, 0, 0)",
        xaxis=dict(showticklabels=False),
        margin=dict(l=15, r=15, t=60, b=15),
    )

    # state
    df_filtered = df.loc[df["State Code"] != "No information"]

    state_counts = df_filtered["State Code"].value_counts().reset_index()
    state_counts.columns = ["State Code", "Users"]

    df_state = df_filtered.merge(state_counts, on="State Code")

    custom_colorscale = [(0, "#ffb803"), (0.5, "#cb7721"), (1, "#803f0c")]

    state_chart = px.choropleth(
        df_state,
        locations="State Code",
        featureidkey="properties.abbreviation",
        locationmode="USA-states",
        color="Users",
        color_continuous_scale=custom_colorscale,
        scope="usa",
        title="Users by State",
        hover_data=["Q-demos-state"],  # Inclui a coluna "State" no hover
    )

    state_chart.update_traces(
        hoverlabel=dict(bgcolor="rgba(255, 255, 255, 0.1)", font_size=12),
        hovertemplate="<b>%{customdata[0]}</b><br>Value: %{z:,}<extra></extra>",  # Mostra o nome do estado e o número de usuários
    )

    state_chart.update_layout(
        margin=dict(l=15, r=15, t=60, b=15),
    )

    # income
    income_counts = df["Q-demos-income"].value_counts().reset_index()
    income_counts.columns = ["Q-demos-income", "Count"]

    income_order = [
        "Prefer not to say",
        "Over $150K",
        "$100 - $149.9K",
        "$75 - $99.9K",
        "$50 - $74.9K",
        "$25 - $49.9K",
        "Under $25K",
    ]
    income_counts["Q-demos-income"] = pd.Categorical(
        income_counts["Q-demos-income"], categories=income_order, ordered=True
    )

    income_counts = income_counts.sort_values(by="Q-demos-income")

    income_chart = px.bar(
        income_counts,
        y="Q-demos-income",
        x="Count",
        text_auto=".2s",
        text="Count",
        title="Household Income",
    )

    income_chart.update_traces(
        marker_color="#b05611",
        textposition="auto",
        hoverlabel=dict(bgcolor="rgba(255, 255, 255, 0.1)", font_size=12),
        hovertemplate="<b>%{y}</b><br>Value: %{x:,}<extra></extra>",
    )

    income_chart.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        plot_bgcolor="rgba(0, 0, 0, 0)",
        xaxis=dict(showticklabels=False),
        margin=dict(l=15, r=15, t=60, b=15),
    )

    return (
        gender_chart,
        age_chart,
        education_chart,
        state_chart,
        income_chart,
    )
