from sqlalchemy import MetaData, Table, create_engine, select

from ..models import Config, BananaColumn
from ..utils import get_table_model, read_sql


class LoadTableCallback:
    def __init__(self, pathname: str, config: Config, metadata: MetaData):
        self.pathname = pathname
        self.config = config
        self.metadata = metadata
        self.engine = create_engine(self.config.connection_string)
        self.banana_table = get_table_model(self.pathname[1:], self.config)

    def get_columns_def(self, column: BananaColumn) -> dict[str, str]:
        if column.foreign_key is None:
            return {
                "headerName": column.display_name,
                "field": column.name,
            }

        else:
            foreign_table = Table(
                column.foreign_key.table_name,
                self.metadata,
                schema=column.foreign_key.schema_name,
                autoload_with=self.engine,
            )

            stmt = select(foreign_table.c[column.foreign_key.column_display])
            stmt = stmt.select_from(foreign_table)
            rows = read_sql(stmt, self.engine)

            return {
                "headerName": column.display_name,
                "field": column.name,
                "editable": True,
                "cellEditor": "agSelectCellEditor",
                "cellEditorParams": {"values": [row[0] for row in rows]},
            }

    @property
    def column_defs(self) -> list[dict]:
        id_col = [
            {
                "headerName": self.banana_table.primary_key.display_name,
                "valueGetter": {
                    "function": f"params.node.{self.banana_table.primary_key.name}"
                },
                "editable": False,
            },
        ]

        values_cols = [self.get_columns_def(col) for col in self.banana_table.columns]
        return id_col + values_cols

    @property
    def row_data(self):
        table = Table(
            self.banana_table.name,
            self.metadata,
            schema=self.banana_table.schema_name,
            autoload_with=self.engine,
        )

        stmt_columns = [table.c[self.banana_table.primary_key.name]]
        joined_table = table

        for col in self.banana_table.columns:
            if col.foreign_key is None:
                try:
                    stmt_columns.append(table.c[col.name])
                except KeyError as e:
                    raise f"Column {col.name} not found in the table {table.name}"
            else:
                foreign_table = Table(
                    col.foreign_key.table_name,
                    self.metadata,
                    schema=col.foreign_key.schema_name,
                    autoload_with=self.engine,
                )
                joined_table = joined_table.outerjoin(
                    foreign_table,
                    joined_table.c[col.name]
                    == foreign_table.c[col.foreign_key.column_name],
                )
                stmt_columns.append(foreign_table.c[col.foreign_key.column_display])

        # Create select statement
        stmt = select(*stmt_columns).select_from(joined_table)
        rows = read_sql(stmt, self.engine)

        # Define Rows
        cols = [self.banana_table.primary_key.name] + [
            col.name for col in self.banana_table.columns
        ]
        row_data = []
        for row in rows:
            row_data.append({col: value for col, value in zip(cols, row)})

        return row_data

    @property
    def row_id(self) -> str:
        return f"params.data.{self.banana_table.primary_key.name}"

    @property
    def table_title(self) -> str:
        return self.banana_table.display_name
