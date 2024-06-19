from dash import Output, Input, callback
from ..configs import TABLES


@callback(
    Output("cadastro--select", "options"),
    Input("cadastro--select", "style"),
)
def load_select(_):
    return [{"label": table.pretty_name, "value": table.name} for table in TABLES]
