from dash import Output, Input, callback
from ..configs import TABLES


@callback(
    Output("cadastro--select", "options"),
    Input("cadastro--select", "style"),
)
def load_select(_):
    options = []
    for table in TABLES["tables"]:
        label = table["pretty_name"]
        value = table["name"]
        options.append({"label": label, "value": value})

    return options
