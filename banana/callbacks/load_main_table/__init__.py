from dash.exceptions import PreventUpdate
from sqlalchemy import MetaData, Table, select

from .main_table_query import MainTableQuery
from ...core.config import db
from ...core.tables import BananaColumn, get_table_model
from ...core.utils import split_pathname
from ...queries import read_sql


class LoadMainTableCallback:
    def __init__(self, pathname: str):
        group_name, table_name = split_pathname(pathname)
        if table_name is None:
            raise PreventUpdate
        self.banana_table = get_table_model(group_name, table_name)

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
