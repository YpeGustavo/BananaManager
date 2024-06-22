from dash import dcc, html
from dash_ag_grid import AgGrid


layout = html.Div(
    [
        html.H1("Cadastro"),
        dcc.Dropdown(
            id="banana--select",
            placeholder="Select a table",
            clearable=False,
        ),
        AgGrid(
            id="banana--table",
            defaultColDef={"filter": True, "sortable": True, "editable": True},
            dashGridOptions={"pagination": True},
        ),
    ],
)
