from sqlalchemy import MetaData, Table, select

from ._execute_query import read_sql
from ..core.config import db


def select_table(banana_table):
    # Get names of the columns
    col_names = [col.name for col in banana_table.columns]
    if add_pk := (banana_table.primary_key not in col_names):
        col_names.append(banana_table.primary_key)

    # Create table instance
    metadata = MetaData()
    table = Table(
        banana_table.name,
        metadata,
        schema=banana_table.schema_name,
        autoload_with=db.engine,
    )

    # Write query
    cols = [table.c[column] for column in col_names]
    query = select(*cols).select_from(table)

    if banana_table.order_by is not None:
        for column in banana_table.order_by:
            if column.desc:
                orderby = table.c[column.column].desc()
            else:
                orderby = table.c[column.column].asc()
            query = query.order_by(orderby)

    if banana_table.limit is not None:
        query = query.limit(banana_table.limit)

    # Execute
    rows = read_sql(query)
    row_data = []
    for row in rows:
        col_value = dict()
        for col, value in zip(banana_table.columns, row):
            if col.dataType.type in ("foreign", "enumerator"):
                col_value[col.name] = col.data.get(value)
            else:
                col_value[col.name] = value
        if add_pk:
            col_value[banana_table.primary_key] = row[-1]
        row_data.append(col_value)
    return row_data
