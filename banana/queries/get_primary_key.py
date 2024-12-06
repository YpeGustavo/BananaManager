from sqlalchemy import Table, MetaData

from ..core.config import db
from ..core.tables import BananaTable


def get_primary_key(banana_table: BananaTable) -> str:
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
        banana_table.name,
        metadata,
        schema=banana_table.schema_name,
        autoload_with=db.engine,
    )

    # Get the primary key columns
    primary_key_columns = list(table.primary_key.columns)

    if not primary_key_columns:
        raise ValueError(
            f"The table '{banana_table.name}' does not have a primary key."
        )

    if len(primary_key_columns) > 1:
        raise ValueError(
            f"The table '{banana_table.name}' has a composite primary key: {', '.join(col.name for col in primary_key_columns)}"
        )

    # Return the single primary key column name
    return primary_key_columns[0].name
