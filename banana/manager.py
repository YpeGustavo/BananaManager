from importlib import resources

from dash import Dash, Input, Output, State, html, ALL, ctx

from .queries import LoadTableCallback, UpdateCellCallback, check_foreign_key_uniqueness
from .layout import layout
from .models import BananaTables
from .utils import read_yaml, config, server


class Banana(Dash):
    def __init__(self):
        with server.app_context():
            check_foreign_key_uniqueness()

        super().__init__(
            server=server,
            assets_folder=resources.files("banana") / "assets",
            title=config.title,
        )
        self.layout = layout

        @self.callback(
            Output("banana--menu", "children"),
            Input("banana--menu", "style"),
        )
        def load_menu(_):
            data = read_yaml(config.tables_file)
            tables = BananaTables(**data)

            return [
                html.A(
                    table.display_name,
                    href=f"/{table.name}",
                    className="menu-item",
                    id={"type": "menu-item", "id": table.name},
                )
                for table in tables.tables
            ]

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

        @self.callback(
            Output({"type": "menu-item", "id": ALL}, "className"),
            Input("banana--location", "pathname"),
        )
        def change_menu_item_style_on_selected(table_name):
            return [
                (
                    "menu-item selected"
                    if item["id"]["id"] == table_name[1:]
                    else "menu-item"
                )
                for item in ctx.outputs_list
            ]
