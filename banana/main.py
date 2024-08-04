from importlib import resources
from os import environ

from dash import Dash, Input, Output, State, ctx, ALL, _dash_renderer
from dash.exceptions import PreventUpdate

from .callbacks import (
    InitApp,
    InsertRow,
    LoadForm,
    LoadMenuCallback,
    LoadTableCallback,
    UpdateCellCallback,
)
from .layout import Layout
from .utils import config, server


_dash_renderer._set_react_version("18.2.0")


def refresh():
    with server.app_context():
        obj = InitApp()
        obj.refresh()


class Banana(Dash):
    def __init__(self):
        refresh()
        super().__init__(
            server=server,
            assets_folder=resources.files("banana") / "assets",
            title=config.title,
        )
        self.layout = Layout()

        @self.callback(
            Output("banana--menu", "children"),
            Input("banana--location", "pathname"),
            Input("banana--refresh-button", "n_clicks"),
        )
        def load_menu(pathname: str, _):
            if ctx.triggered_id == "banana--refresh-button":
                refresh()
            obj = LoadMenuCallback(pathname)
            return obj.menu

        @self.callback(
            Output("banana--location", "pathname"),
            Input({"component": "menu-item", "group": ALL, "table": ALL}, "n_clicks"),
            prevent_initial_call=True,
        )
        def change_pathname(_):
            if len(ctx.triggered) != 1:
                raise PreventUpdate
            return f"/{ctx.triggered_id['group']}/{ctx.triggered_id['table']}"

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
        def update_cell(_, pathname):
            data = ctx.inputs["banana--table.cellValueChanged"]
            obj = UpdateCellCallback(data, pathname)
            obj.exec()

        @self.callback(
            Output("banana--modal", "opened", allow_duplicate=True),
            Output("banana--modal-form", "children"),
            Input("banana--add-button", "n_clicks"),
            State("banana--location", "pathname"),
            prevent_initial_call=True,
        )
        def open_modal(_, pathname: str):
            obj = LoadForm(pathname)
            return True, obj.form

        @self.callback(
            Output("banana--modal", "opened"),
            Input("banana--insert-button", "n_clicks"),
            State("banana--location", "pathname"),
            State({"component": "form-item", "column": ALL}, "value"),
            prevent_initial_call=True,
        )
        def add_row(_click, pathname, _fields):
            obj = InsertRow(pathname, ctx.states_list[1])
            obj.insert()
            return False
