from dash import Output, Input, callback, html
from ..models import TABLES


@callback(
    Output("banana--menu", "children"),
    Input("banana--menu", "style"),
)
def load_menu(_):
    return [
        html.Li(
            html.A(table.pretty_name, href=f"/{table.name}", className="label"),
            className="menu-item",
        )
        for table in TABLES.tables
    ]
