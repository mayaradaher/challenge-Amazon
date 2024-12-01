import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html

app = Dash(
    __name__,
    use_pages=True,
    title="Amazon Dashboard",
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)
server = app.server

# sidebar
sidebar = html.Div(
    [
        dbc.Row(
            [html.Img(src="assets/logos/amazon.svg", style={"height": "35px"})],
            className="sidebar-logo",
        ),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink(
                    "Purchase Overview", href="/puchase_overview", active="exact"
                ),
                dbc.NavLink(
                    "Customer demographics",
                    href="/customer_demographics",
                    active="exact",
                ),
                dbc.NavLink(
                    "Book recommendation", href="/book_recommendation", active="exact"
                ),
            ],
            vertical=True,
            pills=True,
        ),
        html.Div(
            [
                html.Span("Created by "),
                html.A(
                    "Mayara Daher",
                    href="https://github.com/mayaradaher",
                    target="_blank",
                ),
                html.Br(),
                html.Span("Data Source "),
                html.A(
                    "MIT Publication",
                    href="https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/YGLYDY",
                    target="_blank",
                ),
            ],
            className="subtitle-sidebar",
            style={"position": "absolute", "bottom": "10px", "width": "100%"},
        ),
    ],
    className="sidebar",
)


content = html.Div(
    className="page-content",
)

# defining font-awesome (icons) and fonts
app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        {%css%}
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
        <link rel="icon" href="/assets/logos/favicon.svg" type="image/x-icon">
    </head>
    <body>
        {%app_entry%}
        {%config%}
        {%scripts%}
        {%renderer%}
    </body>
</html>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap');
</style>
"""

# layout
app.layout = html.Div(
    [
        dcc.Location(id="url", pathname="/puchase_overview"),
        sidebar,
        content,
        dash.page_container,
    ]
)

if __name__ == "__main__":
    app.run_server(debug=False)
