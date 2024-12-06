from sqlalchemy import Table, MetaData, select, func
from sqlalchemy.exc import IntegrityError

from .check_duplicated_values import check_duplicated_values
from .execute_query import read_sql
from ..core.config import db


def create_foreign_key_options(
    table_name: str,
    schema_name: str,
    key_column: str,
    value_column: str,
) -> dict:
    """
    Fetch a mapping of unique key-value pairs from two specified columns of a table.
    Raises an error if duplicates are found in either column.

    Args:
        table_name (str): Name of the table to query.
        key_column (str): The column whose values will be the dictionary keys.
        value_column (str): The column whose values will be the dictionary values.

    Returns:
        dict: A dictionary where keys are values from the key_column and
              values are from the value_column.

    Raises:
        ValueError: If duplicates are found in either the key_column or the value_column.

    Example:
        get_unique_column_mapping('users', 'username', 'email')
        # Output: {'user1': 'email1@example.com', 'user2': 'email2@example.com'}
    """

    check_duplicated_values(table_name, schema_name, key_column)
    check_duplicated_values(table_name, schema_name, value_column)

    metadata = MetaData()
    table = Table(
        table_name,
        metadata,
        schema=schema_name,
        autoload_with=db.engine,
    )

    query = select(table.c[key_column], table.c[value_column])
    rows = read_sql(query)
    return {row[key_column]: row[value_column] for row in rows}
