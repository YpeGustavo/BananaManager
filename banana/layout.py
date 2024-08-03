from dash import dcc, html
from dash_ag_grid import AgGrid

from .utils import config


layout = html.Div(
    [
        dcc.Location(id="banana--location"),
        html.Div(id="banana--menu", className="left-section"),
        html.Div(
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(
                                id="banana--table-title",
                                className="table-title",
                            ),
                            html.Span(
                                [
                                    html.Button(
                                        "Refresh",
                                        id="banana--refresh-button",
                                        className="banana-button banana-button-refresh",
                                    )
                                ]
                            ),
                        ],
                        style={
                            "display": "flex",
                            "justify-content": "space-between",
                            "margin": "-10px 0 10px",
                        },
                    ),
                    AgGrid(
                        id="banana--table",
                        dashGridOptions=config.grid_options,
                        style={"height": "calc(100vh - 85px)", "overflow": "auto"},
                    ),
                ],
                className="content",
            ),
            className="right-section",
        ),
    ],
    className="container",
)
