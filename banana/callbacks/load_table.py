from dash import html, Output, Input, callback
from sqlalchemy import MetaData, Table, create_engine, select

from ..config import CONFIG
from ..models import TABLES


metadata = MetaData()


@callback(
    Output("banana--table-head", "children"),
    Output("banana--table-body", "children"),
    Input("banana--select", "value"),
    prevent_initial_call=True,
)
def load_table(tablename: str):
    # Get table model
    table = next(table for table in TABLES if table.name == tablename)

    # Get table schema
    engine = create_engine(CONFIG.connection_string)
    tabledata = Table(tablename, metadata, autoload_with=engine)

    # Create select statement
    if table.columns is None:
        query = select(tabledata)
    else:
        query = select(
            *[
                getattr(tabledata.c, col.name).label(col.pretty_name)
                for col in table.columns
            ]
        ).select_from(tabledata)

    # Print datatypes
    print([(col.name, str(col.type)) for col in tabledata.columns])

    # Get data
    with engine.connect() as conn:
        result = conn.execute(query)
        columns = result.keys()

        # Build HTML
        thead = html.Tr([html.Th(col) for col in columns])
        tbody = [
            html.Tr([html.Td(value) for value in row]) for row in result.fetchall()
        ]
        return [thead, tbody]
