import dash_bootstrap_components as dbc
from dash import html


def create_card(title, card_id, icon_class):
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(
                    [
                        html.I(
                            className=f"fas {icon_class} card-icon",
                        ),
                        html.H3(title, className="card-title"),
                    ],
                    className="d-flex align-items-center",
                ),
                html.H4(id=card_id),
            ],
            className="card-body",
        ),
        className="card",
    )
