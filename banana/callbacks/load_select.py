from dash import Output, Input, callback
from ..models import TABLES


@callback(
    Output("banana--select", "options"),
    Input("banana--select", "style"),
)
def load_select(_):
    return [
        {"label": table.pretty_name, "value": table.name} for table in TABLES.tables
    ]
