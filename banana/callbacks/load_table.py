from dash import html, Output, Input, callback
import pandas as pd
from sqlalchemy import create_engine

from ..configs import CONFIG


@callback(
    Output("cadastro--table-head", "children"),
    Output("cadastro--table-body", "children"),
    Input("cadastro--select", "value"),
    prevent_initial_call=True,
)
def load_table(tablename: str):
    query = f"select * from {tablename}"

    engine = create_engine(CONFIG.connection_string)
    with engine.connect() as conn:
        df = pd.read_sql(query, con=conn)

    thead = html.Tr([html.Th(col) for col in df.columns])
    tbody = [html.Tr([html.Td(td) for td in row]) for _, row in df.iterrows()]

    return [thead, tbody]
