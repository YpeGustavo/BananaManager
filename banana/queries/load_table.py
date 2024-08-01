from dash.exceptions import PreventUpdate
from sqlalchemy import Column, ForeignKey, MetaData, String, Table, select

from ..models import BananaColumn, BananaTable, get_table_model
from ..utils import read_sql, split_pathname, db


class SqlAlchemyStatement:
    def __init__(self, banana_table: BananaTable):
        self.banana_table = banana_table
        self.metadata = MetaData()

        self.table = self.define_table()
        self.query = self.construct_query()

    def construct_query(self):
        table_alias = self.table.alias()
        columns_query = [
            table_alias.c[self.banana_table.primary_key.name].label(
                self.banana_table.primary_key.display_name
            )
        ]

        joins_query = []

        for column in self.banana_table.columns:
            if column.foreign_key is None:
                columns_query.append(
                    table_alias.c[column.name].label(column.display_name)
                )
            else:
                fk_table = Table(
                    column.foreign_key.table_name,
                    self.metadata,
                    autoload_with=db.engine,
                    schema=column.foreign_key.schema_name,
                )
                fk_table_alias = fk_table.alias()
                columns_query.append(
                    fk_table_alias.c[column.foreign_key.column_display].label(
                        column.display_name
                    )
                )
                joins_query.append(
                    (
                        fk_table_alias,
                        table_alias.c[column.name]
                        == fk_table_alias.c[column.foreign_key.column_name],
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
    def __init__(self, pathname: str):
        group_name, table_name = split_pathname(pathname)
        if table_name is None:
            raise PreventUpdate

        self.banana_table = get_table_model(table_name, group_name)

    def __get_columns_def(self, column: BananaColumn) -> dict[str, str]:
        if column.foreign_key is None:
            return {
                "headerName": column.display_name,
                "field": column.name,
                "editable": column.editable,
                "filter": column.filter,
                "sortable": column.sortable,
            }

        else:
            metadata = MetaData()
            foreign_table = Table(
                column.foreign_key.table_name,
                metadata,
                schema=column.foreign_key.schema_name,
                autoload_with=db.engine,
            )

            query = select(foreign_table.c[column.foreign_key.column_display])
            query = query.select_from(foreign_table)

            if column.foreign_key.order_by is not None:
                for orderby_col in column.foreign_key.order_by:
                    if orderby_col.desc:
                        orderby = foreign_table.c[orderby_col.column].desc()
                    else:
                        orderby = foreign_table.c[orderby_col.column].asc()
                    query = query.order_by(orderby)

            rows = read_sql(query)

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
                "field": self.banana_table.primary_key.name,
                "editable": False,
                "filter": self.banana_table.primary_key.filter,
                "hide": self.banana_table.primary_key.hide,
                "sortable": self.banana_table.primary_key.sortable,
            },
        ]

        values_cols = [self.__get_columns_def(col) for col in self.banana_table.columns]
        return id_col + values_cols

    @property
    def row_data(self):
        sqlalchemy_table = SqlAlchemyStatement(self.banana_table)
        rows = read_sql(sqlalchemy_table.query)

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
