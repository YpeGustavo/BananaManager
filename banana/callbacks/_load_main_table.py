from dash.exceptions import PreventUpdate

from ..core.tables import tables
from ..core.utils import split_pathname
from ..queries import select_table


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
        col_names = [self.banana_table.primary_key] + [
            col.name
            for col in self.banana_table.columns
            if col.name != self.banana_table.primary_key
        ]

        rows = select_table(
            table_name=self.banana_table.name,
            schema_name=self.banana_table.schema_name,
            columns=col_names,
        )

        banana_columns_without_pk = [
            col
            for col in self.banana_table.columns
            if col.name != self.banana_table.primary_key
        ]

        row_data = []
        for row in rows:
            col_value = {self.banana_table.primary_key: row[0]}
            for col, value in zip(banana_columns_without_pk, row[1:]):
                if col.dataType.type in ("foreign", "enumerator"):
                    col_value[col.name] = col.data.get(value)
                else:
                    col_value[col.name] = value
            row_data.append(col_value)
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
