from typing import Optional


class BananaError(Exception):
    """Base exception for all `banana` related errors."""

    pass


class InvalidBananaForeignKey(BananaError):
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


class MultipleBananaTablesWithSameName(BananaError):
    """Raised when multiple tables with the same name are found."""

    def __init__(self, table_name, message: Optional[str] = None):
        if message is None:
            message = f"Multiple tables with the name '{table_name}' were found. Please use a unique name."
        self.table_name = table_name
        self.message = message
        super().__init__(self.message)


class MultipleBananaGroupsWithSameName(BananaError):
    """Raised when multiple tables with the same name are found."""

    def __init__(self, table_name, message: Optional[str] = None):
        if message is None:
            message = f"Multiple tables with the name '{table_name}' were found. Please use a unique name."
        self.table_name = table_name
        self.message = message
        super().__init__(self.message)


class NoBananaTableFound(BananaError):
    """Raised when no table is found."""

    def __init__(self, table_name, message: Optional[str] = None):
        if message is None:
            message = f"No table found with the name '{table_name}'."
        self.table_name = table_name
        self.message = message
        super().__init__(self.message)


class NoBananaTableSelected(BananaError):
    """Raised when no able is selected."""

    def __init__(
        self,
        message="No table has been selected. Please select a table before proceeding.",
    ):
        self.message = message
        super().__init__(self.message)
