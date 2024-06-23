from dash import dcc, html
from dash_ag_grid import AgGrid


layout = [
    dcc.Location(id="banana--location"),
    html.Div(
        html.Img(alt="Your logo here", className="logo"),
        className="navbar",
    ),
    html.Div(
        [
            html.Div(
                html.Div(
                    id="banana--menu",
                    className="menu",
                ),
                className="drawer",
            ),
            html.Div(
                [
                    html.Div("Metadados da Tabela"),
                    AgGrid(
                        id="banana--table",
                        defaultColDef={
                            "filter": True,
                            "sortable": True,
                            "editable": True,
                        },
                        dashGridOptions={"pagination": True},
                    ),
                ],
                className="main-content",
            ),
        ],
        className="container",
    ),
]
