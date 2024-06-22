from dash import Input, State, callback
from sqlalchemy import MetaData, Table, create_engine, update

from ..config import CONFIG
from ..models import TABLES


metadata = MetaData()


@callback(
    Input("banana--table", "cellValueChanged"),
    State("banana--select", "value"),
)
def update_cell(data, table_name):
    # Validate data
    assert len(data) == 1, data
    data = data[0]

    # Find the table model
    table_model = TABLES[table_name]

    # Update the database
    engine = create_engine(CONFIG.connection_string)
    table_data = Table(table_name, metadata, autoload_with=engine)

    with engine.connect() as conn:
        stmt = (
            update(table_data)
            .where(getattr(table_data.c, table_model.primary_key.name) == data["rowId"])
            .values({data["colId"]: data["value"]})
        )
        conn.execute(stmt)
        conn.commit()
