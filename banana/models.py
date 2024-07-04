from typing import Optional, Self

from pydantic import BaseModel, model_validator, PositiveInt
import yaml


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
    debug: bool = False
    port: PositiveInt = 4000
    tables_file: str = "tables.yaml"


class BananaForeignKey(BaseModel):
    table_name: str
    column_name: str
    column_display: Optional[str] = None
    schema_name: Optional[str] = None

    @model_validator(mode="after")
    def validate_model(self) -> Self:
        if self.column_display is None:
            self.column_display = self.column_name
        return self


class BananaPrimaryKey(BaseModel):
    name: str
    display_name: Optional[str] = None

    @model_validator(mode="after")
    def validate_model(self) -> Self:
        if self.display_name is None:
            self.display_name = self.name
        return self


class BananaColumn(BaseModel):
    name: str
    display_name: Optional[str] = None
    foreign_key: Optional[BananaForeignKey] = None

    @model_validator(mode="after")
    def validate_model(self) -> Self:
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
    def validate_model(self) -> Self:
        if self.display_name is None:
            self.display_name = self.name
        return self


class BananaTables(BaseModel):
    tables: list[BananaTable]

    def __getitem__(self, table_name: str) -> BananaTable:
        tbs = [table for table in self.tables if table.name == table_name]
        assert len(tbs) == 1, "Check the name of the table"
        return tbs[0]
