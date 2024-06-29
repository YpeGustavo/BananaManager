from sqlalchemy import MetaData, Table, create_engine, select, update

from ..models import Config
from ..utils import get_table_model


class UpdateCellCallback:
    def __init__(
        self,
        data: list[dict[str, str]],
        pathname: str,
        config: Config,
        metadata: MetaData,
    ):
        # Validate data
        assert len(data) == 1, data

        self.col_id = data[0]["colId"]
        self.row_id = data[0]["rowId"]
        self.new_value = data[0]["value"]

        self.metadata = metadata
        self.engine = create_engine(config.connection_string)
        self.banana_table = get_table_model(pathname[1:], config)

    def exec(self):
        table_data = Table(
            self.banana_table.name,
            self.metadata,
            autoload_with=self.engine,
        )

        banana_column = next(
            col for col in self.banana_table.columns if col.name == self.col_id
        )

        if banana_column.foreign_key is not None:
            foreign_table = Table(
                banana_column.foreign_key.table_name,
                self.metadata,
                autoload_with=self.engine,
            )

            with self.engine.connect() as conn:
                id_col = foreign_table.c[banana_column.foreign_key.column_name]
                label = foreign_table.c[banana_column.foreign_key.column_display]

                stmt = (
                    select(id_col)
                    .select_from(foreign_table)
                    .where(label == self.new_value)
                )

                result = conn.execute(stmt)
                rows = result.fetchall()
                self.new_value = rows[0][0]

        with self.engine.connect() as conn:
            stmt = (
                update(table_data)
                .where(table_data.c[self.banana_table.primary_key.name] == self.row_id)
                .values({self.col_id: self.new_value})
            )
            conn.execute(stmt)
            conn.commit()
