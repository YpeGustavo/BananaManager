from dash.exceptions import PreventUpdate
from sqlalchemy import Column, ForeignKey, MetaData, Table, String, select

from ..core.config import db
from ..core.tables import BananaTable, tables
from ..core.utils import split_pathname
from ..queries import read_sql


class MainTableQuery:
    def __init__(self, banana_table: BananaTable):
        self.banana_table = banana_table
        self.metadata = MetaData()

        self.table = self.define_table()
        self.query = self.construct_query()

    def construct_query(self):
        table_alias = self.table.alias()
        columns_query = [table_alias.c[self.banana_table.primary_key]]

        joins_query = []
        for column in self.banana_table.columns:
            if column.dataType.type != "foreign":
                columns_query.append(
                    table_alias.c[column.name].label(column.display_name)
                )
            else:
                fk_table = Table(
                    column.dataType.data["tableName"],
                    self.metadata,
                    autoload_with=db.engine,
                    schema=column.dataType.data["schemaName"],
                )
                fk_table_alias = fk_table.alias()
                columns_query.append(
                    fk_table_alias.c[column.dataType.data["columnDisplay"]].label(
                        column.display_name
                    )
                )
                joins_query.append(
                    (
                        fk_table_alias,
                        table_alias.c[column.name]
                        == fk_table_alias.c[column.dataType.data["columnName"]],
                    )
                )

        query = select(*columns_query).select_from(table_alias)
        for fk_table_alias, join_condition in joins_query:
            query = query.outerjoin(fk_table_alias, join_condition)

        if self.banana_table.order_by is not None:
            for column in self.banana_table.order_by:
                if column.desc:
                    orderby = table_alias.c[column.column].desc()
                else:
                    orderby = table_alias.c[column.column].asc()
                query = query.order_by(orderby)

        if self.banana_table.limit is not None:
            query = query.limit(self.banana_table.limit)
        return query

    def define_table(self):
        columns = [Column(self.banana_table.primary_key, String, primary_key=True)]
        for column in self.banana_table.columns:
            if column.name == self.banana_table.primary_key:
                continue
            if column.dataType.type == "foreign":
                fk = ForeignKey(
                    f"{column.dataType.data['tableName']}.{column.dataType.data['columnName']}"
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


class LoadMainTableCallback:
    def __init__(self, pathname: str):
        group_name, table_name = split_pathname(pathname)
        if table_name is None:
            raise PreventUpdate
        self.banana_table = tables(group_name, table_name)

    @property
    def columnDefs(self) -> list[dict]:
        return [col.column_def for col in self.banana_table.columns]

    @property
    def rowData(self):
        sqlalchemy_table = MainTableQuery(self.banana_table)
        rows = read_sql(sqlalchemy_table.query)

        # Define Rows
        cols = [self.banana_table.primary_key] + [
            col.name for col in self.banana_table.columns
        ]
        row_data = []
        for row in rows:
            row_data.append({col: value for col, value in zip(cols, row)})

        return row_data

    @property
    def rowId(self) -> str:
        return f"params.data.{self.banana_table.primary_key}"

    @property
    def tableTitle(self) -> str:
        return self.banana_table.display_name

    @property
    def defaultColDef(self):
        return self.banana_table.defaultColDef

    @property
    def gridOptions(self):
        return self.banana_table.gridOptions
