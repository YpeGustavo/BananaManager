from sqlalchemy import (
    Column,
    Engine,
    ForeignKey,
    MetaData,
    String,
    Table,
    create_engine,
    select,
)

from ..models import Config, BananaColumn, BananaTable
from ..utils import get_table_model, read_sql


class SqlAlchemyStatement:
    def __init__(self, banana_table: BananaTable, engine: Engine):
        self.banana_table = banana_table
        self.engine = engine
        self.metadata = MetaData()

        self.table = self.define_table()
        self.stmt = self.construct_stmt()

    def construct_stmt(self):
        table_alias = self.table.alias()
        columns_stmt = [
            table_alias.c[self.banana_table.primary_key.name].label(
                self.banana_table.primary_key.display_name
            )
        ]

        joins_stmt = []

        for column in self.banana_table.columns:
            if column.foreign_key is None:
                columns_stmt.append(
                    table_alias.c[column.name].label(column.display_name)
                )
            else:
                fk_table = Table(
                    column.foreign_key.table_name,
                    self.metadata,
                    autoload_with=self.engine,
                    schema=column.foreign_key.schema_name,
                )
                fk_table_alias = fk_table.alias()
                columns_stmt.append(
                    fk_table_alias.c[column.foreign_key.column_display].label(
                        column.display_name
                    )
                )
                joins_stmt.append(
                    (
                        fk_table_alias,
                        table_alias.c[column.name]
                        == fk_table_alias.c[column.foreign_key.column_name],
                    )
                )

        query = select(*columns_stmt).select_from(table_alias)
        for fk_table_alias, join_condition in joins_stmt:
            query = query.outerjoin(fk_table_alias, join_condition)

        return query

    def define_table(self):
        columns = [Column(self.banana_table.primary_key.name, String, primary_key=True)]

        for column in self.banana_table.columns:
            if column.foreign_key:
                fk = ForeignKey(
                    f"{column.foreign_key.table_name}.{column.foreign_key.column_name}"
                )
                columns.append(Column(column.name, String, fk))
            else:
                columns.append(Column(column.name, String))

        table = Table(
            self.banana_table.name,
            self.metadata,
            *columns,
            schema=self.banana_table.schema_name,
        )

        return table


class LoadTableCallback:
    def __init__(self, pathname: str, config: Config):
        self.engine = create_engine(config.connection_string)
        self.banana_table = get_table_model(pathname[1:], config)

    def __get_columns_def(self, column: BananaColumn) -> dict[str, str]:
        if column.foreign_key is None:
            return {
                "headerName": column.display_name,
                "field": column.name,
            }

        else:
            metadata = MetaData()
            foreign_table = Table(
                column.foreign_key.table_name,
                metadata,
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

        values_cols = [self.__get_columns_def(col) for col in self.banana_table.columns]
        return id_col + values_cols

    @property
    def row_data(self):
        sqlalchemy_table = SqlAlchemyStatement(self.banana_table, self.engine)
        rows = read_sql(sqlalchemy_table.stmt, self.engine)

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
