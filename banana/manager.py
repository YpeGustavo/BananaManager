from dash import Dash, Input, Output, State, html
from pydantic import BaseModel, field_validator
from sqlalchemy import MetaData, Table, create_engine, select, update

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
        app = Dash(assets_folder=r"banana\assets")
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
                html.A(table.pretty_name, href=f"/{table.name}", className="menu-item")
                for table in tables.tables
            ]

        @app.callback(
            Output("banana--table", "columnDefs"),
            Output("banana--table", "rowData"),
            Output("banana--table", "getRowId"),
            Input("banana--location", "pathname"),
            prevent_initial_call=True,
        )
        def load_table(table_name: str):
            # Get table model
            data = read_yaml(self.config.tables_file)
            tables = BananaTables(**data)
            table_name = table_name[1:]
            table_model = tables[table_name]

            # Get table schema
            engine = create_engine(self.config.connection_string)
            table_data = Table(table_name, metadata, autoload_with=engine)

            # Create select statement
            query = select(
                getattr(table_data.c, table_model.primary_key.name),
                *[getattr(table_data.c, col.name) for col in table_model.columns],
            ).select_from(table_data)

            # Fetch results
            with engine.connect() as conn:
                result = conn.execute(query)
                rows = result.fetchall()

            # Define header
            id_col = [
                {
                    "headerName": table_model.primary_key.pretty_name,
                    "valueGetter": {
                        "function": f"params.node.{table_model.primary_key.name}"
                    },
                    "editable": False,
                },
            ]
            values_cols = [
                {"headerName": col.pretty_name, "field": col.name}
                for col in table_model.columns
            ]
            column_defs = id_col + values_cols

            # Define Rows
            cols = [table_model.primary_key.name] + [
                col.name for col in table_model.columns
            ]
            row_data = []
            for row in rows:
                row_data.append({col: value for col, value in zip(cols, row)})

            return column_defs, row_data, f"params.data.{table_model.primary_key.name}"

        @app.callback(
            Input("banana--table", "cellValueChanged"),
            State("banana--location", "pathname"),
        )
        def update_cell(data, table_name):
            # Validate data
            assert len(data) == 1, data
            data = data[0]

            # Find the table model
            data = read_yaml(self.config.tables_file)
            tables = BananaTables(**data)
            table_name = table_name[1:]
            table_model = tables[table_name]

            # Update the database
            engine = create_engine(self.config.connection_string)
            table_data = Table(table_name, metadata, autoload_with=engine)

            with engine.connect() as conn:
                stmt = (
                    update(table_data)
                    .where(
                        getattr(table_data.c, table_model.primary_key.name)
                        == data["rowId"]
                    )
                    .values({data["colId"]: data["value"]})
                )
                conn.execute(stmt)
                conn.commit()

        app.run(port=self.config.port, debug=self.config.debug)
