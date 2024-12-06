from sqlalchemy import Table, MetaData
from sqlalchemy.sql import insert

from .execute_query import exec_sql
from ..core.config import db


def insert_row(table_name: str, schema_name: str, values: dict) -> None:
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
        table_name,
        metadata,
        schema=schema_name,
        autoload_with=db.engine,
    )

    query = insert(table).values(**values)
    exec_sql(query)
