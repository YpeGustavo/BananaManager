from dash import dcc, html, Output, Input, callback
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
    table_model = next(table for table in TABLES if table.name == tablename)

    # Get table schema
    engine = create_engine(CONFIG.connection_string)
    table_data = Table(tablename, metadata, autoload_with=engine)

    # Create select statement
    query = select(
        getattr(table_data.c, table_model.primary_key),
        *[getattr(table_data.c, col.name) for col in table_model.columns],
    ).select_from(table_data)

    # Get datatype if none was provided
    for column in table_model.columns:
        if column.datatype is None:
            column.datatype = next(
                str(col.type) for col in table_data.columns if col.name == column.name
            )

    # Fetch results
    with engine.connect() as conn:
        result = conn.execute(query)
        rows = result.fetchall()

        # Build HTML
        thead = html.Tr([html.Th(col.pretty_name) for col in table_model.columns])
        tbody = []

        # Fill table body
        for row in rows:
            tr = []
            for col, value in zip(table_model.columns, row[1:]):
                id = {"table": table_model.name, "column": col.name, "row": row[0]}

                match col.datatype.lower():
                    case "int" | "integer":
                        td = dcc.Input(
                            value=value,
                            id=id,
                            type="number",
                            placeholder="null",
                        )
                    case "varchar" | "text" | "str" | "string":
                        td = dcc.Input(
                            value=value,
                            id=id,
                            type="text",
                            placeholder="null",
                        )

                tr.append(html.Td(td))
            tbody.append(html.Tr(tr))
        return [thead, tbody]
