from sqlalchemy import Table, MetaData, delete

from .execute_query import exec_sql
from ..core.config import db


def delete_row(table_name: str, schema_name: str, row_id: int) -> None:
    """Delete a row from a specified table using SQLAlchemy ORM.

    Parameters
    ----------
    banana_table : BananaTable
        Name of the table where the row should be deleted.
    row_id : int
        The ID of the row to delete.

    Example
    -------
    >>> delete_row('users', 1)

    """

    metadata = MetaData()
    table = Table(
        table_name,
        metadata,
        schema=schema_name,
        autoload_with=db.engine,
    )

    query = delete(table).where(table.c.id == row_id)
    exec_sql(query)
