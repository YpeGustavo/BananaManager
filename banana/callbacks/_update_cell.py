from ..core.config import config
from ..core.history import LogType, post_history
from ..core.tables import tables
from ..core.utils import split_pathname
from ..queries import update_cell


class UpdateCellCallback:
    def __init__(self, data: list[dict[str, str]], pathname: str):
        assert len(data) == 1, data

        # Get table name
        self.group_name, table_name = split_pathname(pathname)
        self.banana_table = tables(self.group_name, table_name)

        # Extract values from Ag Grid click data
        self.col_id = data[0]["colId"]
        self.row_id = data[0]["rowId"]
        self.old_value = data[0]["oldValue"]
        self.new_value = data[0]["value"]

        # Inverse values from labels
        banana_column = self.banana_table.get_column_by_name(self.col_id)
        if banana_column.dataType.type in ("foreign", "enumerator"):
            self.old_value = banana_column.data.inv.get(self.old_value)
            self.new_value = banana_column.data.inv.get(self.new_value)

    def exec(self):
        update_cell(
            table_name=self.banana_table.name,
            schema_name=self.banana_table.schema_name,
            row_id=self.row_id,
            column=self.col_id,
            new_value=self.new_value,
        )

        post_history(
            log_type=LogType.UPDATE,
            group_name=self.group_name,
            table_name=self.banana_table.name,
            schema_name=self.banana_table.schema_name,
            user_name=config.connection.username,
            log_data={
                "column_name": self.col_id,
                "row_id": self.row_id,
                "old_value": self.old_value,
                "new_value": self.new_value,
            },
        )
