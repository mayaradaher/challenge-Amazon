import dash
from dash import callback, dcc, html, Output, Input, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

dash.register_page(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    path="/book_recommendation",
)

# dataset
df = pd.read_json("data/ready/top10_grouped_book_purchases.json")

# load environment variables
load_dotenv()

# get API key
api_key = os.getenv("GOOGLE_API_KEY")

# initialize LLM model
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash", google_api_key=api_key
)  # gemini-1.5-flash ou gemini-1.5-pro

# create template
template = """
Question: Recommend three books based on the following query: {query}.
Here is an example of how the output should look like:
1. The Chronicles of Narnia
\nAuthor: C.S. Lewis \nYear: 1950 \nGenre: Fantasy \nDescription: A classic series of children's fantasy novels that follows the adventures of four siblings who discover a magical land called Narnia through a wardrobe. The books explore themes of good vs. evil, faith, and redemption, similar to Harry Potter's journey.

2. The Lord of the Rings
\nAuthor: J.R.R. Tolkien \nYear: 1954 \nGenre: Fantasy \nDescription: This epic fantasy trilogy tells the story of a group of hobbits who set out on a quest to destroy the One Ring, an artifact of immense power created by the Dark Lord Sauron. The series features intricate world-building, complex characters, and themes of courage, friendship, and sacrifice, much like Harry Potter.

3. The Percy Jackson & the Olympians series
\nAuthor: Rick Riordan \nYear: 2005 \nGenre: Fantasy \nDescription: This series follows Percy Jackson, a teenager who discovers he is the son of Poseidon, the Greek god of the sea. He attends a special school for demigods and embarks on a quest to save the world from the forces of evil. The books blend Greek mythology with modern-day adventures, similar to Harry Potter's magical world.

"""

# create prompt template
prompt = PromptTemplate(template=template, input_variables=["query"])

# create execution sequence using RunnableSequence
chain = prompt | llm


# extract personal user information
def get_user_info(user_id):
    try:
        user_row = df.loc[df["Survey ResponseID"] == user_id]
        if user_row.empty:
            print(f"User ID {user_id} not found.")
            return None

        user_info = user_row.iloc[0].to_dict()
        return user_info
    except Exception as e:
        print(f"Error fetching user info: {e}")
        return None


# extract user book purchases
def create_books_table(purchases):
    data = [
        {
            "Title": book["title"],
            "Author": book["authors"],
            "Category": book["categories"],
        }
        for book in purchases
    ]

    table = dash_table.DataTable(
        columns=[
            {"name": "Title", "id": "Title"},
            {"name": "Author", "id": "Author"},
            {"name": "Category", "id": "Category"},
        ],
        data=data,
        cell_selectable=False,
        filter_action="native",
        sort_action="native",
        sort_by=[
            {"column_id": "Title", "direction": "asc"},
            {"column_id": "Author", "direction": "asc"},
            {"column_id": "Category", "direction": "asc"},
        ],
        page_size=5,
        style_header={
            "fontFamily": "Inter, sans-serif",
            "font-size": "14px",
            "textAlign": "right",
            "fontWeight": "bold",
            "color": "#3a4552",
        },
        style_cell={
            "fontFamily": "Inter, sans-serif",
            "font-size": "14px",
            "textAlign": "left",
            "padding": "5px",
            "border": "1px solid #ececec",
            "whiteSpace": "normal",
            "overflow": "hidden",
            "textOverflow": "ellipsis",
        },
        style_cell_conditional=[
            {
                "if": {"column_id": "Title"},
                "width": "225px",
            },
            {
                "if": {"column_id": "Author"},
                "width": "225px",
            },
            {
                "if": {"column_id": "Category"},
                "width": "150px",
            },
        ],
        style_filter={
            "color": "#fff",  # filter icon
            "backgroundColor": "#fff",  # filter cell
        },
    )

    return table


# extract books recommendations
def get_recommendation(query, user_info):
    try:
        demographic_info = user_info["demographic"]
        book_info = user_info["books"]

        user_context = " ".join(
            [f"{key}: {value}" for key, value in demographic_info.items()]
        )

        purchased_books = " ".join(
            [
                f"{book['title']} by {book['authors']} ({book['categories']})"
                for book in book_info
            ]
        )

        # create user context for the model
        query_with_context = f"User details - {user_context}. Books previously purchased - {purchased_books}. {query}"

        response = chain.invoke({"query": query_with_context})
        response_text = response.content.strip()
        response_text = response_text.replace("*", "").replace("#", "")

        return response_text
    except Exception as e:
        print(f"Error fetching recommendations: {e}")
        return "Sorry, I couldn't process your request."


# layout
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc

layout = dbc.Container(
    [
        html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            html.H2(
                                [
                                    "Book recommendation Chatbot",
                                    html.Span(
                                        html.I(
                                            className="fa fa-info-circle",
                                            style={
                                                "fontSize": "18px",
                                                "color": "#f79500",
                                            },
                                        ),
                                        id="info-button",
                                        title="Click here for more information",
                                        style={
                                            "margin-left": "12px",
                                            "cursor": "pointer",
                                        },
                                    ),
                                ],
                                className="title",
                                style={
                                    "display": "flex",
                                    "align-items": "center",
                                },
                            ),
                            width=12,
                        ),
                    ]
                ),
                dbc.Tooltip(
                    "This page offers personalized book suggestions generated by the Gemini language model, which analyzes each user's profile and purchase history. To demonstrate how the recommendations work, we selected the 10 users with the highest investments in books.",
                    target="info-button",
                    placement="right",
                    trigger="click",
                    className="tooltip-inner",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Card(
                                [
                                    html.H4(
                                        "Instructions",
                                        className="subtitle-medium",
                                    ),
                                    html.Br(),
                                    html.H3(
                                        children=[
                                            "1. Please start your query with the word ",
                                            html.Span(
                                                "Book", style={"fontWeight": "bold"}
                                            ),
                                            ". For example:",
                                        ],
                                        className="subtitle-small",
                                    ),
                                    dcc.Markdown(
                                        """
                                        - Book like The Chronicles of Narnia
                                        - Book written by George Orwell
                                        - Book with a plot twist ending
                                        - Book adapted into a movie
                                        - Book translated into multiple languages
                                        - Book that won the Nobel Prize in Literature
                                        """,
                                        className="subtitle-small",
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dcc.Input(
                                                        id="query-input",
                                                        placeholder="Ask me for book recommendations",
                                                        className="search-input",
                                                    ),
                                                ],
                                            ),
                                        ]
                                    ),
                                    html.Br(),
                                    html.Br(),
                                    html.H3(
                                        "2. Select User",
                                        className="subtitle-small",
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dcc.Dropdown(
                                                        id="user-id-dropdown",
                                                        options=[
                                                            {
                                                                "label": f"User {user_id}",
                                                                "value": user_id,
                                                            }
                                                            for user_id in df[
                                                                "Survey ResponseID"
                                                            ]
                                                        ],
                                                        placeholder="Survey ResponseID",
                                                        className="custom-dropdown",
                                                    ),
                                                ],
                                                width=3,
                                            ),
                                        ]
                                    ),
                                    html.Br(),
                                    html.Button(
                                        [
                                            "Search",
                                            html.I(
                                                className="fa fa-search",
                                                style={"margin-left": "10px"},
                                            ),
                                        ],
                                        id="submit-button",
                                        n_clicks=0,
                                        className="btn-custom",
                                    ),
                                ],
                                className="card",
                                style={"padding": "25px"},
                            ),
                            width=12,
                        ),
                    ],
                ),
                html.Br(),
                dcc.Loading(
                    id="loading-recommendations",
                    type="circle",
                    color="#f79500",
                    children=[
                        html.Div(
                            id="user-info-output",
                            style={"padding": "0px 25px 15px 25px"},
                        ),
                        html.Div(
                            id="books-output",
                            style={"padding": "25px 25px 0px 25px"},
                        ),
                    ],
                ),
                html.Div(
                    id="recommendations-output",
                    style={"padding": "25px 25px 20px 25px"},
                ),
            ],
            className="page-content",
        )
    ],
    fluid=True,
)


# callback personal user information, user book purchases and books recommendations
@callback(
    [
        Output("user-info-output", "children"),
        Output("books-output", "children"),
        Output("recommendations-output", "children"),
    ],
    Input("submit-button", "n_clicks"),
    State("query-input", "value"),
    State("user-id-dropdown", "value"),
)
def update_recommendations(n_clicks, query, user_id):
    if n_clicks > 0:
        warnings = []

        # check if the user is selected
        user_warning = "Please select a User."
        if user_id is None:
            warnings.append(
                html.P(
                    user_warning,
                    className="text-danger",
                )
            )

        # check if there is a query and if it starts with "Book"
        query_warning = "Please start your query with the word 'Book'."
        if not query or not query.lower().startswith("book"):
            warnings.append(
                html.P(
                    query_warning,
                    className="text-danger",
                )
            )

        # add a combined warning if both conditions are met
        if user_id is None and (not query or not query.lower().startswith("book")):
            combined_warning = (
                "Please start your query with the word 'Book' and select a User."
            )
            warnings = [
                html.P(
                    combined_warning,
                    className="text-danger",
                )
            ]

        # if there are warnings, return them and skip further processing
        if warnings:
            return warnings, "", ""

        # proceed if no warnings
        user_info = get_user_info(user_id)
        if user_info is None:
            warnings.append(
                html.P(
                    "User information not found.",
                    className="text-danger",
                )
            )
            return warnings, "", ""

        # process personal user information and user book purchases
        demographic_info = user_info["demographic"]
        book_info = user_info["books"]

        # add title for personal user information
        user_info_title = html.H3(
            "User Demographic Information", className="subtitle-small-color"
        )

        # format personal user information as a list of paragraphs
        user_info_display = [
            html.P(f"{key}: {value}", className="user-info-text")
            for key, value in demographic_info.items()
        ]

        # combine title and user book purchases
        books_info_title = html.H3(
            "User's Book Purchase History", className="subtitle-small-color"
        )
        books_table = create_books_table(book_info)
        books_info_display = html.Div([books_info_title, books_table])

        recommendations = get_recommendation(query, user_info)

        if recommendations.startswith("Sorry"):
            return (
                warnings + [user_info_title] + user_info_display,
                books_info_display,
                recommendations,
            )

        # return books recommendations
        return (
            warnings + [user_info_title] + user_info_display,
            books_info_display,
            html.Pre(recommendations, className="text-recommendations"),
        )

    return "", "", ""
