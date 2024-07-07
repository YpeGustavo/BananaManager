from importlib import resources

from dash import Dash, Input, Output, State, html, ALL, ctx
from pydantic import BaseModel, field_validator
from sqlalchemy import MetaData, Table, create_engine, select, func

from .callbacks import LoadTableCallback, UpdateCellCallback
from .layout import layout
from .models import BananaTables, Config
from .utils import read_sql, read_yaml


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

        self.__check_foreign_key_uniqueness()

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
            obj = LoadTableCallback(pathname, self.config)
            return obj.column_defs, obj.row_data, obj.row_id, obj.table_title

        @app.callback(
            Input("banana--table", "cellValueChanged"),
            State("banana--location", "pathname"),
        )
        def update_cell(data, pathname):
            obj = UpdateCellCallback(data, pathname, self.config)
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

        app.run(port=self.config.port)

    def __check_foreign_key_uniqueness(self) -> bool:
        metadata = MetaData()
        data = read_yaml(self.config.tables_file)
        tables = BananaTables(**data)
        engine = create_engine(self.config.connection_string)

        for table in tables.tables:
            for column in table.columns:
                if column.foreign_key is not None:
                    foreign_table = Table(
                        column.foreign_key.table_name,
                        metadata,
                        schema=column.foreign_key.schema_name,
                        autoload_with=engine,
                    )

                    stmt = select(
                        (
                            func.count("*")
                            == func.count(
                                func.distinct(
                                    foreign_table.c[column.foreign_key.column_name]
                                )
                            )
                        )
                        & (
                            func.count("*")
                            == func.count(
                                func.distinct(
                                    foreign_table.c[column.foreign_key.column_display]
                                )
                            )
                        )
                    )

                    rows = read_sql(stmt, engine)
                    if not rows[0][0]:
                        raise Exception(
                            f"Foreign key in the table `{table.name}` values is not unique."
                        )
