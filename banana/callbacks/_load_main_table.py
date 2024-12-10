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
        return select_table(self.banana_table)

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
