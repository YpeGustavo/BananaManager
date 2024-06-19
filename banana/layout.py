from dash import dcc, html


layout = html.Div(
    [
        html.H1("Cadastro"),
        dcc.Dropdown(
            id="banana--select", placeholder="Select a table", clearable=False
        ),
        html.Table(
            [
                html.Thead(id="banana--table-head"),
                html.Tbody(id="banana--table-body"),
            ],
            id="banana--table",
        ),
    ],
)
