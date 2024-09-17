import json
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator, PositiveInt

from .utils import config


class BananaOrderBy(BaseModel):
    column: str
    desc: bool = False


class BananaForeignKey(BaseModel):
    table_name: str
    column_name: str
    column_display: Optional[str] = None
    schema_name: Optional[str] = None
    order_by: Optional[list[BananaOrderBy]] = None

    @model_validator(mode="after")
    def validate_model(self):
        if self.column_display is None:
            self.column_display = self.column_name
        return self


class BananaPrimaryKey(BaseModel):
    name: str
    display_name: Optional[str] = None
    columnDef: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_model(self):
        if self.display_name is None:
            self.display_name = self.name
        return self


class BananaColumn(BaseModel):
    name: str
    display_name: Optional[str] = None
    foreign_key: Optional[BananaForeignKey] = None
    columnDef: dict[str, Any] = Field(default_factory=dict)

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
    order_by: Optional[list[BananaOrderBy]] = None
    limit: Optional[PositiveInt] = None
    defaultColDef: dict[str, Any] = Field(default_factory=dict)
    gridOptions: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_model(self):
        if self.display_name is None:
            self.display_name = self.name

        self.defaultColDef = {
            **config.defaultColDef,
            **self.defaultColDef,
        }
        self.gridOptions = {
            **config.defaultGridOptions,
            **self.gridOptions,
        }

        return self


class BananaGroup(BaseModel):
    tables: list[BananaTable]
    group_name: Optional[str] = None
    display_order: Optional[int] = None


def get_table_model(group_name: str, table_name: str) -> BananaTable:
    json_dir = config.dataPath.joinpath("models.json")
    with open(json_dir, "r") as f:
        models = json.load(f)
        table = BananaTable(**models[group_name]["tables"][table_name])
    return table
