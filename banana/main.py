from importlib import resources

from dash import Dash, Input, Output, State, html, ALL, ctx

from .queries import InitApp, LoadMenuCallback, LoadTableCallback, UpdateCellCallback
from .layout import layout
from .models import BananaTables
from .utils import read_yaml, config, server


class Banana(Dash):
    def __init__(self):
        with server.app_context():
            obj = InitApp()
            obj.refresh()

        super().__init__(
            server=server,
            assets_folder=resources.files("banana") / "assets",
            title=config.title,
        )
        self.layout = layout

        @self.callback(
            Output("banana--menu", "children"),
            Input("banana--location", "pathname"),
        )
        def load_menu(pathname: str):
            obj = LoadMenuCallback(pathname)
            return obj.menu

        @self.callback(
            Output("banana--table", "columnDefs"),
            Output("banana--table", "rowData"),
            Output("banana--table", "getRowId"),
            Output("banana--table-title", "children"),
            Input("banana--location", "pathname"),
            prevent_initial_call=True,
        )
        def load_table(pathname: str):
            obj = LoadTableCallback(pathname)
            return obj.column_defs, obj.row_data, obj.row_id, obj.table_title

        @self.callback(
            Input("banana--table", "cellValueChanged"),
            State("banana--location", "pathname"),
        )
        def update_cell(data, pathname):
            obj = UpdateCellCallback(data, pathname)
            obj.exec()