from sqlalchemy import Table, MetaData
from sqlalchemy.sql import insert

from .execute_query import exec_sql
from ..core.config import db
from ..core.tables import BananaTable


def insert_row(banana_table: BananaTable, values: dict) -> None:
    """Insert a row into a specified table using SQLAlchemy ORM.

    Parameters
    ----------
    table_name : BananaTable
        Name of the table where the row should be inserted.
    values : dict
        A dictionary where keys are column names and values are the corresponding data to insert.

    Example
    -------
    >>> insert_row('users', {'name': 'John Doe', 'email': 'john.doe@example.com'})

    """

    metadata = MetaData(bind=db.engine)
    table = Table(
        banana_table.name,
        metadata,
        schema=banana_table.schema_name,
        autoload_with=db.engine,
    )

    query = insert(table).values(**values)
    exec_sql(query)
