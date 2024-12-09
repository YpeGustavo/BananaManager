from sqlalchemy import MetaData, Table, select, update

from ...core.config import config, db
from ...core.history import LogType, post_history
from ...core.tables import tables
from ...core.utils import raise_error, split_pathname


class UpdateCellCallback:
    def __init__(self, data: list[dict[str, str]], pathname: str):
        assert len(data) == 1, data

        self.col_id = data[0]["colId"]
        self.row_id = data[0]["rowId"]
        self.old_value = data[0]["oldValue"]
        self.new_value = data[0]["value"]

        self.metadata = MetaData()
        self.group_name, table_name = split_pathname(pathname)
        self.banana_table = tables(self.group_name, table_name)

    def exec(self):
        table_data = Table(
            self.banana_table.name,
            self.metadata,
            schema=self.banana_table.schema_name,
            autoload_with=db.engine,
        )

        banana_column = next(
            col for col in self.banana_table.columns if col.name == self.col_id
        )

        if banana_column.dataType.type == "foreign":
            foreign_table = Table(
                banana_column.dataType.data["tableName"],
                self.metadata,
                schema=banana_column.dataType.data["schemaName"],
                autoload_with=db.engine,
            )

            with db.engine.connect() as conn:
                id_col = foreign_table.c[banana_column.dataType.data["columnName"]]
                label = foreign_table.c[banana_column.dataType.data["columnDisplay"]]

                query = (
                    select(id_col)
                    .select_from(foreign_table)
                    .where(label == self.new_value)
                )

                result = conn.execute(query)
                rows = result.fetchall()
                self.new_value = rows[0][0]

        try:
            with db.engine.connect() as conn:
                query = (
                    update(table_data)
                    .where(table_data.c[self.banana_table.primary_key] == self.row_id)
                    .values({self.col_id: self.new_value})
                )
                conn.execute(query)
                conn.commit()

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

        except Exception as e:
            raise_error("Error updating cell", str(e.orig))
