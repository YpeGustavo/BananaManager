from sqlalchemy import Table, MetaData, update

from .execute_query import exec_sql
from ..core.config import db


def update_cell(
    table_name: str,
    schema_name: str,
    row_id: int,
    column: str,
    new_value,
) -> None:
    """Update a cell in a specified table using SQLAlchemy ORM.

    Parameters
    ----------
    banana_table : BananaTable
        Name of the table where the cell should be updated.
    match_condition : dict
        A dictionary specifying the condition to match the row to update.
        Example: {'id': 1} matches a row with id=1.
    column : str
        The column to be updated.
    new_value : Any
        The new value to assign to the specified column.

    Example
    -------
    >>> update_cell('users', {'id': 1}, 'email', 'new_email@example.com')

    """

    metadata = MetaData(bind=db.engine)
    table = Table(
        table_name,
        metadata,
        schema=schema_name,
        autoload_with=db.engine,
    )

    query = update(table).where(table.c.id == row_id).values({column: new_value})
    exec_sql(query)
