from typing import Optional


class BananaError(Exception):
    """Base exception for all `banana` related errors."""

    pass


class InvalidForeignKey(BananaError):
    """Raised when a foreign key id or display column is duplicated or not null."""

    def __init__(
        self,
        table_name: str,
        column_name: str,
        message: Optional[str] = None,
    ):
        if message is None:
            message = f"Column '{column_name}' from table '{table_name}' has duplicated or not null values."

        self.table_name = table_name
        self.column_name = column_name
        self.message = message

        super().__init__(self.message)


class MultipleTablesWithSameName(BananaError):
    """Raised when multiple tables with the same name are found."""

    def __init__(self, table_name, message: Optional[str] = None):
        if message is None:
            message = f"Multiple tables with the name '{table_name}' were found. Please use a unique name."
        self.table_name = table_name
        self.message = message
        super().__init__(self.message)


class MultipleGroupsWithSameName(BananaError):
    """Raised when multiple tables with the same name are found."""

    def __init__(self, table_name, message: Optional[str] = None):
        if message is None:
            message = f"Multiple tables with the name '{table_name}' were found. Please use a unique name."
        self.table_name = table_name
        self.message = message
        super().__init__(self.message)
