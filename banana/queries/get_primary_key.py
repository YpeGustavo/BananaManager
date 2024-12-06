from sqlalchemy import Table, MetaData

from ..core.config import db


def get_primary_key(table_name: str, schema_name: str) -> str:
    """
    Check if a table has a primary key, ensure it has only one column, and return the column name.

    Args:
        table_name (str): Name of the table to check.

    Returns:
        str: The name of the primary key column.

    Raises:
        ValueError: If the table has no primary key or if the primary key consists of multiple columns.

    Example:
        get_primary_key_column('users')
        # Output: 'id'
    """

    metadata = MetaData(bind=db.engine)
    table = Table(
        table_name,
        metadata,
        schema=schema_name,
        autoload_with=db.engine,
    )

    # Get the primary key columns
    primary_key_columns = list(table.primary_key.columns)

    if not primary_key_columns:
        raise ValueError(f"The table '{table_name}' does not have a primary key.")

    if len(primary_key_columns) > 1:
        raise ValueError(
            f"The table '{table_name}' has a composite primary key: {', '.join(col.name for col in primary_key_columns)}"
        )

    # Return the single primary key column name
    return primary_key_columns[0].name
