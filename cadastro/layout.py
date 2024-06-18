from dash import dcc, html


layout = html.Div(
    [
        html.H1("Cadastro"),
        dcc.Dropdown(
            id="cadastro--select", placeholder="Select a table", clearable=False
        ),
        html.Table(
            [
                html.Thead(id="cadastro--table-head"),
                html.Tbody(id="cadastro--table-body"),
            ],
            id="cadastro--table",
        ),
    ],
)
