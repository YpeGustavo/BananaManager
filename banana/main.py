from importlib import resources

from dash import (
    Dash,
    Input,
    Output,
    State,
    _dash_renderer,
    ctx,
    no_update,
    ALL,
)
from dash.exceptions import PreventUpdate
from dash_mantine_components import styles

from .callbacks import (
    InsertRowCallback,
    OpenInsertModalCallback,
    OpenHistoryModalCallback,
    LoadSideMenuCallback,
    LoadMainTableCallback,
    UpdateCellCallback,
)
from .layout import Layout
from .core.config import config, server
from .core.tables import tables
from .core.utils import raise_error


_dash_renderer._set_react_version("18.2.0")


class Banana(Dash):
    def __init__(self):
        tables.refresh_models()
        super().__init__(
            server=server,
            assets_folder=resources.files("banana") / "assets",
            title=config.title,
            external_stylesheets=[styles.NOTIFICATIONS],
            suppress_callback_exceptions=True,
        )
        self.layout = Layout()

        @self.callback(
            Output("banana--location", "pathname"),
            Input({"component": "menu-item", "group": ALL, "table": ALL}, "n_clicks"),
            prevent_initial_call=True,
        )
        def change_path_name(_):
            if len(ctx.triggered) != 1:
                raise PreventUpdate
            return f"/{ctx.triggered_id['group']}/{ctx.triggered_id['table']}"

        @self.callback(
            Output("banana--insert-modal", "opened"),
            Output("banana--refresh-table", "data"),
            Input("banana--insert-confirm", "n_clicks"),
            Input("banana--insert-cancel", "n_clicks"),
            State("banana--location", "pathname"),
            State({"component": "form-item", "column": ALL}, "value"),
            prevent_initial_call=True,
        )
        def insert_row(_confirm, _cancel, pathname, _fields):
            if ctx.triggered_id == "banana--insert-cancel":
                return False, no_update
            try:
                obj = InsertRowCallback(pathname, ctx.states_list[1])
                return obj.exec()
            except Exception as err:
                raise_error("Error inserting new row", str(err))
                return no_update, no_update

        @self.callback(
            Output("banana--table", "columnDefs"),
            Output("banana--table", "rowData"),
            Output("banana--table", "getRowId"),
            Output("banana--table", "defaultColDef"),
            Output("banana--table", "dashGridOptions"),
            Output("banana--table-title", "children"),
            Input("banana--refresh-table", "data"),
            State("banana--location", "pathname"),
        )
        def load_main_table(_, pathname: str):
            try:
                obj = LoadMainTableCallback(pathname)
                return (
                    obj.columnDefs,
                    obj.rowData,
                    obj.rowId,
                    obj.defaultColDef,
                    obj.gridOptions,
                    obj.tableTitle,
                )
            except Exception as err:
                raise_error("Error loading selected table", str(err))
                return no_update, no_update, no_update, no_update, no_update, no_update

        @self.callback(
            Output("banana--menu", "children"),
            Input("banana--refresh-button", "n_clicks"),
            State("banana--location", "pathname"),
        )
        def load_side_menu(_, pathname: str):
            if ctx.triggered_id == "banana--refresh-button":
                try:
                    tables.refresh_models()
                except Exception as e:
                    raise_error("Error refreshing table configuration", str(e))
                    return no_update
            try:
                obj = LoadSideMenuCallback(pathname)
                return obj.menu
            except Exception as err:
                raise_error("Error loading side menu", str(err))
                return no_update

        @self.callback(
            Output("banana--history-modal", "opened"),
            Output("banana--history-modal", "children"),
            Input("banana--history-button", "n_clicks"),
            State("banana--location", "pathname"),
            prevent_initial_call=True,
        )
        def open_history_modal(_, pathname: str):
            try:
                obj = OpenHistoryModalCallback(pathname)
                return True, obj.rows
            except Exception as err:
                raise_error("Error loading history data", str(err))
                return no_update, no_update

        @self.callback(
            Output("banana--insert-modal", "opened", allow_duplicate=True),
            Output("banana--insert-form", "children"),
            Input("banana--insert-button", "n_clicks"),
            State("banana--location", "pathname"),
            prevent_initial_call=True,
        )
        def open_insert_modal(_, pathname: str):
            try:
                obj = OpenInsertModalCallback(pathname)
                return True, obj.form
            except Exception as err:
                raise_error("Error loading insertion form", str(err))
                return no_update, no_update

        @self.callback(
            Input("banana--table", "cellValueChanged"),
            State("banana--location", "pathname"),
        )
        def update_cell(_, pathname):
            try:
                data = ctx.inputs["banana--table.cellValueChanged"]
                obj = UpdateCellCallback(data, pathname)
                obj.exec()
            except Exception as err:
                raise_error("Error updating value", str(err))
