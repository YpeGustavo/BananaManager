from typing import Optional, Self

from pydantic import BaseModel, model_validator
import yaml

from .config import CONFIG


class BananaPrimaryKey(BaseModel):
    name: str
    pretty_name: Optional[str] = None

    @model_validator(mode="after")
    def validate_model(self) -> Self:
        if self.pretty_name is None:
            self.pretty_name = self.name
        return self


class BananaColumn(BaseModel):
    name: str
    pretty_name: Optional[str] = None
    datatype: Optional[str] = None

    @model_validator(mode="after")
    def validate_model(self) -> Self:
        if self.pretty_name is None:
            self.pretty_name = self.name
        return self


class BananaTable(BaseModel):
    name: str
    primary_key: BananaPrimaryKey
    pretty_name: Optional[str] = None
    columns: Optional[list[BananaColumn]] = None

    @model_validator(mode="after")
    def validate_model(self) -> Self:
        if self.pretty_name is None:
            self.pretty_name = self.name
        return self


class BananaTables(BaseModel):
    tables: list[BananaTable]

    def __getitem__(self, table_name: str) -> BananaTable:
        tbs = [table for table in self.tables if table.name == table_name]
        assert len(tbs) == 1, "Check the name of the table"
        return tbs[0]


try:
    with open(CONFIG.tables_file, "r") as file:
        data = yaml.safe_load(file)
        TABLES = BananaTables(**data)
except FileNotFoundError:
    raise Exception(f"Config file {CONFIG.tables_file} not found.")
except yaml.YAMLError as exc:
    raise Exception(f"Error parsing YAML config file: {exc}")
