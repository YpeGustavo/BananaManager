from sqlalchemy import Column, ForeignKey, MetaData, String, Table, select

from ...models import BananaTable
from ...utils import db


class MainTableQuery:
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
