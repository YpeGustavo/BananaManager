from typing import Optional

from pydantic import BaseModel, model_validator

from .errors import (
    MultipleBananaTablesWithSameName,
    NoBananaTableFound,
    NoBananaTableSelected,
)
from .utils import read_yaml, config


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


def get_table_model(table_name: str) -> BananaTable:
    data = read_yaml(config.tables_file)
    tables = BananaTables(**data)
    return tables[table_name]
