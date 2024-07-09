from typing import Optional

from pydantic import BaseModel, model_validator, PositiveInt
import yaml

from .errors import (
    MultipleBananaTablesWithSameName,
    NoBananaTableFound,
    NoBananaTableSelected,
)


def read_yaml(file) -> dict:
    try:
        with open(file, "r", encoding="utf8") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        raise Exception(f"Config file `{file}` not found.")
    except yaml.YAMLError as exc:
        raise Exception(f"Error parsing YAML config file: {exc}")


class Config(BaseModel):
    connection_string: str
    port: PositiveInt = 4000
    tables_file: str = "tables.yaml"
    title: str = "Banana Database Manager"


class BananaForeignKey(BaseModel):
    table_name: str
    column_name: str
    column_display: Optional[str] = None
    schema_name: Optional[str] = None

    @model_validator(mode="after")
    def validate_model(self):
        if self.column_display is None:
            self.column_display = self.column_name
        return self


class BananaPrimaryKey(BaseModel):
    name: str
    display_name: Optional[str] = None

    @model_validator(mode="after")
    def validate_model(self):
        if self.display_name is None:
            self.display_name = self.name
        return self


class BananaColumn(BaseModel):
    name: str
    display_name: Optional[str] = None
    foreign_key: Optional[BananaForeignKey] = None

    @model_validator(mode="after")
    def validate_model(self):
        if self.display_name is None:
            self.display_name = self.name
        return self


class BananaTable(BaseModel):
    name: str
    primary_key: BananaPrimaryKey
    display_name: Optional[str] = None
    schema_name: Optional[str] = None
    columns: Optional[list[BananaColumn]] = None

    @model_validator(mode="after")
    def validate_model(self):
        if self.display_name is None:
            self.display_name = self.name
        return self


class BananaTables(BaseModel):
    tables: list[BananaTable]

    def __getitem__(self, table_name: str) -> BananaTable:
        tbs = [table for table in self.tables if table.name == table_name]

        if not table_name:
            raise NoBananaTableSelected()
        if len(tbs) == 0:
            raise NoBananaTableFound(table_name)
        elif len(tbs) > 1:
            raise MultipleBananaTablesWithSameName(table_name)

        return tbs[0]
