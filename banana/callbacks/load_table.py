from dash import Output, Input, callback
from sqlalchemy import MetaData, Table, create_engine, select

from ..config import CONFIG
from ..models import TABLES


metadata = MetaData()


@callback(
    Output("banana--table", "columnDefs"),
    Output("banana--table", "rowData"),
    Output("banana--table", "getRowId"),
    Input("banana--select", "value"),
    prevent_initial_call=True,
)
def load_table(table_name: str):
    # Get table model
    table_model = TABLES[table_name]

    # Get table schema
    engine = create_engine(CONFIG.connection_string)
    table_data = Table(table_name, metadata, autoload_with=engine)

    # Create select statement
    query = select(
        getattr(table_data.c, table_model.primary_key.name),
        *[getattr(table_data.c, col.name) for col in table_model.columns],
    ).select_from(table_data)

    # Fetch results
    with engine.connect() as conn:
        result = conn.execute(query)
        rows = result.fetchall()

    # Define header
    id_col = [
        {
            "headerName": table_model.primary_key.pretty_name,
            "valueGetter": {"function": f"params.node.{table_model.primary_key.name}"},
            "editable": False,
        },
    ]
    values_cols = [
        {"headerName": col.pretty_name, "field": col.name}
        for col in table_model.columns
    ]
    column_defs = id_col + values_cols

    # Define Rows
    cols = [table_model.primary_key.name] + [col.name for col in table_model.columns]
    row_data = []
    for row in rows:
        row_data.append({col: value for col, value in zip(cols, row)})

    return column_defs, row_data, f"params.data.{table_model.primary_key.name}"
