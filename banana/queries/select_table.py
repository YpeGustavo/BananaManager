from sqlalchemy import MetaData, Table, select

from .execute_query import read_sql
from ..core.config import db


def select_table(table_name: str, schema_name: str, columns: list[str]):
    metadata = MetaData()
    table = Table(
        table_name,
        metadata,
        schema=schema_name,
        autoload_with=db.engine,
    )

    cols = [table.c[column] for column in columns]
    query = select(*cols).select_from(table)
    return read_sql(query)
