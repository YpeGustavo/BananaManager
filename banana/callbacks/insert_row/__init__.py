from time import time

from dash import no_update

from ...core.history import LogType, post_history
from ...core.config import config
from ...core.tables import get_table_model
from ...core.utils import raise_error, split_pathname
from ...queries import insert_row


class InsertRowCallback:
    def __init__(self, pathname, fields):
        self.group_name, table_name = split_pathname(pathname)
        self.banana_table = get_table_model(self.group_name, table_name)
        self.values = self.get_values(fields)

    def get_values(self, fields):
        return {
            field["id"]["column"]: field["value"] for field in fields if field["value"]
        }

    def exec(self):
        try:
            insert_row(self.banana_table, self.values)
            post_history(
                log_type=LogType.INSERT,
                group_name=self.group_name,
                table_name=self.banana_table.name,
                schema_name=self.banana_table.schema_name,
                user_name=config.connection.username,
                log_data=self.values,
            )
            return False, int(time())

        except Exception as e:
            raise_error("Error inserting row", str(e.orig))
            return no_update, no_update
