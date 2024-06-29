from importlib import resources

from dash import Dash, Input, Output, State, html, ALL, ctx
from pydantic import BaseModel, field_validator
from sqlalchemy import MetaData

from .callbacks.load_table import LoadTableCallback
from .callbacks.update_cell import UpdateCellCallback
from .layout import layout
from .models import Config, read_yaml, BananaTables


def DefaultConfig() -> Config:
    data = read_yaml("config.yaml")
    return Config(**data)


class Banana(BaseModel):
    config: Config = DefaultConfig()

    @field_validator("config", mode="before")
    @classmethod
    def load_config(cls, config):
        if not isinstance(config, Config):
            config = read_yaml(config)
        return config

    def run(self):
        app = Dash(assets_folder=resources.files("banana") / "assets")
        app.layout = layout

        metadata = MetaData()

        @app.callback(
            Output("banana--menu", "children"),
            Input("banana--menu", "style"),
        )
        def load_menu(_):
            data = read_yaml(self.config.tables_file)
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

        @app.callback(
            Output("banana--table", "columnDefs"),
            Output("banana--table", "rowData"),
            Output("banana--table", "getRowId"),
            Output("banana--table-title", "children"),
            Input("banana--location", "pathname"),
            prevent_initial_call=True,
        )
        def load_table(pathname: str):
            obj = LoadTableCallback(pathname, self.config, metadata)
            return obj.column_defs, obj.row_data, obj.row_id, obj.table_title

        @app.callback(
            Input("banana--table", "cellValueChanged"),
            State("banana--location", "pathname"),
        )
        def update_cell(data, pathname):
            obj = UpdateCellCallback(data, pathname, self.config, metadata)
            obj.exec()

        @app.callback(
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

        app.run(port=self.config.port, debug=self.config.debug)
